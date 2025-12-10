"""Logging configuration utility.

This module sets up structured logging for the application with appropriate
formatters and handlers for different environments.
"""

import logging
import sys
from typing import Optional
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = 'INFO') -> None:
    """Configure application-wide logging.

    Sets up JSON-formatted structured logging for production environments
    and standard formatted logging for development.

    :param log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :type log_level: str
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)

    # Use JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)

    # Set specific logger levels
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)



