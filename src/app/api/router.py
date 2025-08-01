from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from .auth import auth_router
from .summarize import summarize_router


__API_VERSION__ = "v1.0.0"
__API_PREFIX__ = f"/api/{__API_VERSION__[:2]}"

router = APIRouter(prefix=__API_PREFIX__)

router.include_router(auth_router)
router.include_router(summarize_router)

@router.get("/")
async def api_root():
    return RedirectResponse(url="/")

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "API Service", "version": __API_VERSION__}
