import os
import logging
from dotenv import load_dotenv

load_dotenv()


class JWTSettings:
    def __init__(self, secret_key: str = None, algorithm: str = None, access_token_expire_minutes: int = None):
        self.secret_key: str = secret_key or os.getenv("JWT_SECRET_KEY", "fallback-secret-key-for-development")
        self.algorithm: str = algorithm or os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes: int = access_token_expire_minutes or int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "300"))

        if self.secret_key.startswith("fallback"):
            from summarizer.utils import get_logger
            logger = get_logger(
                __name__,
                os.getenv("LOG_FORMAT", "text").lower(),
                getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
            )
            logger.warning(
                msg="jwt secret_key",
                extra={
                    "info": "Using fallback secret key for JWT. Please set JWT_SECRET_KEY in environment variables.",
                    "fallback": self.secret_key,
                }
            )

jwt_settings = JWTSettings()
