from google.cloud import logging


def setup_logger():
    client = logging.Client()
    client.setup_logging()