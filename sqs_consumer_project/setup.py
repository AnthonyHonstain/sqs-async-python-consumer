import logging
from pythonjsonlogger import jsonlogger


def setup_logging():
    log_level = logging.INFO  # or any other level
    logger = logging.getLogger()
    logger.setLevel(log_level)

    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
