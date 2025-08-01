from typing import Optional

from openai import OpenAI

from summarizer.pipelines.summarizer.config import SummarizerClientConfig


class ClientFactory:
    @classmethod
    def create(
        cls,
        config: Optional[SummarizerClientConfig] = None,
    ) -> OpenAI:
        if not config:
            config = SummarizerClientConfig()
            
        client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

        return client
