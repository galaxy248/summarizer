from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .jwt_token import JWTManager
from .models import TokenData
from .exceptions import TokenValidationError, TokenExpiredError


auth_scheme = HTTPBearer()

class RouterTokenVerification:
    jwt_manager: JWTManager

    def __init__(self, jwt_manager: JWTManager):
        self.__class__.jwt_manager = jwt_manager

    @classmethod
    async def verify_token(cls, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> TokenData:
        if not credentials or not credentials.scheme == "Bearer":
            raise ValueError("Invalid authentication scheme")

        token = credentials.credentials
        if not token:
            raise ValueError("Token is missing")

        try:
            payload = cls.jwt_manager.verify_token(token)
            return payload
        except TokenExpiredError as e:
            raise HTTPException(
                status_code=401,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        except TokenValidationError as e:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e

    @classmethod
    def get_auth_scheme(cls) -> HTTPBearer:
        return cls.auth_scheme
    
    @classmethod
    def get_jwt_manager(cls) -> JWTManager:
        return cls.jwt_manager


router_token_verification = RouterTokenVerification(JWTManager())
