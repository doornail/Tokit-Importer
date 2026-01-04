"""Cooknjoy web interface automation."""

import asyncio
import time
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PlaywrightTimeoutError

from ..models import OmnicookRecipe
from ..config import config


class CooknjoyUploader:
    """Automates recipe upload to Cooknjoy web interface."""

    def __init__(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        headless: bool = True
    ):
        """Initialize the uploader."""
        self.email = email or config.COOKNJOY_EMAIL
        self.password = password or config.COOKNJOY_PASSWORD
        self.base_url = base_url or config.COOKNJOY_URL
        self.headless = headless

        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the browser session."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()

    async def close(self):
        """Close the browser session."""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def login(self) -> bool:
        """Login to Cooknjoy."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            # Navigate to login page
            await self.page.goto(f"{self.base_url}/login", wait_until="networkidle")

            # Wait for login form
            await self.page.wait_for_selector('input[type="email"], input[name="email"], input[id="email"]', timeout=10000)

            # Fill in credentials
            # Try different common selectors for email/password fields
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[id="email"]',
                'input[placeholder*="email" i]'
            ]

            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id="password"]'
            ]

            # Fill email
            for selector in email_selectors:
                try:
                    await self.page.fill(selector, self.email, timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue

            # Fill password
            for selector in password_selectors:
                try:
                    await self.page.fill(selector, self.password, timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue

            # Submit form
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                'button:has-text("Login")'
            ]

            for selector in submit_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue

            # Wait for navigation after login
            await self.page.wait_for_load_state("networkidle", timeout=15000)

            # Check if login was successful by looking for common logged-in indicators
            # This is a heuristic - adjust based on actual Cooknjoy UI
            await asyncio.sleep(2)  # Give time for redirect

            current_url = self.page.url
            if '/login' not in current_url.lower():
                return True

            return False

        except Exception as e:
            print(f"Login failed: {e}")
            return False

    async def upload_recipe(self, recipe: OmnicookRecipe, dry_run: bool = False) -> bool:
        """Upload a recipe to Cooknjoy."""
        if dry_run:
            print(f"DRY RUN: Would upload recipe '{recipe.name}'")
            return True

        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")

        try:
            # Navigate to recipe creation page
            # This is a generic approach - adjust based on actual Cooknjoy UI
            create_urls = [
                f"{self.base_url}/recipes/new",
                f"{self.base_url}/recipe/new",
                f"{self.base_url}/new-recipe",
                f"{self.base_url}/create-recipe"
            ]

            # Try to find the recipe creation page
            for url in create_urls:
                try:
                    await self.page.goto(url, wait_until="networkidle", timeout=10000)
                    # If we didn't get a 404, assume this is the right page
                    break
                except Exception:
                    continue

            # Alternatively, look for a "Create Recipe" or "New Recipe" button
            try:
                new_recipe_selectors = [
                    'a:has-text("New Recipe")',
                    'a:has-text("Create Recipe")',
                    'a:has-text("Add Recipe")',
                    'button:has-text("New Recipe")',
                    'button:has-text("Create Recipe")'
                ]

                for selector in new_recipe_selectors:
                    try:
                        await self.page.click(selector, timeout=2000)
                        await self.page.wait_for_load_state("networkidle")
                        break
                    except PlaywrightTimeoutError:
                        continue
            except Exception:
                pass

            # Fill in recipe details
            # These are generic selectors - adjust based on actual form structure
            await self._fill_recipe_form(recipe)

            # Submit the form
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Save")',
                'button:has-text("Create")',
                'button:has-text("Add Recipe")',
                'button:has-text("Submit")'
            ]

            for selector in submit_selectors:
                try:
                    await self.page.click(selector, timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue

            # Wait for success
            await self.page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)

            return True

        except Exception as e:
            print(f"Upload failed: {e}")
            if config.DEBUG:
                # Take screenshot for debugging
                await self.page.screenshot(path=f"upload_error_{int(time.time())}.png")
            return False

    async def _fill_recipe_form(self, recipe: OmnicookRecipe):
        """Fill in the recipe form fields."""
        # Recipe name/title
        name_selectors = [
            'input[name="name"]',
            'input[name="title"]',
            'input[id="name"]',
            'input[id="title"]',
            'input[placeholder*="name" i]',
            'input[placeholder*="title" i]'
        ]

        for selector in name_selectors:
            try:
                await self.page.fill(selector, recipe.name, timeout=2000)
                break
            except PlaywrightTimeoutError:
                continue

        # Description
        desc_selectors = [
            'textarea[name="description"]',
            'textarea[id="description"]',
            'input[name="description"]',
            'textarea[placeholder*="description" i]'
        ]

        if recipe.description:
            for selector in desc_selectors:
                try:
                    await self.page.fill(selector, recipe.description, timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue

        # Servings
        servings_selectors = [
            'input[name="servings"]',
            'input[id="servings"]',
            'input[type="number"]'
        ]

        for selector in servings_selectors:
            try:
                await self.page.fill(selector, str(recipe.servings), timeout=2000)
                break
            except PlaywrightTimeoutError:
                continue

        # Ingredients
        # This is tricky as different sites have different UIs
        # Common patterns: textarea, multiple input fields, or a rich editor
        ingredients_text = "\n".join(recipe.ingredients)

        ingredients_selectors = [
            'textarea[name="ingredients"]',
            'textarea[id="ingredients"]',
            'textarea[placeholder*="ingredients" i]',
            '#ingredients',
            '[data-field="ingredients"]'
        ]

        for selector in ingredients_selectors:
            try:
                await self.page.fill(selector, ingredients_text, timeout=2000)
                break
            except PlaywrightTimeoutError:
                continue

        # Instructions/Steps
        steps_text = "\n\n".join([
            f"Step {i+1}: {step}"
            for i, step in enumerate(recipe.steps)
        ])

        steps_selectors = [
            'textarea[name="instructions"]',
            'textarea[id="instructions"]',
            'textarea[name="steps"]',
            'textarea[id="steps"]',
            'textarea[placeholder*="instructions" i]',
            'textarea[placeholder*="steps" i]',
            '#instructions',
            '[data-field="instructions"]'
        ]

        for selector in steps_selectors:
            try:
                await self.page.fill(selector, steps_text, timeout=2000)
                break
            except PlaywrightTimeoutError:
                continue

        # Additional fields if available
        if recipe.total_time_minutes:
            time_selectors = [
                'input[name="time"]',
                'input[name="total_time"]',
                'input[id="time"]',
                'input[placeholder*="time" i]'
            ]

            for selector in time_selectors:
                try:
                    await self.page.fill(selector, str(recipe.total_time_minutes), timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue

        if recipe.difficulty:
            # Try to find difficulty dropdown or radio buttons
            try:
                difficulty_selector = 'select[name="difficulty"], select[id="difficulty"]'
                await self.page.select_option(difficulty_selector, recipe.difficulty, timeout=2000)
            except PlaywrightTimeoutError:
                pass

        if recipe.category:
            # Try to find category dropdown or input
            try:
                category_selectors = [
                    'select[name="category"]',
                    'select[id="category"]',
                    'input[name="category"]',
                    'input[id="category"]'
                ]

                for selector in category_selectors:
                    try:
                        if 'select' in selector:
                            await self.page.select_option(selector, recipe.category, timeout=2000)
                        else:
                            await self.page.fill(selector, recipe.category, timeout=2000)
                        break
                    except PlaywrightTimeoutError:
                        continue
            except Exception:
                pass

        # Notes
        if recipe.notes:
            notes_selectors = [
                'textarea[name="notes"]',
                'textarea[id="notes"]',
                'input[name="notes"]'
            ]

            for selector in notes_selectors:
                try:
                    await self.page.fill(selector, recipe.notes, timeout=2000)
                    break
                except PlaywrightTimeoutError:
                    continue


def upload_recipe_sync(recipe: OmnicookRecipe, dry_run: bool = False) -> bool:
    """Synchronous wrapper for recipe upload."""
    async def _upload():
        async with CooknjoyUploader() as uploader:
            if not dry_run:
                logged_in = await uploader.login()
                if not logged_in:
                    print("Failed to login to Cooknjoy")
                    return False

            return await uploader.upload_recipe(recipe, dry_run=dry_run)

    return asyncio.run(_upload())
