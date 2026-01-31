import argparse
import asyncio
import os
import sys

from src.core.client import ChatClient
from src.core.config import AppConfig
from src.core.io import load_inputs, load_prompt, write_outputs
from src.core.runner import run_batch


def build_config(args: argparse.Namespace) -> AppConfig:
    api_key = args.api_key or os.getenv("SILICONFLOW_API_KEY")
    if not api_key:
        raise ValueError("Missing API key. Set SILICONFLOW_API_KEY or use --api-key.")

    base_url = (
        args.base_url
        or os.getenv("SILICONFLOW_BASE_URL")
        or "https://api.siliconflow.cn"
    )

    model = args.model or os.getenv("SILICONFLOW_MODEL")
    if not model:
        raise ValueError("Missing model. Set SILICONFLOW_MODEL or use --model.")

    return AppConfig(
        api_key=api_key,
        base_url=base_url,
        endpoint=args.endpoint,
        model=model,
        concurrency=args.concurrency,
        timeout_seconds=args.timeout,
        max_retries=args.max_retries,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch chat completions client.")
    parser.add_argument("--prompt-file", required=True, help="System prompt file path.")
    parser.add_argument("--input-file", required=True, help="Input file path.")
    parser.add_argument("--output-file", required=True, help="Output JSONL file path.")
    parser.add_argument("--model", help="Model name.")
    parser.add_argument("--api-key", help="API key override.")
    parser.add_argument("--base-url", help="Base URL override.")
    parser.add_argument(
        "--endpoint",
        default="/v1/chat/completions",
        help="Chat completions endpoint path.",
    )
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrency.")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout.")
    parser.add_argument("--max-retries", type=int, default=3, help="Max retries.")
    return parser.parse_args(argv)


async def main_async(argv: list[str]) -> int:
    args = parse_args(argv)
    config = build_config(args)

    prompt = load_prompt(args.prompt_file)
    inputs = load_inputs(args.input_file)

    client = ChatClient(config)
    results = await run_batch(client, prompt, inputs)
    write_outputs(args.output_file, results)
    return 0


def main() -> int:
    try:
        return asyncio.run(main_async(sys.argv[1:]))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
