import logging
import os

class Config:
    # enables request logging -> persist every external request in embedded database
    request_logging_enabled = True

    # global log level
    logging.basicConfig(level=logging.WARN)

    # location of the spec file. every spec comes into a new line. put a substring of a desired spec into every new line.
    # example for a spec config:
    # softwareverbund
    # fertigungsablauf
    # -> both properties will be shown if found. if nothing found, nothing will be shown
    SPEC_CONFIG_LOCATION = os.getenv('SPEC_CONFIG_LOCATION')

# class end