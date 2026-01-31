# WuSi - Legal JSON Batch

输入一条法条（或法条片段）→ 输出严格 JSON。用于批量调用 AI API 并保存 JSONL 结果。

## Requirements
- Python 3.10+

## Install
```
pip install -r requirements.txt
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
python -m src.main ^
  --prompt-file .\examples\prompt\system_legal_json.txt ^
  --input-file .\examples\input\inputs.jsonl ^
  --output-file .\examples\output\outputs.jsonl ^
  --model <your-model-name>
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

## Output
Writes JSONL with fields:
- `id`
- `input`
- `response_text`
- `raw_response`
