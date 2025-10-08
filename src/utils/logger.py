"""
NeoMate AI Logger Module

This module provides a comprehensive, configurable logging system for NeoMate AI.
It supports file and console logging with different levels, log rotation, and
structured formatting for better debugging and monitoring.

Features:
- Hierarchical logging with configurable levels
- File and console output with different verbosity
- Log rotation to prevent disk space issues
- Structured log format with timestamps, modules, and levels
- Error handling and graceful degradation
- Environment-based configuration

Author: NeoMate AI Team
Version: 1.0.0
License: MIT
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


class NeoMateLogger:
    """
    Advanced logger class for NeoMate AI with enhanced features.

    This class provides centralized logging configuration with support for
    multiple handlers, log rotation, and environment-specific settings.
    """

    _instance: Optional['NeoMateLogger'] = None
    _logger: Optional[logging.Logger] = None

    def __new__(cls) -> 'NeoMateLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._logger is None:
            self._logger = self._setup_logger()

    def get_logger(self) -> logging.Logger:
        """Get the configured logger instance."""
        return self._logger

    def _setup_logger(self) -> logging.Logger:
        """
        Setup and configure the logger with all handlers and formatters.

        Returns:
            logging.Logger: Configured logger instance
        """
        # Create logger
        logger = logging.getLogger("NeoMateAI")
        logger.setLevel(self._get_log_level())

        # Prevent duplicate handlers
        if logger.handlers:
            return logger

        # Create logs directory
        logs_dir = Path('logs')
        logs_dir.mkdir(exist_ok=True)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / 'neomate.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self._get_console_level())
        console_handler.setFormatter(formatter)

        # Error file handler
        error_handler = logging.FileHandler(logs_dir / 'neomate_errors.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.addHandler(error_handler)

        return logger

    def _get_log_level(self) -> int:
        """Get log level from environment or default to DEBUG."""
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        level = level_map.get('DEBUG')  # Default to DEBUG
        return level

    def _get_console_level(self) -> int:
        """Get console log level, default to INFO."""
        return logging.INFO


# Global logger instance
_logger_instance = NeoMateLogger()
log = _logger_instance.get_logger()
