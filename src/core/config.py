from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    api_key: str
    base_url: str
    endpoint: str
    model: str
    concurrency: int
    timeout_seconds: int
    max_retries: int
    verbose: bool
    progress_every: int
    max_tokens: int
    temperature: float
    top_p: float
