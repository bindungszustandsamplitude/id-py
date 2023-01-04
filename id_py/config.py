import logging

class Config:
    # enables request logging -> persist every external request in embedded database
    request_logging_enabled = True

    # global log level
    logging.basicConfig(level=logging.WARN)

    # selected specs
    # just append another key that is _included_ in the spec you search for. case-insensitive.
    # example: appending 'head-up' may yield 'Ohne Head-Up Display'
    # another example: appending 'modelljahr' may yield 'VWD Modelljahreswechsel'
    # 
    SELECTED_SPECS: list[str] = [
        'Softwareverbund',
        'Fertigungsablauf',
        'Assistenzpaket',
        'Head-Up',
        'Modelljahr',
    ]