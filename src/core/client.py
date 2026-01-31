import asyncio
from typing import Any

import httpx

from src.core.config import AppConfig


class ChatClient:
    def __init__(self, config: AppConfig) -> None:
        self._config = config

    @property
    def concurrency(self) -> int:
        return self._config.concurrency

    async def send(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._config.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._config.model,
            "messages": messages,
        }

        url = self._config.base_url.rstrip("/") + self._config.endpoint

        async with httpx.AsyncClient(timeout=self._config.timeout_seconds) as client:
            return await self._request_with_retries(client, url, payload, headers)

    async def _request_with_retries(
        self,
        client: httpx.AsyncClient,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        last_exc: Exception | None = None
        for attempt in range(1, self._config.max_retries + 1):
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except Exception as exc:
                last_exc = exc
                if attempt >= self._config.max_retries:
                    break
                await asyncio.sleep(min(2 ** attempt, 8))
        raise RuntimeError(f"Request failed after {self._config.max_retries} attempts") from last_exc
