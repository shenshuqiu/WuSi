# WuSi - Batch Chat Completions

Batch-send prompts to an AI chat completion API and save JSONL results.

## Requirements
- Python 3.10+

## Install
```
pip install -r requirements.txt
```

## Prepare files
- Prompt file: plain text (system prompt)
- Input file:
  - `.txt`: one user message per line
  - `.jsonl`: one JSON object per line with keys:
    - `id` (optional)
    - `input` (user content)
    - `messages` (optional array of role/content objects)

Example `inputs.jsonl`:
```
{"id": "a1", "input": "请用JSON返回标题和摘要"}
{"id": "a2", "messages": [{"role":"user","content":"按要求输出JSON"}]}
```

## Run
```
python -m src.main ^
  --prompt-file .\prompt.txt ^
  --input-file .\inputs.jsonl ^
  --output-file .\outputs.jsonl ^
  --model <your-model-name>
```

Environment variables:
- `SILICONFLOW_API_KEY` (required unless `--api-key` provided)
- `SILICONFLOW_BASE_URL` (optional, default `https://api.siliconflow.cn`)

## Output
Writes JSONL with fields:
- `id`
- `input`
- `response_text`
- `raw_response`
