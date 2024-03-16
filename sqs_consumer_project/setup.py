import logging
from pythonjsonlogger import jsonlogger


def setup_logging():
    log_level = logging.INFO  # or any other level
    httpx_log_level = logging.DEBUG  # For detailed connection logs

    logger = logging.getLogger()
    logger.setLevel(log_level)

    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    # Configure HTTPX and httpcore logging
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(httpx_log_level)

    httpcore_logger = logging.getLogger("httpcore")
    httpcore_logger.setLevel(httpx_log_level)
