import asyncio
import json
import os
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from src.core.client import ChatClient
from src.core.config import AppConfig


@dataclass
class TaskState:
    id: str
    status: str = "pending"  # pending | running | done | error
    progress: int = 0
    law_text: str = ""
    result: dict[str, Any] | None = None
    error: str | None = None
    started_at: float | None = None
    ended_at: float | None = None
    logs: list[str] = field(default_factory=list)


app = FastAPI()
tasks: dict[str, TaskState] = {}
semaphore: asyncio.Semaphore | None = None


def _build_config() -> AppConfig:
    api_key = os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise RuntimeError("Missing SILICONFLOW_API_KEY")
    base_url = os.getenv("SILICONFLOW_BASE_URL") or "https://api.siliconflow.cn"
    model = os.getenv("SILICONFLOW_MODEL") or "Pro/deepseek-ai/DeepSeek-V3.2"

    return AppConfig(
        api_key=api_key,
        base_url=base_url,
        endpoint="/v1/chat/completions",
        model=model,
        concurrency=int(os.getenv("SILICONFLOW_CONCURRENCY") or "5"),
        timeout_seconds=int(os.getenv("SILICONFLOW_TIMEOUT") or "60"),
        max_retries=int(os.getenv("SILICONFLOW_MAX_RETRIES") or "3"),
        verbose=False,
        progress_every=1,
        max_tokens=int(os.getenv("SILICONFLOW_MAX_TOKENS") or "1200"),
        temperature=float(os.getenv("SILICONFLOW_TEMPERATURE") or "0.2"),
        top_p=float(os.getenv("SILICONFLOW_TOP_P") or "0.9"),
    )


def _load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8-sig").strip()


def _build_user_prompt(law_text: str) -> str:
    template_path = Path("examples/prompt/user_legal_json.txt")
    template = _load_text(template_path)
    if template:
        return (
            template.replace("{LAW_TEXT}", law_text)
            .replace("{LAW_NAME}", "")
            .replace("{ARTICLE_LOCATOR}", "")
            .replace("{SCENARIO}", "")
            .replace("{ALLOW_ONLINE_SEARCH true/false}", "false")
            .replace(
                "{SOURCE_WHITELIST e.g. 最高法官网/裁判文书网/北大法宝/中国法院网}",
                "",
            )
        )
    return law_text


async def _run_task(task: TaskState) -> None:
    if semaphore is None:
        raise RuntimeError("Server not initialized")
    async with semaphore:
        task.status = "running"
        task.progress = 10
        task.logs.append("start")

        config = _build_config()
        client = ChatClient(config)
        system_prompt = _load_text(Path("examples/prompt/system_legal_json.txt"))
        if not system_prompt:
            raise RuntimeError("Missing system prompt file")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": _build_user_prompt(task.law_text)},
        ]

        try:
            response = await client.send(messages)
            task.progress = 80
            response_text = None
            try:
                choices = response.get("choices") or []
                if choices:
                    response_text = choices[0].get("message", {}).get("content")
            except Exception:
                response_text = None

            parsed: dict[str, Any] | None = None
            if response_text:
                try:
                    parsed = json.loads(response_text)
                except json.JSONDecodeError:
                    parsed = None

            task.result = {
                "response_text": response_text,
                "parsed_json": parsed,
                "raw_response": response,
            }
            task.status = "done"
            task.progress = 100
            task.logs.append("done")
        except Exception as exc:
            task.status = "error"
            task.progress = 100
            task.error = str(exc)
            task.logs.append(f"error: {exc}")


@app.on_event("startup")
async def _startup() -> None:
    global semaphore
    config = _build_config()
    semaphore = asyncio.Semaphore(config.concurrency)


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    html_path = Path("src/web/index.html")
    if html_path.exists():
        return html_path.read_text(encoding="utf-8-sig")
    return "<h1>Missing src/web/index.html</h1>"


@app.post("/api/tasks")
async def create_task(payload: dict[str, Any]) -> dict[str, Any]:
    law_text = (payload.get("law_text") or "").strip()
    if not law_text:
        raise HTTPException(status_code=400, detail="law_text is required")

    task_id = str(uuid.uuid4())
    task = TaskState(id=task_id, law_text=law_text)
    tasks[task_id] = task
    asyncio.create_task(_run_task(task))
    return {"task_id": task_id}


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str) -> dict[str, Any]:
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="task not found")
    return {
        "id": task.id,
        "status": task.status,
        "progress": task.progress,
        "error": task.error,
        "result": task.result,
        "logs": task.logs,
    }
