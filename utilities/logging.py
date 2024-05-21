import logging
import google.cloud.logging
from google.cloud.logging_v2.handlers import (CloudLoggingHandler,
                                              setup_logging)


def setup_logger():
    client = google.cloud.logging.Client()
    handler = CloudLoggingHandler(client)
    setup_logging(handler)
    logging.getLogger().setLevel(logging.DEBUG)

