"""
NeoMate AI Main Entry Point

This module serves as the main entry point for the NeoMate AI application.
It initializes configuration, sets up logging, and prepares the application
for execution by orchestrating core modules.

Features:
- Loads configuration using ConfigManager
- Sets up logging with user-defined log level
- Placeholder for future brain/conductor module integration
- Graceful shutdown on user interrupt
- Robust error handling with detailed logging
"""

import sys

from src.utils.config_loader import ConfigManager
from src.utils.logger import setup_logger, logger
# from src.core.brain import Conductor  # Future import for brain module


def main() -> None:
    """
    Main application logic entry point.

    This function initializes configuration, sets up logging, and starts
    the core application loop (currently a placeholder).

    Raises:
        Any unexpected exceptions are logged and re-raised.
    """
    # Load configuration
    config = ConfigManager()

    # Setup logger with configured log level
    setup_logger(log_level=config.application.log_level)

    logger.info("NeoMate AI is starting...")

    # Future: Initialize and start the Conductor (brain) module
    # conductor = Conductor(config)
    # conductor.run()

    # Placeholder for now
    logger.info("Conductor module is not yet implemented.")
    print("NeoMate AI started. (Conductor module placeholder)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("NeoMate AI is shutting down.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        sys.exit(1)
