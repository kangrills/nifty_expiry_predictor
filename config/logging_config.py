"""Logging configuration for Nifty Expiry Predictor."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.settings import settings


def setup_logging():
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("nifty_expiry")
    logger.setLevel(getattr(logging, settings.log_level))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.log_level))
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        settings.log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
    )
    file_handler.setLevel(getattr(logging, settings.log_level))
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (defaults to 'nifty_expiry')

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"nifty_expiry.{name}")
    return logging.getLogger("nifty_expiry")


# Initialize logging
logger = setup_logging()
