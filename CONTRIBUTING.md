# Contributing to Tokit Omnicook Recipe Importer

Thank you for your interest in contributing!

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install Playwright browsers: `playwright install`
4. Copy `.env.example` to `.env` and configure your credentials

## Adding New Recipe Sources

To add support for a new recipe website:

1. Create a new scraper in `src/scrapers/` (e.g., `allrecipes.py`)
2. Inherit from `RecipeScraper` base class
3. Implement the required methods:
   - `can_scrape(url)`: Check if the scraper supports the URL
   - `scrape(url)`: Extract recipe data and return a `Recipe` object

4. Register your scraper in `src/scrapers/base.py` in the `get_scraper()` method

Example:

```python
from .base import RecipeScraper
from ..models import Recipe, Ingredient, RecipeStep

class AllRecipesScraper(RecipeScraper):
    def can_scrape(self, url: str) -> bool:
        return 'allrecipes.com' in url

    def scrape(self, url: str) -> Recipe:
        # Implement scraping logic
        pass
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to classes and methods
- Keep functions focused and small

## Testing

Before submitting a PR:

1. Test your scraper with multiple recipes
2. Verify the Claude conversion works correctly
3. Test the upload process (use `--dry-run` flag)

## Submitting Changes

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request with a clear description

## Areas for Contribution

- **New Scrapers**: Support for more recipe websites
- **Enhanced Conversion**: Improve Claude prompts for better Omnicook formatting
- **UI Improvements**: Better CLI output and error messages
- **Testing**: Add unit and integration tests
- **Documentation**: Improve docs and examples

## Questions?

Open an issue for discussion before starting major changes.
