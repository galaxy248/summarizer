import os
from threading import Lock
from typing import Dict, Optional, Generator

from dotenv import load_dotenv
from sqlalchemy.engine import Engine
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from .events import DEFAULT_EVENT_LISTENERS

load_dotenv()

DEFAULT_DB_URL = os.getenv("DB_URL")
DEFAULT_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
DEFAULT_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "10"))
DEFAULT_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
DEFAULT_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))


class DBConnectionManager:
    _lock = Lock()
    _engines: Dict[str, Engine] = {}
    _session_makers: Dict[str, sessionmaker] = {}

    @classmethod
    def get_engine(
        cls,
        db_url: str,
        *,
        event_listeners: Dict[str, callable] = DEFAULT_EVENT_LISTENERS,
        pool_size: int = DEFAULT_POOL_SIZE,
        pool_recycle: int = DEFAULT_POOL_RECYCLE,
        max_overflow: int = DEFAULT_MAX_OVERFLOW,
        pool_timeout: int = DEFAULT_POOL_TIMEOUT,
        pool_pre_ping: bool = True,
        **kwargs
    ) -> Engine:
        if db_url not in cls._engines:
            with cls._lock:
                if db_url not in cls._engines:
                    engine = create_engine(
                        db_url,
                        pool_size=pool_size,
                        pool_recycle=pool_recycle,
                        max_overflow=max_overflow,
                        pool_pre_ping=pool_pre_ping,
                        pool_timeout=pool_timeout,
                        **kwargs
                    )
                    if event_listeners:
                        cls.register_event_listeners(engine, event_listeners)
                    cls._engines[db_url] = engine

        return cls._engines[db_url]
    
    @classmethod
    def register_event_listeners(
        cls,
        engine: Engine,
        event_listeners: Dict[str, callable]
    ) -> None:
        for event_name, listener in event_listeners.items():
            event.listen(engine, event_name, listener)

    @classmethod
    def get_session_maker(
        cls,
        db_url: str,
        *,
        engine: Optional[Engine] = None,
        **kwargs
    ) -> sessionmaker:
        if db_url not in cls._session_makers:
            with cls._lock:
                if db_url not in cls._session_makers:
                    if engine is None:
                        engine = cls.get_engine(db_url)
                    cls._session_makers[db_url] = sessionmaker(bind=engine, **kwargs)
        
        return cls._session_makers[db_url]
    
    @classmethod
    def get_session(
        cls,
        db_url: str,
        engine_kwargs: Optional[Dict] = None,
        session_maker_kwargs: Optional[Dict] = None
    ) -> Session:
        engine_kwargs = engine_kwargs or {}
        session_maker_kwargs = session_maker_kwargs or {}

        engine = cls.get_engine(db_url, **engine_kwargs)
        session_maker = cls.get_session_maker(db_url, engine=engine, **session_maker_kwargs)
        
        return session_maker()


def get_db_session(db_url: str, enable_event_listener: bool = True) -> Session:
    return DBConnectionManager.get_session(db_url, engine_kwargs={"event_listeners": DEFAULT_EVENT_LISTENERS if enable_event_listener else {}})

def get_db_session_depends() -> Generator[Session, None, None]:
    if DEFAULT_DB_URL is None:
        raise ValueError("DB_URL environment variable is not set.")
    
    session = get_db_session(DEFAULT_DB_URL, enable_event_listener=True)
    try:
        yield session
    finally:
        session.close()
