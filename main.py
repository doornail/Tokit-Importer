#!/usr/bin/env python3
"""
Tokit Omnicook Recipe Importer - Main CLI Application

Imports recipes from various sources and converts them for use in Tokit Omnicook.
"""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config import config
from src.logger import get_logger, console
from src.models import Recipe, OmnicookRecipe
from src.scrapers import RecipeScraper
from src.converters import ClaudeConverter
from src.uploaders import upload_recipe_sync

logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Tokit Omnicook Recipe Importer - Convert and import recipes automatically."""
    pass


@cli.command()
@click.option(
    '--url',
    '-u',
    required=True,
    help='URL of the recipe to import'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Convert recipe but do not upload to Cooknjoy'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Directory to save converted recipe JSON (default: ./recipes)'
)
@click.option(
    '--no-upload',
    is_flag=True,
    help='Skip upload to Cooknjoy (only scrape and convert)'
)
def import_recipe(url: str, dry_run: bool, output: Optional[str], no_upload: bool):
    """Import a single recipe from a URL."""
    try:
        # Validate configuration
        config.validate()

        console.print(Panel.fit(
            f"[bold cyan]Importing Recipe[/bold cyan]\n\n"
            f"URL: {url}\n"
            f"Mode: {'DRY RUN' if dry_run else 'LIVE'}",
            border_style="cyan"
        ))

        # Step 1: Scrape recipe
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scraping recipe...", total=None)

            scraper = RecipeScraper.get_scraper(url)
            if not scraper:
                console.print("[red]✗[/red] No scraper available for this URL")
                console.print(f"Supported sources: NYTimes Cooking (cooking.nytimes.com)")
                sys.exit(1)

            recipe = scraper.scrape(url)
            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Scraped: {recipe.title}")

        # Step 2: Convert with Claude
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Converting recipe with Claude AI...", total=None)

            converter = ClaudeConverter()
            omnicook_recipe = converter.convert(recipe)

            progress.update(task, completed=True)
            console.print(f"[green]✓[/green] Converted to Omnicook format")

        # Display converted recipe
        _display_recipe(omnicook_recipe)

        # Step 3: Save to file if requested
        if output:
            output_dir = Path(output)
        else:
            output_dir = Path(config.OUTPUT_DIR)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        safe_filename = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in omnicook_recipe.name
        )
        output_file = output_dir / f"{safe_filename}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(omnicook_recipe.model_dump(), f, indent=2, ensure_ascii=False)

        console.print(f"[green]✓[/green] Saved to: {output_file}")

        # Step 4: Upload to Cooknjoy
        if not no_upload:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Uploading to Cooknjoy...", total=None)

                success = upload_recipe_sync(omnicook_recipe, dry_run=dry_run)

                progress.update(task, completed=True)

                if success:
                    if dry_run:
                        console.print("[yellow]✓[/yellow] Dry run successful (not actually uploaded)")
                    else:
                        console.print("[green]✓[/green] Successfully uploaded to Cooknjoy")
                else:
                    console.print("[red]✗[/red] Upload failed")
                    sys.exit(1)

        console.print("\n[bold green]Import completed successfully![/bold green]")

    except ValueError as e:
        console.print(f"[red]Configuration error:[/red] {e}")
        console.print("\nPlease check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        if config.DEBUG:
            logger.exception("Full error details:")
        sys.exit(1)


@cli.command()
@click.option(
    '--file',
    '-f',
    type=click.Path(exists=True),
    required=True,
    help='File containing URLs (one per line)'
)
@click.option(
    '--dry-run',
    is_flag=True,
    help='Convert recipes but do not upload to Cooknjoy'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Directory to save converted recipe JSONs'
)
def batch(file: str, dry_run: bool, output: Optional[str]):
    """Import multiple recipes from a file containing URLs."""
    try:
        config.validate()

        # Read URLs
        with open(file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        console.print(Panel.fit(
            f"[bold cyan]Batch Import[/bold cyan]\n\n"
            f"Recipes: {len(urls)}\n"
            f"Mode: {'DRY RUN' if dry_run else 'LIVE'}",
            border_style="cyan"
        ))

        success_count = 0
        fail_count = 0

        for idx, url in enumerate(urls, 1):
            console.print(f"\n[bold]Recipe {idx}/{len(urls)}[/bold]")

            try:
                # Import recipe
                scraper = RecipeScraper.get_scraper(url)
                if not scraper:
                    console.print(f"[yellow]⊘[/yellow] Skipping unsupported URL: {url}")
                    fail_count += 1
                    continue

                recipe = scraper.scrape(url)
                console.print(f"[green]✓[/green] Scraped: {recipe.title}")

                converter = ClaudeConverter()
                omnicook_recipe = converter.convert(recipe)
                console.print(f"[green]✓[/green] Converted")

                # Save
                if output:
                    output_dir = Path(output)
                else:
                    output_dir = Path(config.OUTPUT_DIR)

                output_dir.mkdir(parents=True, exist_ok=True)

                safe_filename = "".join(
                    c if c.isalnum() or c in (' ', '-', '_') else '_'
                    for c in omnicook_recipe.name
                )
                output_file = output_dir / f"{safe_filename}.json"

                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(omnicook_recipe.model_dump(), f, indent=2, ensure_ascii=False)

                # Upload
                success = upload_recipe_sync(omnicook_recipe, dry_run=dry_run)

                if success:
                    console.print(f"[green]✓[/green] Uploaded")
                    success_count += 1
                else:
                    console.print(f"[red]✗[/red] Upload failed")
                    fail_count += 1

            except Exception as e:
                console.print(f"[red]✗[/red] Failed: {e}")
                fail_count += 1
                if config.DEBUG:
                    logger.exception("Error details:")

        # Summary
        console.print(f"\n[bold]Batch Import Summary[/bold]")
        console.print(f"Success: [green]{success_count}[/green]")
        console.print(f"Failed: [red]{fail_count}[/red]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument('recipe_file', type=click.Path(exists=True))
def show(recipe_file: str):
    """Display a saved recipe JSON file."""
    try:
        with open(recipe_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        recipe = OmnicookRecipe(**data)
        _display_recipe(recipe)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


def _display_recipe(recipe: OmnicookRecipe):
    """Display a recipe in a nice format."""
    # Recipe header
    header = f"[bold cyan]{recipe.name}[/bold cyan]"
    if recipe.description:
        header += f"\n{recipe.description}"

    info_parts = []
    if recipe.servings:
        info_parts.append(f"Servings: {recipe.servings}")
    if recipe.total_time_minutes:
        info_parts.append(f"Time: {recipe.total_time_minutes} min")
    if recipe.difficulty:
        info_parts.append(f"Difficulty: {recipe.difficulty}")
    if recipe.category:
        info_parts.append(f"Category: {recipe.category}")

    if info_parts:
        header += f"\n[dim]{' | '.join(info_parts)}[/dim]"

    console.print(Panel(header, border_style="cyan"))

    # Ingredients
    if recipe.ingredients:
        console.print("\n[bold yellow]Ingredients:[/bold yellow]")
        for ing in recipe.ingredients:
            # Handle both old string format and new OmnicookIngredient objects
            if hasattr(ing, 'name'):
                console.print(f"  • {ing.quantity} {ing.name}")
            else:
                console.print(f"  • {ing}")

    # Steps with detailed parameters
    if recipe.steps:
        console.print("\n[bold yellow]Tokit Omnicook Steps:[/bold yellow]")
        for step in recipe.steps:
            # Handle both old string format and new OmnicookStep objects
            if hasattr(step, 'parameters'):
                params = step.parameters
                console.print(f"\n  [bold cyan]Step {step.step_number}:[/bold cyan] {step.description}")

                # Display parameters in a compact format
                param_parts = []

                # Time
                if params.duration_minutes > 0 or params.duration_seconds > 0:
                    time_str = f"{params.duration_minutes}:{params.duration_seconds:02d}"
                    param_parts.append(f"⏱️  {time_str}")

                # Temperature
                if params.temperature_on:
                    param_parts.append(f"🌡️  {params.temperature_celsius}°C")
                else:
                    param_parts.append("🌡️  OFF")

                # Speed
                if params.speed > 0:
                    param_parts.append(f"🔄 {params.speed} (chop/blend)")
                elif params.speed < 0:
                    param_parts.append(f"🔄 {abs(params.speed)} reverse (stir)")
                else:
                    param_parts.append("🔄 0 (no mixing)")

                console.print(f"     [dim]{' | '.join(param_parts)}[/dim]")
            else:
                # Old format fallback
                console.print(f"  [bold]{step.step_number if hasattr(step, 'step_number') else '?'}.[/bold] {step}")

    # Notes
    if recipe.notes:
        console.print(f"\n[bold yellow]Notes:[/bold yellow]")
        console.print(f"  {recipe.notes}")

    if recipe.source:
        console.print(f"\n[dim]Source: {recipe.source}[/dim]")


if __name__ == '__main__':
    cli()
