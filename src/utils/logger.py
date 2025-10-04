"""
NeoMate AI Logger Module

This module provides a centralized, configurable logging system for NeoMate AI using Loguru.
It supports multiple output sinks (console and file) with structured formatting, automatic
rotation, retention, and compression. The logger integrates with the application's
configuration system for dynamic log level control.

Features:
- Colored console output for real-time monitoring
- File logging with automatic rotation and compression
- Structured log format with timestamps, levels, and source information
- Automatic exception handling with full stack traces
- Configurable log levels via settings.yaml
- Thread-safe and performant logging

Usage:
    from src.utils.logger import setup_logger, logger

    # Initialize logging (call once at application startup)
    setup_logger()

    # Use logger throughout the application
    logger.info("Application started")
    logger.error("An error occurred", exc_info=True)
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from src.utils.config_loader import config


def setup_logger(log_level: Optional[str] = None) -> None:
    """
    Initialize and configure the logging system for NeoMate AI.

    This function sets up multiple logging sinks with appropriate formatting,
    rotation, and retention policies. It integrates with the application's
    configuration system to determine log verbosity.

    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                  If None, uses config.application.log_level.

    Raises:
        ValueError: If invalid log level is provided.
        PermissionError: If log file cannot be created/written.

    Example:
        >>> setup_logger()
        >>> setup_logger("DEBUG")
    """
    # Remove default logger to avoid duplicate logs
    logger.remove()

    # Determine log level from config or parameter
    if log_level is None:
        try:
            log_level = config.application.log_level.upper()
        except AttributeError:
            log_level = "INFO"  # Fallback if config not available

    # Validate log level
    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if log_level not in valid_levels:
        raise ValueError(f"Invalid log level '{log_level}'. Must be one of {valid_levels}")

    # Convert string level to numeric for Loguru
    level_map = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50
    }
    numeric_level = level_map[log_level]

    # Define structured log format
    base_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}:{function}:{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console sink with colors
    logger.add(
        sys.stdout,
        level=numeric_level,
        format=base_format,
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe
        catch=True     # Catch and log exceptions in logging itself
    )

    # File sink with rotation, retention, and compression
    log_file_path = Path("logs/neomate.log")
    log_file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure logs directory exists

    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )

    try:
        logger.add(
            log_file_path,
            level=numeric_level,
            format=file_format,
            rotation="10 MB",      # Rotate when file reaches 10MB
            retention="30 days",   # Keep logs for 30 days
            compression="gz",      # Compress old logs with gzip
            encoding="utf-8",
            backtrace=True,
            diagnose=True,
            enqueue=True,
            catch=True
        )
    except PermissionError as e:
        # Fallback to console-only if file logging fails
        logger.warning(f"Could not set up file logging: {e}. Using console only.")

    # Add exception handler for unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Log unhandled exceptions with full stack trace."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical(
            "Unhandled exception occurred"
        )

    # Install exception handler
    sys.excepthook = handle_exception

    # Log successful initialization
    logger.info("Logger initialized successfully")
    logger.debug(f"Log level set to {log_level}")
    logger.debug(f"Console and file logging enabled")


# Export the configured logger instance for easy import
__all__ = ["setup_logger", "logger"]
