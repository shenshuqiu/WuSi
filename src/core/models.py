from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class InputItem:
    id: str
    text: str | None
    messages: list[dict[str, Any]] | None


@dataclass(frozen=True)
class OutputItem:
    id: str
    input_text: str | None
    response_text: str | None
    raw_response: dict[str, Any] | None
