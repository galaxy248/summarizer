import os
from typing import Optional
from dataclasses import dataclass


ALLOWED_MODELS = [
    "openai/gpt-4.1-mini",
]

ALLOWED_PROMPT_MODES = [
    "priority",
    "thematic",
]

@dataclass
class SummarizerConfig:
    model: Optional[str] = None
    prompt: Optional[str] = None
    temperature: Optional[float] = 0.0

    def __post_init__(self):
        if self.prompt is None:
            raise ValueError("Prompt must be provided for summarization.")

        if self.model not in ALLOWED_MODELS:
            raise ValueError(f"Unknown Model - Allowed Models: {', '.join(ALLOWED_MODELS)}")


@dataclass
class SummarizerClientConfig:
    api_key: Optional[str] = None
    base_url: str = "https://models.github.ai/inference"

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv("MODEL_TOKEN")
            if self.api_key is None:
                raise ValueError("API key must be provided either as an argument or through the MODEL_TOKEN environment variable.")
