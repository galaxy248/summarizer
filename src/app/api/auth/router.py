from fastapi import APIRouter
from .user.router import router as user_router

router = APIRouter(prefix="/auth")

router.include_router(user_router)
