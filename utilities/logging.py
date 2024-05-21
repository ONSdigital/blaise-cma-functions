from google.cloud.logging_v2.handlers import (CloudLoggingHandler,
                                              setup_logging)


def setup_logger():
    handler = CloudLoggingHandler()
    setup_logging(handler)
