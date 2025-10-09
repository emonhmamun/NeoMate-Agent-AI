"""
NeoMate AI Wake Word Detector Module

This module provides an always-on wake word detection system for NeoMate AI using
open-source technologies. It continuously listens to microphone input in the background
and triggers when predefined wake words (e.g., "Hey NeoMate") are detected.

Features:
- Offline wake word detection using openwakeword library
- Real-time audio processing with pyaudio
- Configurable confidence threshold
- Asynchronous operation for integration with asyncio-based architecture
- Comprehensive logging and error handling
- Graceful cleanup and resource management

Author: NeoMate AI Team
Version: 1.0.0
License: MIT
"""

import asyncio
import numpy as np
import pyaudio
from typing import Optional, Dict, Any
import openwakeword

from src.utils.config_loader import ConfigLoader
from src.utils.logger import log


class WakeWordDetector:
    """
    Wake Word Detector class for NeoMate AI.

    This class encapsulates the wake word detection functionality, providing
    an interface to initialize, start listening, and clean up resources.
    """

    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        """
        Initialize the WakeWordDetector.

        Args:
            config_loader: Optional ConfigLoader instance for configuration.
                          If None, a new instance will be created.
        """
        self.config_loader = config_loader or ConfigLoader()
        self.config = self.config_loader.get_config()

        # Wake word detection parameters
        self.confidence_threshold = self.config.get('wake_word', {}).get('confidence_threshold', 0.5)

        # Audio parameters
        self.chunk_size = 1280
        self.sample_rate = 16000
        self.format = pyaudio.paInt16
        self.channels = 1

        # Audio components
        self.audio = None
        self.stream = None
        self.oww_model = None

        # Control flags
        self.is_listening = False
        self.detection_event = asyncio.Event()

        log.info("WakeWordDetector initialized successfully")

    async def initialize(self) -> bool:
        """
        Initialize audio components and wake word model.

        Returns:
            bool: True if initialization successful, False otherwise.
        """
        try:
            # Initialize PyAudio
            self.audio = pyaudio.PyAudio()

            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )

            # Get pretrained model paths
            model_paths = openwakeword.get_pretrained_model_paths()

            # Initialize OpenWakeWord model
            self.oww_model = openwakeword.Model(
                wakeword_models=model_paths,
                inference_framework='tflite'
            )

            log.info("WakeWordDetector components initialized successfully")
            return True

        except Exception as e:
            log.error(f"Failed to initialize WakeWordDetector: {e}")
            await self.cleanup()
            return False

    async def listen(self) -> bool:
        """
        Start listening for wake words asynchronously.

        This method runs an infinite loop that continuously processes audio
        chunks and checks for wake word detection.

        Returns:
            bool: True if wake word detected, False if error occurred.
        """
        if not await self.initialize():
            return False

        self.is_listening = True
        log.info("WakeWordDetector started listening")

        try:
            while self.is_listening:
                # Read audio chunk
                audio_data = await asyncio.to_thread(
                    self.stream.read,
                    self.chunk_size,
                    exception_on_overflow=False
                )

                # Convert to numpy array
                audio_np = np.frombuffer(audio_data, dtype=np.int16)

                # Run wake word detection in thread
                predictions = await asyncio.to_thread(self.oww_model.predict, audio_np)

                # Check for wake word detection
                for model_name, confidence in predictions.items():
                    if confidence > self.confidence_threshold:
                        log.info(f"Wake word detected: {model_name} (confidence: {confidence:.2f})")
                        self.detection_event.set()
                        return True

                # Small delay to prevent excessive CPU usage
                await asyncio.sleep(0.01)

        except asyncio.CancelledError:
            log.info("Wake word listening cancelled")
        except Exception as e:
            log.error(f"Error during wake word listening: {e}")
            return False
        finally:
            self.is_listening = False

        return False

    async def stop_listening(self):
        """
        Stop the listening process gracefully.
        """
        self.is_listening = False
        log.info("WakeWordDetector stopped listening")

    async def cleanup(self):
        """
        Clean up resources and close audio components.
        """
        try:
            if self.stream:
                await asyncio.to_thread(self.stream.stop_stream)
                await asyncio.to_thread(self.stream.close)
                self.stream = None

            if self.audio:
                await asyncio.to_thread(self.audio.terminate)
                self.audio = None

            if self.oww_model:
                # OpenWakeWord model cleanup if available
                self.oww_model = None

            log.info("WakeWordDetector resources cleaned up")

        except Exception as e:
            log.error(f"Error during cleanup: {e}")

    async def wait_for_wake_word(self) -> bool:
        """
        Wait for wake word detection event.

        Returns:
            bool: True if wake word detected, False otherwise.
        """
        await self.detection_event.wait()
        return True

    def reset_detection_event(self):
        """
        Reset the wake word detection event.
        """
        self.detection_event.clear()


# Standalone execution for testing
async def main():
    """
    Main function for standalone execution and testing.
    """
    detector = WakeWordDetector()

    try:
        detected = await detector.listen()
        if detected:
            print("Wake word detected!")
        else:
            print("Listening stopped without detection")
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        await detector.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
