from typing import Tuple

from sqlalchemy.exc import IntegrityError

from .exceptions import (
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError, 
    UserCreationError,
    UserNotFoundError,
    UserPasswordError,
)

from summarizer.db import Database, User


class UserRepository(Database):
    __abstract__ = True
    __table__ = "users"

    def get_user_by_username(self, username: str) -> User:
        with self.get_session() as session:
            return session.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        with self.get_session() as session:
            return session.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: str) -> User:
        with self.get_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, username: str, password: str) -> User:
        user = self.get_user_by_username(username)
        if not user:
            raise UserNotFoundError(username)
        
        if not user.verify_password(password):
            raise UserPasswordError("Password is incorrect")

        return user

    def add_new_user(self, username: str, first_name: str, last_name: str, email: str, password: str) -> User:
        new_user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        new_user.set_password(password)

        try:
            with self.get_session() as session:
                session.add(new_user)
                session.commit()
                session.refresh(new_user)

            return new_user

        except IntegrityError as e:
            if self.get_user_by_username(username):
                raise UsernameAlreadyExistsError(username)
            elif self.get_user_by_email(email):
                raise EmailAlreadyExistsError(email)
            else:
                raise UserCreationError("User creation failed due to an unknown error")

    def check_user_exists(self, username: str = None, email: str = None) -> Tuple[bool, User | None]:
        with self.get_session() as session:
            if username and not email:
                user = session.query(User).filter(User.username == username).first()
                if user:
                    return True, user
                else:
                    return False, None
            
            if email and not username:
                user = session.query(User).filter(User.email == email).first()
                if user:
                    return True, user
                else:
                    return False, None
                
            if username and email:
                user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                if user:
                    return True, user
                else:
                    return False, None

            if not username and not email:
                raise ValueError("At least one of username or email must be provided")
