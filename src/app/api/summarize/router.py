import os
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from .schema import SummarizeRequest
from .services import SummarizationService
from ...api.auth.token import TokenData, router_token_verification

from summarizer.utils import get_logger
from summarizer.services.storage.user_storage import create_user_storage_manager 


summarize_router = APIRouter(prefix="/summarize")


@summarize_router.post("/")
async def summarize(
    request: SummarizeRequest = Depends(),
    token_data: TokenData = Depends(router_token_verification.verify_token)
):
    storage_manager = create_user_storage_manager(token_data, uuid4())
    logger = get_logger(
        __name__,
        os.getenv("LOG_FORMAT", "text").lower(),
        getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
    )

    try:
        summarization_service = SummarizationService(storage_manager, logger)
        result = await summarization_service.summarize(request)
        
        return JSONResponse(
            status_code=200,
            content={
                "summary": result,
                "session_uuid": str(storage_manager.current_session_uuid)
            }
        )

    except Exception as e:
        logger.error(
            msg="Summarization Error",
            exc_info=e,
            stack_info=True,
            extra={
                "session_uuid": str(storage_manager.current_session_uuid),
            }
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "An error occurred during summarization.",
            }
        )
