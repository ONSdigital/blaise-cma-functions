import inspect

from google.cloud.logging.handlers import StructuredLogHandler
from google.cloud.logging_v2.handlers import setup_logging


def setup_logger():
    handler = StructuredLogHandler()
    setup_logging(handler)


def function_name():
    return f"{inspect.stack()[1][3]}()"
