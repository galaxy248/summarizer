from pydantic import BaseModel, Field


class TokenHeader(BaseModel):
    alg: str = Field(..., description="Algorithm used for signing the token")
    typ: str = Field(..., description="Type of the token, usually 'JWT'")


class TokenData(BaseModel):
    sub: str = Field(..., description="Subject of the token, usually the username")
    name: str = Field(..., description="Name of the user")
    user_id: str = Field(..., description="Unique identifier for the user")


class TokenPayload(TokenData):
    exp: int = Field(..., description="Expiration time of the token as a Unix timestamp")
    iss: str = Field(..., description="Issuer of the token, usually the application name")
    iat: int = Field(..., description="Issued at time of the token as a Unix timestamp")
