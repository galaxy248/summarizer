import uuid
import string
import secrets

from sqlalchemy.sql import func
from passlib.hash import pbkdf2_sha256
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, CHAR

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    password_salt_length = 32

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    email = Column(String(254), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    password_salt = Column(CHAR(password_salt_length), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

    def __str__(self):
        return f"User(id={self.id}, username={self.username}, email={self.email})"

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email
        }
    
    def hash_password(self, password: str) -> str:
        hashed_password = pbkdf2_sha256.hash(password + self.password_salt)
        return hashed_password
    
    def generate_salt(self, length: int = 32) -> str:
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(characters) for _ in range(length))

    def update_current_password(self, password: str) -> None:
        if not self.password_salt:
            self.password_salt = self.generate_salt()
        self.password_hash = self.hash_password(password)
    
    def set_password(self, password: str) -> None:
        self.password_salt = self.generate_salt()
        self.password_hash = self.hash_password(password)

    def verify_password(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password + self.password_salt, self.password_hash)
