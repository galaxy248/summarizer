class UserException(Exception):
    pass

class UsernameAlreadyExistsError(UserException):
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"Username '{username}' already exists")

class EmailAlreadyExistsError(UserException):
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Email '{email}' already exists")

class UserCreationError(UserException):
    def __init__(self, message: str = "User creation failed"):
        super().__init__(message)

class UserNotFoundError(UserException):
    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' not found")

class UserPasswordError(UserException):
    def __init__(self, message: str = "Password is incorrect"):
        super().__init__(message)

class InvalidCredentialsError(UserException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message)
