import logging
import sys
from typing import Optional
from contextvars import ContextVar
from pythonjsonlogger import json

task_id_var: ContextVar[Optional[str]] = ContextVar('task_id_var', default=None)

class TaskContextFilter(logging.Filter):
    def filter(self, record):
        record.task_id = task_id_var.get()
        record.input_type = getattr(record, 'input_type', None)
        record.service = getattr(record, 'service', 'summary-api')
        return True

def setup_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level.upper())
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level.upper())

    json_formatter = json.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s %(task_id)s %(input_type)s %(service)s',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )

    console_handler.setFormatter(json_formatter)
    console_handler.addFilter(TaskContextFilter())
    root_logger.addHandler(console_handler)

    logging.getLogger('sqlalchemy').setLevel('WARNING')
    logging.getLogger('asyncio').setLevel('WARNING')
    logging.getLogger('aio_pika').setLevel('WARNING')
    logging.getLogger('aiormq').setLevel('WARNING')