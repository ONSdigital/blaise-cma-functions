from google.cloud import logging


def setup_logger():
    # Instantiates a client
    client = logging.Client()

    # Connects the logger to the root logging handler
    client.setup_logging()
