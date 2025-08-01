import os
import logging

from summarizer.utils import get_logger

logger = get_logger(
    __name__,
    os.getenv("LOG_FORMAT", "text").lower(),
    getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)
)

def receive_connect(dbapi_connection, connection_record):
    logger.debug(
        msg=f"database connection",
        extra={
            "event": "connect",
            "connection_id": id(dbapi_connection)
        }
    )

def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    logger.debug(
        msg=f"database connection",
        extra={
            "event": "checkout",
            "connection_id": id(dbapi_connection)
        }
    )

def receive_checkin(dbapi_connection, connection_record):
    logger.debug(
        msg=f"database connection",
        extra={
            "event": "checkin",
            "connection_id": id(dbapi_connection)
        }
    )

def receive_invalidate(dbapi_connection, connection_record, exception):
    logger.error(
        msg=f"database connection",
        extra={
            "event": "invalidate",
            "connection_id": id(dbapi_connection),
            "exception": str(exception)
        },
        exc_info=True,
        stack_info=True
    )

def receive_close(dbapi_connection, connection_record):
    logger.debug(
        msg=f"database connection",
        extra={
            "event": "close",
            "connection_id": id(dbapi_connection)
        }
    )

DEFAULT_EVENT_LISTENERS = {
    "connect": receive_connect,
    "checkout": receive_checkout,
    "checkin": receive_checkin,
    "invalidate": receive_invalidate,
    "close": receive_close
}
