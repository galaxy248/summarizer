from __future__ import annotations

import os
import logging
from contextlib import contextmanager
from typing import Generator, TYPE_CHECKING

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from summarizer.utils import get_logger

if TYPE_CHECKING:
    from summarizer.utils import Logger

Base = declarative_base()


class Database(Base):
    __abstract__ = True
    session: Session = None

    def __init__(self, session: Session, logger: Logger = None):
        self.session = session
        self.logger = logger or get_logger(
            __name__,
            os.getenv("LOG_FORMAT", "text").lower(),
            getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
        )

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        if self.session is None:
            raise ValueError("Database session is not initialized.")
        try:
            yield self.session
            if self.session.dirty or self.session.new or self.session.deleted:
                self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def rollback(self):
        if self.session:
            self.session.rollback()

    def close(self):
        if self.session:
            self.session.close()
            self.session = None
