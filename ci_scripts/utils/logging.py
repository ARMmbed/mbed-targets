"""Logs errors according to severity of the exception."""
import logging
from .definitions import LOGGER_FORMAT


def log_exception(logger, exception):
    """Logs an exception.

    Args:
        logger: logger
        exception: exception to log
    """
    if logger and exception:
        logger.error(exception)
        logger.debug(exception, exc_info=True)


def set_log_level(verbose_count):
    """Sets the log level.

    Args:
        verbose_count: requested log level count
    """
    if verbose_count > 2:
        log_level = logging.DEBUG
    elif verbose_count == 2:
        log_level = logging.INFO
    elif verbose_count == 1:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR
    logging.basicConfig(level=log_level, format=LOGGER_FORMAT)
