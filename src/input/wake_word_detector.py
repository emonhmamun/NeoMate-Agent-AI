"""
NeoMate AI Wake Word Detector Module

This module provides real-time wake word detection using openwakeword.
It continuously listens for specified wake words and triggers when detected.

Features:
- Real-time audio processing
- Configurable wake words
- Efficient resource usage
- Integration with NeoMate AI logging and configuration

Author: NeoMate AI Team
Version: 1.0.0
License: MIT
"""

import openwakeword as oww
import pyaudio
import numpy as np
from src.utils.config_loader import CONFIG as settings
from src.utils.logger import log


class WakeWordDetector:
    """
    Wake word detection class using openwakeword.

    This class initializes the wake word engine and provides methods
    to listen for wake words and clean up resources.
    """

    def __init__(self):
        """
        Initialize the wake word detector.

        Sets up openwakeword model and opens audio stream.
        """
        try:
            self.model = oww.Model()
            self.chunk_size = 1280
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                rate=16000,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            log.info("Wake word detector initialized successfully.")
        except Exception as e:
            log.error(f"Failed to initialize wake word detector: {e}")
            raise

    def listen(self):
        """
        Start listening for wake words.

        Continuously processes audio frames and detects wake words.
        Returns True when a wake word is detected.
        """
        log.info("Starting wake word detection...")
        try:
            while True:
                data = self.stream.read(self.chunk_size)
                audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                result = self.model.predict(audio_data)
                # result is a dict with model names as keys and confidence scores as values
                for key, score in result.items():
                    if score > 0.5:
                        log.info(f"Wake word '{key}' detected!")
                        return True
        except Exception as e:
            log.error(f"Error during wake word detection: {e}")
            raise

    def cleanup(self):
        """
        Clean up resources.

        Closes audio stream and terminates openwakeword model.
        """
        try:
            if hasattr(self, 'stream') and self.stream:
                self.stream.close()
            if hasattr(self, 'audio') and self.audio:
                self.audio.terminate()
            if hasattr(self, 'model') and self.model:
                del self.model
            log.info("Wake word detector resources cleaned up.")
        except Exception as e:
            log.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    detector = WakeWordDetector()
    try:
        detector.listen()
    except KeyboardInterrupt:
        log.info("Wake word detection interrupted by user.")
        detector.cleanup()
