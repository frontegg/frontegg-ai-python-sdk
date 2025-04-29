"""
Logger Module

This module provides a standardized way to set up logging for the SDK.
"""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "ai_agents_sdk",
    level: int = logging.INFO,
    format_string: Optional[str] = None,
    stream_handler: bool = True,
    file_handler: Optional[str] = None,
) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Name of the logger
        level: Logging level (default: INFO)
        format_string: Custom format string for log messages
        stream_handler: Whether to add a stream handler to output logs to the console
        file_handler: Optional path to a file to which logs should be written

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    formatter = logging.Formatter(format_string)

    # Remove any existing handlers to avoid duplicate logs
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    if stream_handler:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    if file_handler:
        file_handler_obj = logging.FileHandler(file_handler)
        file_handler_obj.setFormatter(formatter)
        logger.addHandler(file_handler_obj)
    
    return logger


# Default logger instance for the SDK
default_logger = setup_logger() 