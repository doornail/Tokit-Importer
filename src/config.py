"""Configuration management."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""

    # Anthropic
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    # NYTimes
    NYTIMES_EMAIL: Optional[str] = os.getenv("NYTIMES_EMAIL")
    NYTIMES_PASSWORD: Optional[str] = os.getenv("NYTIMES_PASSWORD")

    # Cooknjoy
    COOKNJOY_EMAIL: str = os.getenv("COOKNJOY_EMAIL", "")
    COOKNJOY_PASSWORD: str = os.getenv("COOKNJOY_PASSWORD", "")
    COOKNJOY_URL: str = os.getenv("COOKNJOY_URL", "https://cooknjoy.com")

    # General
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "./recipes")

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        errors = []

        if not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")

        if not cls.COOKNJOY_EMAIL or not cls.COOKNJOY_PASSWORD:
            errors.append("COOKNJOY_EMAIL and COOKNJOY_PASSWORD are required for upload")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


config = Config()
