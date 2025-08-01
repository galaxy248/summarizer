from typing import Annotated, Optional

from fastapi import Form, File, UploadFile, HTTPException

from ..services.utils import FileUtils
from summarizer.pipelines.summarizer.config import (
    ALLOWED_MODELS,
    ALLOWED_PROMPT_MODES,
)


class SummarizeRequest:
    prompt: Annotated[str, Form(...)]
    model: Annotated[str, Form(...)]
    text: Annotated[Optional[str], Form(None)]
    file: Annotated[Optional[UploadFile], File(None)]

    def __init__(
        self,
        prompt: str = Form(...),
        model: str = Form(...),
        text: Optional[str] = Form(None),
        file: Optional[UploadFile] = File(None),
    ):
        self.prompt = self._validate_prompt(prompt)
        self.model = self._validate_model(model)
        self.text = text
        self.file = self._validate_file(file)
        
        if self.text and self.file:
            raise HTTPException(status_code=422, detail="Only one of 'text' or 'file' should be provided.")

    def _validate_prompt(self, v: str):
        v = v.lower()
        if v not in ALLOWED_PROMPT_MODES:
            raise HTTPException(status_code=422, detail=f"Invalid prompt mode. Allowed: {', '.join(ALLOWED_PROMPT_MODES)}")
        return v

    def _validate_model(self, v: str):
        v = v.lower()
        if v not in ALLOWED_MODELS:
            raise HTTPException(status_code=422, detail=f"Invalid model. Allowed: {', '.join(ALLOWED_MODELS)}")
        return v

    def _validate_file(self, f: Optional[UploadFile]):
        if f and f.filename:
            if not FileUtils.is_text_file(f.filename) and \
               not FileUtils.is_pdf_file(f.filename):
                raise HTTPException(status_code=422, detail="Invalid file type. Only .txt, .md, .pdf supported.")
        return f
