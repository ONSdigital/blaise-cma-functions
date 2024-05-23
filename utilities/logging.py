from google.cloud.logging import StructuredLogHandler, setup_logging


def setup_logger():
    handler = StructuredLogHandler()
    setup_logging(handler)
