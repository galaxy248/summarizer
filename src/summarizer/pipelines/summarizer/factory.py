from pathlib import Path
from typing import Optional, Union

from .base import Summarizer
from summarizer.pipelines.summarizer.client import ClientFactory
from summarizer.pipelines.summarizer.config import SummarizerConfig
from summarizer.pipelines.summarizer.config import SummarizerClientConfig


class SummarizerFactory:
    @classmethod
    def create(
        cls,
        config: SummarizerConfig,
        client_config: Optional[SummarizerClientConfig] = None,
    ) -> Summarizer:

        client = ClientFactory.create(client_config or SummarizerClientConfig())

        return Summarizer(
            client,
            config,
        )
