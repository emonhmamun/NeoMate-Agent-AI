"""
NeoMate AI Helpers Module

This module provides a comprehensive collection of utility functions and constants
used across the NeoMate AI project. It serves as a central toolbox for common tasks
such as path management, data manipulation, validation, and cross-cutting concerns.

Features:
- Project root path detection and path utilities
- Data manipulation and merging functions
- Validation and type checking helpers
- File system operations
- Configuration utilities
- Error handling decorators
- Performance monitoring helpers

Author: NeoMate AI Team
Version: 1.0.0
License: MIT
"""

import functools
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, TypeVar
from datetime import datetime

T = TypeVar('T')


def get_project_root() -> Path:
    """
    Get the absolute path to the project root directory.

    This function determines the project root by navigating up from the current file's location.
    Since this file is located at src/utils/helpers.py, we go up two levels to reach the root.

    Returns:
        Path: Absolute path to the project root directory (NeoMate-AI/)

    Raises:
        RuntimeError: If the project structure is invalid and root cannot be determined
    """
    try:
        root = Path(__file__).resolve().parents[2]
        if not root.exists():
            raise RuntimeError(f"Project root directory does not exist: {root}")
        return root
    except Exception as e:
        raise RuntimeError(f"Failed to determine project root: {e}")


def merge_dicts(base: Dict[str, Any], update: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
    """
    Merge two dictionaries recursively.

    Args:
        base: Base dictionary
        update: Dictionary with updates
        deep: Whether to perform deep merge (default: True)

    Returns:
        Dict[str, Any]: Merged dictionary
    """
    if not deep:
        return {**base, **update}

    result = base.copy()
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value, deep=True)
        else:
            result[key] = value
    return result


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure

    Returns:
        Path: Path object of the ensured directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value using dot notation.

    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., 'application.name')
        default: Default value if key not found

    Returns:
        Any: Value at key path or default
    """
    keys = key_path.split('.')
    current = data

    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default


def validate_config(config: Dict[str, Any], required_keys: List[str]) -> List[str]:
    """
    Validate configuration dictionary for required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required key paths (dot notation supported)

    Returns:
        List[str]: List of missing keys
    """
    missing = []
    for key_path in required_keys:
        if safe_get(config, key_path) is None:
            missing.append(key_path)
    return missing


def timing_decorator(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to measure and log function execution time.

    Args:
        func: Function to decorate

    Returns:
        Callable: Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Function {func.__name__} failed after {execution_time:.4f} seconds: {e}")
            raise
    return wrapper


def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string.

    Args:
        format_str: Timestamp format (default: ISO-like format)

    Returns:
        str: Formatted timestamp
    """
    return datetime.now().strftime(format_str)


def is_valid_path(path: Union[str, Path]) -> bool:
    """
    Check if a path exists and is accessible.

    Args:
        path: Path to check

    Returns:
        bool: True if path exists and is accessible
    """
    try:
        return Path(path).exists()
    except (OSError, ValueError):
        return False


# Global constants
PROJECT_ROOT = get_project_root()
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
EXTERNAL_DIR = PROJECT_ROOT / "external"


if __name__ == "__main__":
    # Test the helpers functionality
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Config Dir: {CONFIG_DIR}")
    print(f"Data Dir: {DATA_DIR}")
    print(f"Logs Dir: {LOGS_DIR}")

    # Test merge_dicts
    base = {"app": {"name": "NeoMate", "version": "1.0"}}
    update = {"app": {"version": "1.1"}, "new_key": "value"}
    merged = merge_dicts(base, update)
    print(f"Merged dict: {merged}")

    # Test safe_get
    test_data = {"level1": {"level2": "value"}}
    print(f"Safe get result: {safe_get(test_data, 'level1.level2', 'default')}")

    # Test timestamp
    print(f"Current timestamp: {get_timestamp()}")
