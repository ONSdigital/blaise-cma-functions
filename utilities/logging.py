from google.cloud.logging import setup_logging
from google.cloud.logging_v2.handlers import StructuredLogHandler


def setup_logger():
    handler = StructuredLogHandler()
    setup_logging(handler)
