class TokenException(Exception):
    pass

class TokenValidationError(TokenException):
    def __init__(self, message: str = "Token validation failed"):
        super().__init__(message)

class TokenPayloadError(TokenException):
    def __init__(self, message: str = "Invalid token payload"):
        super().__init__(message)

class TokenExpiredError(TokenException):
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message)

class TokenCreationError(TokenException):
    def __init__(self, message: str = "Token creation failed"):
        super().__init__(message)
