from logging import Logger
from typing import TYPE_CHECKING

import markdown
from pymupdf import Document
from fastapi import UploadFile

from .utils import FileUtils

if TYPE_CHECKING:
    from ..schema.request import SummarizeRequest

from summarizer.prompts import PromptFactory
from summarizer.pipelines.summarizer import SummarizerFactory
from summarizer.pipelines.summarizer.config import SummarizerConfig
from summarizer.services.storage.user_storage import UserStorageManager


class SummarizationService:
    def __init__(self, storage_manager: UserStorageManager, logger: Logger):
        self.logger = logger
        self.storage_manager = storage_manager
        self.session_uuid = self.storage_manager.current_session_uuid

    async def summarize(
        self,
        request: "SummarizeRequest",
    ) -> str:
        try:
            if request.file:
                if FileUtils.is_pdf_file(request.file.filename):
                    return await self._pdf_summarize(
                        file=request.file,
                        prompt_mode=request.prompt,
                        model=request.model,
                    )
                elif FileUtils.is_text_file(request.file.filename):
                    text_body = await request.file.read()
                    return await self._text_summarize(
                        text=text_body.decode('utf-8'),
                        prompt_mode=request.prompt,
                        model=request.model,
                    )
            else:
                return await self._text_summarize(
                    text=request.text,
                    prompt_mode=request.prompt,
                    model=request.model,
                )

        except Exception as e:
            self.logger.error(
                msg="Summarization Error",
                exc_info=e,
                stack_info=True,
                extra={
                    "session_uuid": self.session_uuid,
                }
            )
            raise

    async def _pdf_summarize(
        self,
        file: UploadFile,
        prompt_mode: str,
        model: str,
    ) -> str:
        file_name = f"{str(self.session_uuid)}.pdf"

        try:
            self.storage_manager.save_uploaded_file(file, "contents", file_name)
        except Exception as e:
            self.logger.error(
                msg="API Error",
                exc_info=e,
                stack_info=True,
                extra={
                    "file_name": file_name,
                    "session_uuid": self.session_uuid,
                }
            )
            raise

        try:
            pdf_data = self.storage_manager.read_file("contents", file_name)
            pdf_document = Document(stream=pdf_data, filetype="pdf")

            with pdf_document:
                text_content = ""
                for page in pdf_document:
                    text_content += page.get_text()

            return await self._text_summarize(
                text=text_content,
                prompt_mode=prompt_mode,
                model=model,
            )

        except Exception as e:
            self.logger.error(
                msg="API Error",
                exc_info=e,
                stack_info=True,
                extra={
                    "file_name": file_name,
                    "session_uuid": self.session_uuid,
                    "summarize_type": "pdf",
                }
            )
            raise

    async def _text_summarize(
        self,
        text: str,
        prompt_mode: str,
        model: str,
    ) -> str:
        file_name = f"{str(self.session_uuid)}.txt"

        try:
            self.storage_manager.save_text_content(text, file_name)
        except Exception as e:
            self.logger.error(
                msg="API Error",
                exc_info=e,
                stack_info=True,
                extra={
                    "file_name": file_name,
                    "session_uuid": self.session_uuid,
                }
            )
            raise
        
        result = await self._handle_summarizing(
            text=text,
            model=model,
            prompt_mode=prompt_mode,
        )

        html = markdown.markdown(result)
        return html

    async def _handle_summarizing(
        self,
        text: str,
        model: str,
        prompt_mode: str,
    ) -> str:

        prompt = PromptFactory.create(prompt_mode)
        summarizing_config = SummarizerConfig(
            prompt=prompt,
            model=model,
        )
        summarizer = SummarizerFactory.create(summarizing_config)

        try:
            result = summarizer.run(text)
        except Exception as e:
            self.logger.error(
                msg="Summarization Error",
                exc_info=e,
                stack_info=True,
                extra={
                    "text_length": len(text),
                    "model": model,
                    "prompt_mode": prompt_mode,
                    "session_uuid": self.session_uuid,
                }
            )
            raise

        return result
