"""
NeoMate AI Helpers Module

This module provides a collection of reusable utility functions for common operations
across the NeoMate AI application. These functions help reduce code duplication and
ensure consistent behavior throughout the project.

Features:
- Project root detection for dynamic path resolution
- JSON file handling with error logging
- Directory creation utilities
- Extensible for future common operations

All functions include proper error handling and logging for robust operation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from src.utils.logger import logger


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.

    This function dynamically determines the project root (NeoMate-AI/) by traversing
    up from the current file's location. It works reliably from any subdirectory
    within the project.

    Returns:
        Path: Absolute path to the project root directory.

    Example:
        >>> root = get_project_root()
        >>> config_path = root / "config" / "settings.yaml"
    """
    # Navigate up from src/utils/helpers.py to project root
    # __file__ -> src/utils/ -> src/ -> NeoMate-AI/
    current_file = Path(__file__)
    return current_file.parent.parent.parent


def load_json(file_path: Union[str, Path]) -> Optional[Union[Dict[str, Any], List[Any]]]:
    """
    Load and parse a JSON file.

    Args:
        file_path: Path to the JSON file (string or Path object).

    Returns:
        Parsed JSON data as a dict or list, or None if loading fails.

    Raises:
        Logs errors for FileNotFoundError and JSONDecodeError but doesn't raise exceptions.

    Example:
        >>> data = load_json("config/settings.json")
        >>> if data:
        ...     print(data["key"])
    """
    file_path = Path(file_path)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            logger.debug(f"Successfully loaded JSON from {file_path}")
            return data

    except FileNotFoundError:
        logger.error(f"JSON file not found: {file_path}")
        return None

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format in {file_path}: {e}")
        return None

    except PermissionError as e:
        logger.error(f"Permission denied reading {file_path}: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error loading JSON from {file_path}: {e}")
        return None


def save_json(data: Union[Dict[str, Any], List[Any]], file_path: Union[str, Path]) -> bool:
    """
    Save data to a JSON file with pretty formatting.

    Args:
        data: Python object (dict or list) to save.
        file_path: Path where to save the JSON file.

    Returns:
        True if save was successful, False otherwise.

    Example:
        >>> data = {"key": "value"}
        >>> success = save_json(data, "output/data.json")
    """
    file_path = Path(file_path)

    try:
        # Ensure parent directory exists
        ensure_directory_exists(file_path.parent)

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
            logger.debug(f"Successfully saved JSON to {file_path}")
            return True

    except TypeError as e:
        logger.error(f"Data is not JSON serializable: {e}")
        return False

    except PermissionError as e:
        logger.error(f"Permission denied writing to {file_path}: {e}")
        return False

    except Exception as e:
        logger.error(f"Unexpected error saving JSON to {file_path}: {e}")
        return False


def ensure_directory_exists(directory_path: Union[str, Path]) -> None:
    """
    Ensure that a directory exists, creating it and parents if necessary.

    Args:
        directory_path: Path to the directory to create.

    Example:
        >>> ensure_directory_exists("logs")
        >>> ensure_directory_exists("data/cache/subdir")
    """
    directory_path = Path(directory_path)

    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        if not directory_path.exists():
            logger.warning(f"Failed to create directory: {directory_path}")
        else:
            logger.debug(f"Directory ensured: {directory_path}")

    except PermissionError as e:
        logger.error(f"Permission denied creating directory {directory_path}: {e}")

    except Exception as e:
        logger.error(f"Unexpected error creating directory {directory_path}: {e}")


# Export functions for easy importing
__all__ = [
    "get_project_root",
    "load_json",
    "save_json",
    "ensure_directory_exists"
]
