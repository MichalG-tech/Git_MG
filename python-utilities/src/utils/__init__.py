"""
Utilities
Shared helper functions used across all powerbi-utilities modules.

Provides:
  - Structured logging with consistent formatting
  - Configuration loading with validation
  - Environment variable management
  - File system helpers for TMDL model navigation
  - Result formatting for CI/CD output
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


__all__ = [
    "get_logger",
    "load_config",
    "get_env",
    "find_tmdl_files",
    "find_model_directories",
    "format_result",
    "print_summary",
]


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Return a consistently-formatted logger for the given module name.

    All loggers share the same format: ISO timestamp | level | module | message.

    Args:
        name: Logger name — use __name__ in calling modules.
        level: Logging level (default: INFO).
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        ))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def load_config(config_path: str, required_keys: Optional[List[str]] = None) -> Dict:
    """Load and validate a JSON configuration file.

    Args:
        config_path: Path to the JSON configuration file.
        required_keys: If provided, raises KeyError if any key is missing.

    Returns:
        Parsed configuration dictionary.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(path, encoding="utf-8") as f:
        config = json.load(f)
    if required_keys:
        missing = [k for k in required_keys if k not in config]
        if missing:
            raise KeyError(f"Missing required config keys: {missing}")
    return config


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """Read an environment variable with optional default and required enforcement.

    Args:
        key: Environment variable name.
        default: Default value if the variable is not set.
        required: If True, raises EnvironmentError when the variable is missing.

    Returns:
        The variable value as a string, or None if not set and not required.
    """
    value = os.environ.get(key, default)
    if required and value is None:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Set it in your .env file or CI/CD secrets."
        )
    return value


def find_tmdl_files(root_dir: str, pattern: str = "**/*.tmdl") -> List[Path]:
    """Recursively find all TMDL files under a directory."""
    return sorted(Path(root_dir).glob(pattern))


def find_model_directories(models_root: str = "semantic-models") -> List[Path]:
    """Return model root directories (those containing definition/model.tmdl)."""
    return [p.parent.parent for p in Path(models_root).rglob("definition/model.tmdl")]


def format_result(task: str, status: str, details: Optional[Dict] = None) -> Dict:
    """Create a standardised result dictionary for CI/CD reporting.

    Args:
        task: Short task description (e.g. "TMDL Validation").
        status: Outcome string ("success", "failure", "warning").
        details: Optional extra key-value pairs to include.

    Returns:
        Dict with task, status, timestamp, and any extra detail keys.
    """
    result: Dict[str, Any] = {
        "task":      task,
        "status":    status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if details:
        result.update(details)
    return result


def print_summary(results: List[Dict], title: str = "Run Summary") -> None:
    """Print a formatted summary table of task results to stdout."""
    width = 70
    print("=" * width)
    print(f" {title}")
    print("=" * width)
    passed = sum(1 for r in results if r.get("status") == "success")
    for r in results:
        icon = "[OK]  " if r.get("status") == "success" else "[FAIL]"
        print(f"  {icon}  {r.get('task', 'Unknown')}")
    print("-" * width)
    print(f"  Total: {len(results)}  |  Passed: {passed}  |  Failed: {len(results) - passed}")
    print("=" * width)
