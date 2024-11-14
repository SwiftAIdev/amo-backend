import logging
from contextlib import contextmanager
from typing import Dict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


@contextmanager
def log_context(context: Dict[str, str]):
    logger = logging.getLogger()
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        for key, value in context.items():
            setattr(record, key, value)
        return record

    logging.setLogRecordFactory(record_factory)
    try:
        yield
    finally:
        logging.setLogRecordFactory(old_factory)

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next):
        self.logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        self.logger.info(f"Response status: {response.status_code}")
        return response