# Tokit Omnicook Recipe Importer

A tool to import recipes from various sources and automatically convert them for use in the Tokit Omnicook, with automatic upload to the cooknjoy platform.

## Features

- 🍳 **Recipe Scraping**: Import recipes from NYTimes Cooking (more sources coming soon)
- 🤖 **AI-Powered Conversion**: Uses Claude AI to intelligently convert recipes to Tokit Omnicook format
- 🌐 **Automatic Upload**: Seamlessly uploads converted recipes to cooknjoy web interface
- 📝 **Smart Formatting**: Preserves recipe structure, ingredients, and instructions

## Prerequisites

- Python 3.8+
- Anthropic API key (for Claude AI)
- NYTimes Cooking account (for recipe access)
- Cooknjoy account (for recipe upload)

## Installation

### Windows Users

**See [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md) for detailed Windows installation instructions with screenshots and troubleshooting.**

Quick setup for Windows:
```cmd
setup-windows.bat
```

### Linux/Mac Users

1. Clone the repository:
```bash
git clone <repository-url>
cd Tokit-Importer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Create a `.env` file with the following:

```env
# Anthropic API
ANTHROPIC_API_KEY=your_api_key_here

# NYTimes Cooking (optional, for authenticated content)
NYTIMES_EMAIL=your_email@example.com
NYTIMES_PASSWORD=your_password

# Cooknjoy credentials
COOKNJOY_EMAIL=your_email@example.com
COOKNJOY_PASSWORD=your_password
```

## Usage

### Basic Usage

Import a NYTimes recipe by URL:

```bash
python main.py import-recipe --url "https://cooking.nytimes.com/recipes/..."
```

### Advanced Options

```bash
# Dry run (convert but don't upload)
python main.py import-recipe --url "URL" --dry-run

# Specify output directory for converted recipes
python main.py import-recipe --url "URL" --output ./recipes

# Skip upload to Cooknjoy (only scrape and convert)
python main.py import-recipe --url "URL" --no-upload

# Batch import from file
python main.py batch --file urls.txt

# Batch import with dry run
python main.py batch --file urls.txt --dry-run

# View a saved recipe
python main.py show recipes/Recipe_Name.json
```

## Project Structure

```
.
├── src/
│   ├── scrapers/       # Recipe scrapers for different sources
│   ├── converters/     # AI-powered recipe converters
│   ├── uploaders/      # Upload automation for cooknjoy
│   ├── models.py       # Data models
│   └── config.py       # Configuration management
├── main.py            # Main CLI application
└── examples/          # Example usage scripts
```

## How It Works

1. **Scrape**: Extracts recipe data from the source URL
2. **Convert**: Uses Claude AI to transform the recipe into Tokit Omnicook format
3. **Upload**: Automates the upload process to cooknjoy web interface

## Supported Sources

- ✅ NYTimes Cooking
- 🔜 AllRecipes (coming soon)
- 🔜 Food Network (coming soon)
- 🔜 Serious Eats (coming soon)

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.
