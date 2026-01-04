#!/usr/bin/env python3
"""
Example programmatic usage of the Tokit Importer library.

This demonstrates how to use the library components directly in your own code.
"""

from src.scrapers import NYTimesScraper
from src.converters import ClaudeConverter
from src.uploaders import upload_recipe_sync


def example_scrape_and_convert():
    """Example: Scrape and convert a recipe without uploading."""

    # Step 1: Scrape a recipe
    url = "https://cooking.nytimes.com/recipes/YOUR-RECIPE-ID"

    scraper = NYTimesScraper()
    recipe = scraper.scrape(url)

    print(f"Scraped: {recipe.title}")
    print(f"Ingredients: {len(recipe.ingredients)}")
    print(f"Steps: {len(recipe.steps)}")

    # Step 2: Convert to Omnicook format
    converter = ClaudeConverter()
    omnicook_recipe = converter.convert(recipe)

    print(f"\nConverted Recipe:")
    print(f"Name: {omnicook_recipe.name}")
    print(f"Servings: {omnicook_recipe.servings}")
    print(f"Total Time: {omnicook_recipe.total_time_minutes} minutes")
    print(f"Difficulty: {omnicook_recipe.difficulty}")

    return omnicook_recipe


def example_full_workflow():
    """Example: Complete workflow from scrape to upload."""

    # Scrape
    url = "https://cooking.nytimes.com/recipes/YOUR-RECIPE-ID"
    scraper = NYTimesScraper()
    recipe = scraper.scrape(url)

    # Convert
    converter = ClaudeConverter()
    omnicook_recipe = converter.convert(recipe)

    # Upload (use dry_run=True to test without actually uploading)
    success = upload_recipe_sync(omnicook_recipe, dry_run=True)

    if success:
        print("Recipe successfully processed!")
    else:
        print("Upload failed")


def example_async_upload():
    """Example: Using the async uploader directly."""
    import asyncio
    from src.uploaders import CooknjoyUploader
    from src.models import OmnicookRecipe

    async def upload_example():
        # Create a sample recipe
        recipe = OmnicookRecipe(
            name="Test Recipe",
            description="A test recipe",
            servings=4,
            ingredients=["2 cups flour", "1 cup sugar", "3 eggs"],
            steps=[
                "Mix dry ingredients",
                "Add wet ingredients",
                "Bake at 350°F for 30 minutes"
            ],
            total_time_minutes=45,
            difficulty="Easy",
            category="Dessert"
        )

        # Upload using async context manager
        async with CooknjoyUploader(headless=False) as uploader:
            await uploader.login()
            await uploader.upload_recipe(recipe, dry_run=True)

    asyncio.run(upload_example())


if __name__ == '__main__':
    print("Running example: Scrape and Convert")
    print("=" * 50)

    # Uncomment the example you want to run:
    # example_scrape_and_convert()
    # example_full_workflow()
    # example_async_upload()

    print("\nTo run these examples:")
    print("1. Set up your .env file with API keys")
    print("2. Uncomment the example function you want to run")
    print("3. Replace 'YOUR-RECIPE-ID' with an actual recipe URL")
