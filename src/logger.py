"""Logging utilities."""

import logging
import sys
from typing import Optional
from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Setup a logger with rich formatting."""
    if level is None:
        try:
            from .config import config
            level = "DEBUG" if config.DEBUG else "INFO"
        except ImportError:
            level = "INFO"

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Add rich handler
    handler = RichHandler(
        console=console,
        show_time=True,
        show_path=False,
        rich_tracebacks=True
    )

    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get or create a logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
