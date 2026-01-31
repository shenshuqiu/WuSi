import asyncio
import sys
import time
from typing import Any

from src.core.client import ChatClient
from src.core.models import InputItem, OutputItem


def _build_messages(prompt: str, item: InputItem) -> list[dict[str, Any]]:
    if item.messages is not None:
        if prompt:
            return [{"role": "system", "content": prompt}, *item.messages]
        return item.messages
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": item.text or ""},
    ]


def _extract_text(response: dict[str, Any]) -> str | None:
    try:
        choices = response.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message") or {}
        return message.get("content")
    except Exception:
        return None


async def _process_one(
    client: ChatClient,
    prompt: str,
    item: InputItem,
    semaphore: asyncio.Semaphore,
    log_fn,
) -> OutputItem:
    async with semaphore:
        messages = _build_messages(prompt, item)
        started = time.perf_counter()
        await log_fn(f"start id={item.id}")
        try:
            response = await client.send(messages)
            response_text = _extract_text(response)
            elapsed = time.perf_counter() - started
            await log_fn(f"done  id={item.id} elapsed={elapsed:.2f}s")
            return OutputItem(
                id=item.id,
                input_text=item.text,
                response_text=response_text,
                raw_response=response,
            )
        except Exception as exc:
            elapsed = time.perf_counter() - started
            await log_fn(f"error id={item.id} elapsed={elapsed:.2f}s err={exc}")
            return OutputItem(
                id=item.id,
                input_text=item.text,
                response_text=None,
                raw_response=None,
                error=str(exc),
            )


async def run_batch(
    client: ChatClient,
    prompt: str,
    inputs: list[InputItem],
    *,
    verbose: bool,
    progress_every: int,
) -> list[OutputItem]:
    semaphore = asyncio.Semaphore(client.concurrency)
    lock = asyncio.Lock()
    total = len(inputs)
    completed = 0
    started = time.perf_counter()

    async def log_fn(message: str) -> None:
        if not verbose:
            return
        async with lock:
            print(message, file=sys.stderr, flush=True)

    async def report_progress() -> None:
        nonlocal completed
        if not verbose:
            return
        if progress_every <= 0:
            return
        if completed % progress_every != 0:
            return
        elapsed = time.perf_counter() - started
        await log_fn(f"progress {completed}/{total} elapsed={elapsed:.2f}s")

    async def wrapped(item: InputItem) -> OutputItem:
        nonlocal completed
        result = await _process_one(client, prompt, item, semaphore, log_fn)
        async with lock:
            completed += 1
        await report_progress()
        return result

    await log_fn(f"batch start total={total} concurrency={client.concurrency}")
    tasks = [wrapped(item) for item in inputs]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    await log_fn("batch done")
    return list(results)
