"""
NeoMate AI Main Entry Point

This module serves as the heartbeat and starting point of the NeoMate AI application.
It bootstraps the application, initializes all core infrastructure modules (configuration,
logging, etc.), and starts the main application loop. This is the first file executed
when users run NeoMate.

For Phase 1, this provides a minimal skeleton proving that all utility modules work
together correctly. In the future, this will bring the Cognitive Control Architecture
or "brain" to life.

Features:
- Async application bootstrap
- Configuration and logging initialization
- Main application loop with graceful shutdown
- Error handling and signal management

Author: NeoMate AI Team
Version: 1.0.0
License: MIT
"""

import asyncio
import signal
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.config_loader import ConfigLoader
from utils.logger import log
from utils.helpers import PROJECT_ROOT


class NeoMateApp:
    """
    Main NeoMate AI application class.

    This class encapsulates the application lifecycle, initialization,
    and main execution loop.
    """

    def __init__(self):
        self.config_loader = ConfigLoader()
        self.config = None
        self.running = False

    async def initialize(self) -> bool:
        """
        Initialize the application components.

        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Load configuration
            self.config = self.config_loader.get_config()
            log.info("Configuration loaded successfully")

            # Log application startup
            app_name = self.config.get('application', {}).get('name', 'NeoMate AI')
            app_version = self.config.get('application', {}).get('version', '1.0.0')
            log.info(f"Starting {app_name} version {app_version}...")

            # Initialize other components here in the future
            # - Input modules (voice, vision, etc.)
            # - Processing modules (LLM, reasoning, etc.)
            # - Output modules (speech, actions, etc.)
            # - Memory and storage systems

            log.info("Application initialized successfully")
            return True

        except Exception as e:
            log.error(f"Failed to initialize application: {e}")
            return False

    async def run_main_loop(self):
        """
        Main application loop.

        This loop will eventually implement the core "listen -> think -> act" cycle.
        Currently, it's a placeholder that demonstrates the async structure.
        """
        log.info("Entering main application loop")

        try:
            while self.running:
                # Placeholder for main application logic
                # Future: Listen for inputs, process them, generate responses
                log.debug("Main loop iteration - listening for inputs...")

                # Simulate processing time
                await asyncio.sleep(10)

        except asyncio.CancelledError:
            log.info("Main loop cancelled")
        except Exception as e:
            log.error(f"Error in main loop: {e}")
        finally:
            log.info("Exited main application loop")

    async def shutdown(self):
        """
        Gracefully shutdown the application.
        """
        log.info("Initiating application shutdown...")

        self.running = False

        # Shutdown components in reverse order
        # Future: Clean up resources, save state, etc.

        app_name = self.config.get('application', {}).get('name', 'NeoMate AI') if self.config else 'NeoMate AI'
        log.info(f"{app_name} shutdown complete. Goodbye!")

    async def run(self):
        """
        Run the complete application lifecycle.
        """
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            log.info(f"Received signal {signum}, initiating shutdown...")
            asyncio.create_task(self.shutdown())

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initialize application
        if not await self.initialize():
            log.error("Application initialization failed")
            return

        # Start main loop
        self.running = True
        try:
            await self.run_main_loop()
        except KeyboardInterrupt:
            log.info("Received keyboard interrupt")
        except Exception as e:
            log.error(f"Unexpected error in application run: {e}")
        finally:
            await self.shutdown()


async def main():
    """
    Main entry point for NeoMate AI.
    """
    app = NeoMateApp()
    await app.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Graceful exit on Ctrl+C
        pass
    except Exception as e:
        log.error(f"Fatal error: {e}")
        sys.exit(1)
