# WuSi - Legal JSON Batch

输入一条法条（或法条片段）→ 输出严格 JSON。用于批量调用 AI API 并保存 JSONL 结果。

## Requirements
- Python 3.10+

## Install (uv)
```
uv sync
```

## Prepare files
- Prompt file: System Prompt（强制只输出 JSON）
- Input file:
  - `.txt`: 每行一条“法条文本或法条片段”
  - `.jsonl`: 每行一个 JSON 对象：
    - `id`（可选）
    - `input`（法条文本或法条片段）
    - `messages`（可选：已拼好的多轮对话）

## Run
```
uv run python -m src.main
```

Optional overrides:
```
uv run python -m src.main ^
  --prompt-file .\\examples\\prompt\\system_legal_json.txt ^
  --input-file .\\examples\\input\\inputs.jsonl ^
  --output-file .\\examples\\output\\outputs.jsonl ^
  --model Pro/deepseek-ai/DeepSeek-V3.2 ^
  --max-tokens 1200 ^
  --temperature 0.2 ^
  --top-p 0.9
```

Readable output:
- 仍然输出 JSONL：`examples/output/outputs.jsonl`
- 额外输出美化版 JSON：`examples/output/outputs_pretty.json`

Progress logs (stderr):
- 默认会输出每条任务的 start/done/error，以及总体进度
- 如需静默：加 `--quiet`

## Web UI (单条输入 + 进度条)
启动服务：
```
uv run uvicorn src.server:app --host 0.0.0.0 --port 8000
```

打开浏览器访问：
```
http://localhost:8000
```

## Example files (Legal JSON)
- System prompt: `examples/prompt/system_legal_json.txt`
- User prompt template: `examples/prompt/user_legal_json.txt`
- Schema draft (JSON): `examples/prompt/schema_legal_json.json`
- Inputs: `examples/input/inputs.txt` or `examples/input/inputs.jsonl`
- Example input (完整 user prompt): `examples/input/legal_user_prompt.txt`
- Outputs: `examples/output/outputs.jsonl`
- Example output (单条): `examples/output/legal_output.json`

Environment variables:
- `SILICONFLOW_API_KEY` (required unless `--api-key` provided)
- `SILICONFLOW_BASE_URL` (optional, default `https://api.siliconflow.cn`)
- `SILICONFLOW_MODEL` (optional, default `Pro/deepseek-ai/DeepSeek-V3.2`)

More detailed output:
- 默认已提高 `max_tokens=1200`，并设置 `temperature=0.2`、`top_p=0.9`
- 需要更长输出可继续调大 `--max-tokens`

## Output
Writes JSONL with fields:
- `id`
- `input`
- `response_text`
- `raw_response`
