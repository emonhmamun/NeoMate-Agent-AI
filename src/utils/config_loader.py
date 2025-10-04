"""
NeoMate AI Configuration Loader

This module provides a singleton configuration manager that loads settings from
config/settings.yaml and handles environment variable substitution securely.

Usage:
    from src.utils.config_loader import config

    # Access settings
    provider = config.llm.provider
    api_key = config.llm.api_key
    theme = config.ui.theme
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dotenv import load_dotenv


class ConfigManager:
    """
    Singleton configuration manager for NeoMate AI.

    This class ensures that the configuration file is loaded only once and
    provides easy access to nested settings using dot notation.
    """

    _instance: Optional['ConfigManager'] = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._config is None:
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file and substitute environment variables."""
        # Load environment variables from .env file if it exists
        load_dotenv()

        # Determine the path to the config file
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # Go up to project root
        config_path = project_root / "config" / "settings.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        # Load YAML configuration
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                self._config = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

        # Substitute environment variables
        self._config = self._substitute_env_vars(self._config)

        logging.info("Configuration loaded successfully")

    def _substitute_env_vars(self, data: Any) -> Any:
        """
        Recursively substitute environment variables in the configuration data.

        Args:
            data: Configuration data (dict, list, or primitive)

        Returns:
            Data with environment variables substituted
        """
        if isinstance(data, dict):
            return {key: self._substitute_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            return self._substitute_string(data)
        else:
            return data

    def _substitute_string(self, value: str) -> str:
        """
        Substitute environment variables in a string value.

        Supports ${VAR_NAME} syntax.

        Args:
            value: String that may contain environment variable placeholders

        Returns:
            String with environment variables substituted
        """
        import re

        def replace_var(match):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value is None:
                logging.warning(f"Environment variable '{var_name}' not found")
                return match.group(0)  # Return original placeholder if not found
            return env_value

        # Replace ${VAR_NAME} with environment variable values
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_var, value)

    def __getattr__(self, name: str) -> Any:
        """Allow dot notation access to configuration sections."""
        if self._config is None:
            raise RuntimeError("Configuration not loaded")

        if name not in self._config:
            raise AttributeError(f"Configuration section '{name}' not found")

        value = self._config[name]
        if isinstance(value, dict):
            # Return a nested accessor for dict values
            return _NestedConfigAccessor(value)
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.

        Args:
            key: Dot-separated key path (e.g., 'llm.provider')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded")

        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = None
        self._load_config()


class _NestedConfigAccessor:
    """
    Helper class for accessing nested configuration values using dot notation.
    """

    def __init__(self, data: Dict[str, Any]):
        self._data = data

    def __getattr__(self, name: str) -> Any:
        if name not in self._data:
            raise AttributeError(f"Configuration key '{name}' not found")

        value = self._data[name]
        if isinstance(value, dict):
            return _NestedConfigAccessor(value)
        return value


# Global configuration instance
config = ConfigManager()
