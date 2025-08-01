from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Session
from summarizer.db import get_db_session_depends
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Form

from .exceptions import (
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError, 
    UserCreationError,
    UserNotFoundError,
    UserPasswordError,
)
from .database import UserRepository

from app.api.auth.token import TokenData
from app.api.auth.token import router_token_verification

if TYPE_CHECKING:
    from app.api.auth.token.jwt_token import JWTManager

router = APIRouter(prefix="/user")

@router.get("/")
async def get_current_user(session: Session = Depends(get_db_session_depends), payload = Depends(router_token_verification.verify_token)):
    user_repo = UserRepository(session)
    user = user_repo.get_user_by_id(payload.user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "created_at": user.created_at.isoformat(),
    }

@router.post("/register")
async def register_user(
    username: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_db_session_depends)
):
    user_repo = UserRepository(session)

    try:
        new_user = user_repo.add_new_user(username, first_name, last_name, email, password)
    except UsernameAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UserCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "first_name": new_user.first_name,
        "last_name": new_user.last_name,
        "created_at": new_user.created_at.isoformat(),
    }

@router.post("/login")
async def login_user(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_db_session_depends),
    jwt_manager: JWTManager = Depends(router_token_verification.get_jwt_manager)
):
    user_repo = UserRepository(session)

    try:
        user = user_repo.authenticate_user(username, password)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UserPasswordError as e:
        raise HTTPException(status_code=401, detail=str(e))

    token_data = jwt_manager.create_access_token(
        TokenData(
            sub=user.username,
            name=f"f: [{user.first_name}], l: [{user.last_name}]",
            user_id=str(user.id)
        )
    )

    return {
        "success": True,
        "message": "Login successful",
        "redirect_url": "/dashboard",
        "user": {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name
        },
        "token": token_data
    }

@router.post("/logout")
async def logout_user():
    response = RedirectResponse(url="/login", status_code=302)
    return response
