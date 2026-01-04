# Quick Start Guide

Get started with the Tokit Omnicook Recipe Importer in 5 minutes.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Tokit-Importer

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your credentials:
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
COOKNJOY_EMAIL=your_email@example.com
COOKNJOY_PASSWORD=your_password
```

## Your First Import

Import a single NYTimes recipe:

```bash
python main.py import-recipe --url "https://cooking.nytimes.com/recipes/12345-example"
```

### Test Without Uploading

Use the `--dry-run` flag to test the scraping and conversion without uploading:

```bash
python main.py import-recipe --url "URL" --dry-run
```

### Save Without Uploading

To only scrape and convert (no upload to Cooknjoy):

```bash
python main.py import-recipe --url "URL" --no-upload
```

## Batch Import

Create a file with URLs (one per line):

```bash
# urls.txt
https://cooking.nytimes.com/recipes/12345-first-recipe
https://cooking.nytimes.com/recipes/67890-second-recipe
```

Then import all at once:

```bash
python main.py batch --file urls.txt
```

## View a Saved Recipe

Display a previously saved recipe:

```bash
python main.py show recipes/Recipe_Name.json
```

## Common Options

- `--dry-run`: Test without uploading
- `--no-upload`: Skip Cooknjoy upload
- `--output DIR`: Save recipes to specific directory
- `--help`: Show all available options

## Troubleshooting

### "No module named 'X'" error
Install dependencies: `pip install -r requirements.txt`

### "ANTHROPIC_API_KEY is required"
Add your API key to the `.env` file

### Login fails
- Check your Cooknjoy credentials in `.env`
- Try running with visible browser: The uploader will show you what's happening

### Recipe scraping fails
- Verify the URL is from a supported source (currently NYTimes Cooking)
- Check your internet connection
- For NYTimes premium recipes, add your credentials to `.env`

## What's Next?

- Check `CONTRIBUTING.md` to add support for more recipe sources
- See `examples/example_usage.py` for programmatic usage
- Read the full README for advanced features

## Need Help?

- Check the full [README.md](README.md)
- See [examples](examples/)
- Open an issue on GitHub
