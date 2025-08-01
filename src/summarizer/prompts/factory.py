import os
import logging
from typing import Literal

from .base import THEMATIC, PRIORITY

from summarizer.utils import get_logger


class PromptFactory:
    @classmethod
    def create(cls, prompt: Literal["thematic", "priority"]) -> str:
        prompt = prompt.lower()
        
        if prompt == "thematic":
            return THEMATIC
        elif prompt == "priority":
            return PRIORITY
        else:
            logger = get_logger(
                __name__,
                os.getenv("LOG_FORMAT", "text").lower(),
                getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
            )

            logger.error(
                msg="invalid prompt type",
                extra={
                    "prompt": prompt,
                }
            )
            raise ValueError(f"Invalid prompt type: {prompt}. Must be 'thematic' or 'priority'.")
