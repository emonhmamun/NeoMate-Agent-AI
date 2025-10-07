"""
Configuration Loader Module for NeoMate AI

This module provides a centralized, robust way to load and access configuration settings
from the settings.yaml file. It includes validation, environment variable overrides,
caching, and comprehensive error handling to ensure reliable configuration management.

Features:
- YAML file loading with validation
- Environment variable override support
- Configuration caching for performance
- Comprehensive error handling and logging
- Type hints for better code maintainability

Author: NeoMate AI Team
Version: 1.0.0
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml


logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    A singleton class responsible for loading and managing application configuration.

    This class provides methods to load YAML configuration files, validate them,
    apply environment variable overrides, and cache the results for efficient access.
    """

    _instance: Optional['ConfigLoader'] = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls) -> 'ConfigLoader':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._config = self._load_and_validate_config()

    def get_config(self) -> Dict[str, Any]:
        """
        Get the loaded and validated configuration.

        Returns:
            Dict[str, Any]: The complete configuration dictionary.
        """
        return self._config

    def _load_and_validate_config(self) -> Dict[str, Any]:
        """
        Load configuration from settings.yaml file with validation and overrides.

        Returns:
            Dict[str, Any]: Validated configuration dictionary.

        Raises:
            FileNotFoundError: If the configuration file is not found.
            yaml.YAMLError: If there's an error parsing the YAML file.
            ValueError: If required configuration keys are missing.
        """
        config_path = self._get_config_path()

        if not config_path.exists():
            error_msg = (
                f"Configuration file 'settings.yaml' not found at {config_path}. "
                "Please ensure it exists in the 'config' directory."
            )
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                if config is None:
                    config = {}
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            raise

        logger.info(f"Configuration loaded from {config_path}")

        # Validate required keys
        self._validate_config(config)

        # Apply environment variable overrides
        config = self._apply_env_overrides(config)

        logger.info("Configuration validation and overrides applied successfully")
        return config

    def _get_config_path(self) -> Path:
        """
        Determine the absolute path to the configuration file.

        Returns:
            Path: Absolute path to settings.yaml.
        """
        # Assuming this script is in src/utils/, config is at project root
        return Path(__file__).parent.parent.parent / "config" / "settings.yaml"

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate that required configuration keys are present.

        Args:
            config (Dict[str, Any]): Configuration dictionary to validate.

        Raises:
            ValueError: If required keys are missing.
        """
        required_keys = [
            'application.name',
            'application.version',
            'llm.primary_provider',
            'privacy.encryption'
        ]

        missing_keys = []
        for key in required_keys:
            keys = key.split('.')
            value = config
            try:
                for k in keys:
                    value = value[k]
                if value is None:
                    missing_keys.append(key)
            except (KeyError, TypeError):
                missing_keys.append(key)

        if missing_keys:
            error_msg = f"Missing required configuration keys: {', '.join(missing_keys)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.

        Environment variables should be prefixed with 'NEOMATE_' and use underscores
        instead of dots (e.g., NEOMATE_APPLICATION_NAME).

        Args:
            config (Dict[str, Any]): Original configuration dictionary.

        Returns:
            Dict[str, Any]: Configuration with environment overrides applied.
        """
        def apply_override(conf: Dict[str, Any], path: str = '') -> Dict[str, Any]:
            result = {}
            for key, value in conf.items():
                current_path = f"{path}_{key}".upper() if path else key.upper()
                env_key = f"NEOMATE_{current_path}"

                env_value = os.getenv(env_key)
                if env_value is not None:
                    # Try to convert to appropriate type
                    if isinstance(value, bool):
                        result[key] = env_value.lower() in ('true', '1', 'yes')
                    elif isinstance(value, int):
                        try:
                            result[key] = int(env_value)
                        except ValueError:
                            result[key] = value
                    elif isinstance(value, float):
                        try:
                            result[key] = float(env_value)
                        except ValueError:
                            result[key] = value
                    else:
                        result[key] = env_value
                    logger.info(f"Applied environment override for {env_key}")
                elif isinstance(value, dict):
                    result[key] = apply_override(value, current_path)
                else:
                    result[key] = value
            return result

        return apply_override(config)


# Global configuration instance
config_loader = ConfigLoader()
CONFIG = config_loader.get_config()


if __name__ == "__main__":
    """
    Test script to verify configuration loading.
    Run this module directly to see the loaded configuration.
    """
    import json
    print("Loaded Configuration:")
    print(json.dumps(CONFIG, indent=2, default=str))
