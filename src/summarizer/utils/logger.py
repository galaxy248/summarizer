import logging

from threading import Lock
from typing import Dict, Literal

from pythonjsonlogger import jsonlogger


class CustomTextFormatter(logging.Formatter):
    def format(self, record):
        formatted = super().format(record)

        extra_fields = []
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
                'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated',
                'thread', 'threadName', 'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info', 'asctime', 'message'
            ]:
                extra_fields.append(f"[{key}]={value}")
        
        if extra_fields:
            formatted += f" | {' | '.join(extra_fields)}"
        
        return formatted


class Logger:
    _lock: Lock = Lock()
    _loggers: Dict[str, logging.Logger] = {}

    @classmethod
    def create(
        cls,
        name: str,
        formatter_type: Literal['text', 'json'] = 'text',
        level = logging.DEBUG
    ) -> logging.Logger:
    
        with cls._lock:
            if name not in cls._loggers:
                if formatter_type == 'json':
                    formatter = jsonlogger.JsonFormatter(
                        fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S'
                    )
                elif formatter_type == 'text':
                    formatter = CustomTextFormatter(
                        datefmt='%Y/%m/%d %H:%M:%S'
                    )
                else:
                    raise ValueError(f"Unknown formatter type: {formatter_type}")
                
                cls._loggers[name] = cls._initialize_logger(name, formatter, level)
        
        return cls._loggers[name]

    @classmethod
    def _initialize_logger(
        cls,
        name: str,
        formatter: logging.Formatter,
        level = logging.DEBUG
    ) -> logging.Logger:
        
        logger: logging.Logger = logging.getLogger(name)
        logger.setLevel(level)
        
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        logger.handlers.clear()
        logger.addHandler(handler)
        logger.propagate = False

        return logger


def get_logger(
    name: str,
    formatter_type: Literal['text', 'json'] = 'text',
    level: int = logging.DEBUG
) -> logging.Logger:
    return Logger.create(name, formatter_type, level)
