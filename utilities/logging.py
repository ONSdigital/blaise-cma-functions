from google.cloud.logging_v2.handlers import StructuredLogHandler, setup_logging


def setup_logger():
    handler = StructuredLogHandler()
    setup_logging(handler)
