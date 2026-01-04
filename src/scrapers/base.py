"""Base recipe scraper interface."""

from abc import ABC, abstractmethod
from typing import Optional
from ..models import Recipe


class RecipeScraper(ABC):
    """Abstract base class for recipe scrapers."""

    @abstractmethod
    def can_scrape(self, url: str) -> bool:
        """Check if this scraper can handle the given URL."""
        pass

    @abstractmethod
    def scrape(self, url: str) -> Recipe:
        """Scrape a recipe from the given URL."""
        pass

    @classmethod
    def get_scraper(cls, url: str) -> Optional['RecipeScraper']:
        """Get the appropriate scraper for a URL."""
        from .nytimes import NYTimesScraper

        scrapers = [NYTimesScraper()]

        for scraper in scrapers:
            if scraper.can_scrape(url):
                return scraper

        return None
