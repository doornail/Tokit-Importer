"""NYTimes Cooking recipe scraper."""

import json
import re
from typing import Optional
import requests
from bs4 import BeautifulSoup

from ..models import Recipe, Ingredient, RecipeStep
from .base import RecipeScraper


class NYTimesScraper(RecipeScraper):
    """Scraper for NYTimes Cooking recipes."""

    def __init__(self):
        self.base_url = "https://cooking.nytimes.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def can_scrape(self, url: str) -> bool:
        """Check if URL is from NYTimes Cooking."""
        return 'cooking.nytimes.com' in url

    def scrape(self, url: str) -> Recipe:
        """Scrape a recipe from NYTimes Cooking."""
        response = self.session.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'lxml')

        # Try to extract recipe from JSON-LD structured data
        recipe_data = self._extract_json_ld(soup)

        if recipe_data:
            return self._parse_json_ld(recipe_data, url)

        # Fallback to HTML parsing
        return self._parse_html(soup, url)

    def _extract_json_ld(self, soup: BeautifulSoup) -> Optional[dict]:
        """Extract recipe data from JSON-LD structured data."""
        scripts = soup.find_all('script', type='application/ld+json')

        for script in scripts:
            try:
                data = json.loads(script.string)

                # Handle arrays of JSON-LD objects
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'Recipe':
                            return item
                elif data.get('@type') == 'Recipe':
                    return data
            except (json.JSONDecodeError, AttributeError):
                continue

        return None

    def _parse_json_ld(self, data: dict, url: str) -> Recipe:
        """Parse recipe from JSON-LD structured data."""
        # Parse ingredients
        ingredients = []
        for ing_text in data.get('recipeIngredient', []):
            ingredients.append(self._parse_ingredient(ing_text))

        # Parse steps
        steps = []
        instructions = data.get('recipeInstructions', [])

        for idx, instruction in enumerate(instructions, 1):
            if isinstance(instruction, dict):
                text = instruction.get('text', '')
            else:
                text = str(instruction)

            if text.strip():
                steps.append(RecipeStep(
                    step_number=idx,
                    instruction=text.strip()
                ))

        # Extract times
        prep_time = self._parse_duration(data.get('prepTime'))
        cook_time = self._parse_duration(data.get('cookTime'))
        total_time = self._parse_duration(data.get('totalTime'))

        # Extract yield/servings
        recipe_yield = data.get('recipeYield')
        servings = None
        if recipe_yield:
            if isinstance(recipe_yield, list):
                servings = recipe_yield[0] if recipe_yield else None
            else:
                servings = str(recipe_yield)

        return Recipe(
            title=data.get('name', 'Untitled Recipe'),
            description=data.get('description'),
            source_url=url,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time,
            total_time=total_time,
            ingredients=ingredients,
            steps=steps,
            author=self._extract_author(data),
            tags=data.get('recipeCategory', []) if isinstance(data.get('recipeCategory'), list) else []
        )

    def _parse_html(self, soup: BeautifulSoup, url: str) -> Recipe:
        """Fallback HTML parsing when JSON-LD is not available."""
        title_elem = soup.find('h1', class_=re.compile('recipe.*title', re.I))
        title = title_elem.get_text(strip=True) if title_elem else 'Untitled Recipe'

        description_elem = soup.find('meta', attrs={'name': 'description'})
        description = description_elem.get('content') if description_elem else None

        # Parse ingredients
        ingredients = []
        ing_elements = soup.find_all(['li', 'span'], class_=re.compile('ingredient', re.I))

        for ing_elem in ing_elements:
            ing_text = ing_elem.get_text(strip=True)
            if ing_text:
                ingredients.append(self._parse_ingredient(ing_text))

        # Parse steps
        steps = []
        step_elements = soup.find_all(['li', 'div', 'p'], class_=re.compile('preparation.*step|instruction', re.I))

        for idx, step_elem in enumerate(step_elements, 1):
            instruction = step_elem.get_text(strip=True)
            if instruction:
                steps.append(RecipeStep(
                    step_number=idx,
                    instruction=instruction
                ))

        return Recipe(
            title=title,
            description=description,
            source_url=url,
            ingredients=ingredients,
            steps=steps
        )

    def _parse_ingredient(self, text: str) -> Ingredient:
        """Parse an ingredient string into structured data."""
        # Simple parsing - quantity, unit, item
        # This is a basic implementation and could be enhanced
        text = text.strip()

        # Try to extract quantity (numbers, fractions)
        quantity_match = re.match(r'^([\d\s\/\.\-½¼¾⅓⅔⅛⅜⅝⅞]+)\s*', text)
        quantity = None
        remainder = text

        if quantity_match:
            quantity = quantity_match.group(1).strip()
            remainder = text[len(quantity):].strip()

        # Common units
        units = [
            'cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp',
            'pound', 'pounds', 'lb', 'lbs', 'ounce', 'ounces', 'oz',
            'gram', 'grams', 'g', 'kilogram', 'kilograms', 'kg',
            'milliliter', 'milliliters', 'ml', 'liter', 'liters', 'l',
            'pinch', 'dash', 'clove', 'cloves', 'can', 'cans', 'package', 'packages'
        ]

        unit = None
        item = remainder

        for u in units:
            pattern = rf'^({u})\b\s*'
            match = re.match(pattern, remainder, re.IGNORECASE)
            if match:
                unit = match.group(1)
                item = remainder[len(unit):].strip()
                break

        return Ingredient(
            quantity=quantity,
            unit=unit,
            item=item
        )

    def _parse_duration(self, duration_str: Optional[str]) -> Optional[str]:
        """Parse ISO 8601 duration to human-readable format."""
        if not duration_str:
            return None

        # Parse PT format (e.g., PT30M, PT1H30M)
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0

            parts = []
            if hours:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

            return " ".join(parts) if parts else None

        return duration_str

    def _extract_author(self, data: dict) -> Optional[str]:
        """Extract author name from JSON-LD data."""
        author = data.get('author')
        if not author:
            return None

        if isinstance(author, dict):
            return author.get('name')
        elif isinstance(author, list) and author:
            first_author = author[0]
            if isinstance(first_author, dict):
                return first_author.get('name')
            return str(first_author)

        return str(author)
