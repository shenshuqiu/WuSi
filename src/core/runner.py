import asyncio
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
) -> OutputItem:
    async with semaphore:
        messages = _build_messages(prompt, item)
        response = await client.send(messages)
        response_text = _extract_text(response)
        return OutputItem(
            id=item.id,
            input_text=item.text,
            response_text=response_text,
            raw_response=response,
        )


async def run_batch(
    client: ChatClient,
    prompt: str,
    inputs: list[InputItem],
) -> list[OutputItem]:
    semaphore = asyncio.Semaphore(client.concurrency)
    tasks = [
        _process_one(client, prompt, item, semaphore)
        for item in inputs
    ]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return list(results)
