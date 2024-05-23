from google.cloud.loggin import setup_logging
from google.cloud.logging_v2.handlers import StructuredLogHandler


def setup_logger():
    handler = StructuredLogHandler()
    setup_logging(handler)
