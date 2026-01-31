import json
from pathlib import Path
from typing import Any

from src.core.models import InputItem, OutputItem


def load_prompt(path: str) -> str:
    text = Path(path).read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("Prompt file is empty.")
    return text


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_no}") from exc
    return items


def load_inputs(path: str) -> list[InputItem]:
    input_path = Path(path)
    if not input_path.exists():
        raise FileNotFoundError(str(input_path))

    if input_path.suffix.lower() == ".jsonl":
        raw_items = _load_jsonl(input_path)
        items: list[InputItem] = []
        for index, item in enumerate(raw_items, start=1):
            item_id = str(item.get("id") or index)
            text = item.get("input")
            messages = item.get("messages")
            if text is None and messages is None:
                raise ValueError(f"Item {item_id} missing 'input' or 'messages'.")
            items.append(InputItem(id=item_id, text=text, messages=messages))
        return items

    lines = input_path.read_text(encoding="utf-8-sig").splitlines()
    items = []
    for index, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        items.append(InputItem(id=str(index), text=line, messages=None))
    return items


def write_outputs(path: str, outputs: list[OutputItem]) -> None:
    output_path = Path(path)
    with output_path.open("w", encoding="utf-8") as handle:
        for item in outputs:
            payload = {
                "id": item.id,
                "input": item.input_text,
                "response_text": item.response_text,
                "raw_response": item.raw_response,
            }
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
