"""Recipe scrapers for various sources."""

from .base import RecipeScraper
from .nytimes import NYTimesScraper

__all__ = ["RecipeScraper", "NYTimesScraper"]
