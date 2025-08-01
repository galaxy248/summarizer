from __future__ import annotations

import jwt
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from .config import jwt_settings as DEFAULT_JWT_SETTINGS
from .models import TokenHeader, TokenPayload, TokenData
from .exceptions import TokenValidationError, TokenExpiredError, TokenPayloadError

if TYPE_CHECKING:
    from .config import JWTSettings


class JWTManager:
    jwt_settings: JWTSettings

    def __init__(self, jwt_settings: Optional[JWTSettings] = None):
        self.__class__.jwt_settings = jwt_settings or DEFAULT_JWT_SETTINGS

    def create_header(self) -> TokenHeader:
        return TokenHeader(
            alg=self.jwt_settings.algorithm,
            typ="JWT",
        )

    def create_payload(self, data: TokenData) -> TokenPayload:
        current_time = datetime.now().astimezone()
        expire = current_time + timedelta(minutes=self.jwt_settings.access_token_expire_minutes)

        return TokenPayload(
            sub=data.sub,
            name=data.name,
            user_id=data.user_id,
            exp=int(expire.timestamp()),
            iat=int(current_time.timestamp()),
            iss="Summerizer",
        )

    def create_access_token(self, data: TokenData) -> str:
        header = self.create_header()
        payload = self.create_payload(data)

        token = jwt.encode(
            payload=payload.model_dump(),
            key=self.jwt_settings.secret_key,
            algorithm=self.jwt_settings.algorithm,
            headers=header.model_dump(),
        )

        return token

    @classmethod
    def verify_token(cls, token: str) -> TokenData:
        try:
            payload = jwt.decode(
                jwt=token,
                key=cls.jwt_settings.secret_key,
                algorithms=[cls.jwt_settings.algorithm],
                options={"require": ["exp", "iat", "sub"]},
                leeway=10,
            )

            username = payload.get("sub")
            user_id = payload.get("user_id")
            if username is None or user_id is None:
                raise TokenPayloadError("token payload is missing required fields")

            return TokenData(
                sub=username,
                name=payload.get("name", ""),
                user_id=user_id,
            )

        except ExpiredSignatureError as e:
            raise TokenExpiredError("token has expired") from e
        except InvalidTokenError as e:
            raise TokenValidationError("invalid token") from e
