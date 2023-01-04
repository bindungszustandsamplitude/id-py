import logging

class Config:
    # enables request logging -> persist every external request in embedded database
    request_logging_enabled = True

    # global log level
    logging.basicConfig(level=logging.WARN)