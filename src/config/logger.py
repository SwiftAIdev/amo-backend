import logging
import datetime
import logging
import sys
import uuid
from pyclm.logging import Logger
from src.config.cfg import DEPLOYMENT_STAGE, NAME_SERVICE, YC_GROUP_ID, YC_TOKEN


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = getattr(record, 'request_id', uuid.uuid4().__str__())
        return True


class YandexCloudLoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logger = Logger(
            log_group_id=YC_GROUP_ID,
            resource_id=NAME_SERVICE,
            resource_type=DEPLOYMENT_STAGE,
            credentials={"token": YC_TOKEN}
        )

    def emit(self, record):
        if isinstance(record.msg, dict):
            data = record.msg
        else:
            data = {
                "message": record.msg
            }
        data["x_request_id"] = getattr(record, 'x_request_id', uuid.uuid4().__str__())
        data["time"] = str(datetime.datetime.now())
        match record.levelno:
            case logging.DEBUG:
                call_fun = self.logger.debug
            case logging.INFO:
                call_fun = self.logger.info
            case logging.WARNING:
                call_fun = self.logger.warn
            case logging.WARNING:
                call_fun = self.logger.warn
            case logging.ERROR:
                call_fun = self.logger.error
            case logging.FATAL:
                call_fun = self.logger.fatal
            case logging.CRITICAL:
                call_fun = self.logger.critical
            case _:
                call_fun = self.logger.info
        call_fun(**data)
        return True


def get_logger():
    logger = logging.getLogger('python-logstash-logger')
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)

    ycl_handler = YandexCloudLoggingHandler()
    ycl_handler.setLevel(logging.INFO)
    logger.addHandler(ycl_handler)

    logger.addFilter(RequestIdFilter())

    return logger

logger = get_logger()