from pathlib import Path
from typing import Optional, Union

from openai import OpenAI

from summarizer.pipelines.summarizer.config import SummarizerConfig


class Summarizer:
    def __init__(self, client: OpenAI, config: SummarizerConfig):
        self.client = client
        self.config = config

    def run(self, text_content: str) -> str:
        response = self.client.chat.completions.create(
            messages= [
                {
                    "role": "system", "content": self.config.prompt
                },
                {
                    "role": "user", "content": text_content
                }
            ],
            model=self.config.model,
            temperature=self.config.temperature,
            top_p=0.1
        )

        return response.choices[0].message.content
