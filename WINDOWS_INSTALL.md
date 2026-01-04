# Windows Installation Guide

Complete step-by-step installation instructions for Windows users.

## Prerequisites

### 1. Install Python

The application requires Python 3.8 or higher.

**Download Python:**
1. Go to [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python 3.x installer for Windows
3. Run the installer

**Important:** During installation:
- ✅ Check the box "Add Python to PATH"
- ✅ Check the box "Install pip"
- Click "Install Now"

**Verify Installation:**
Open Command Prompt (press `Win + R`, type `cmd`, press Enter) and run:
```cmd
python --version
```

You should see something like `Python 3.11.x` or higher.

### 2. Install Git (Optional but Recommended)

**Download Git:**
1. Go to [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. Download and run the installer
3. Use default settings during installation

**Verify Installation:**
```cmd
git --version
```

## Installation Steps

### Step 1: Get the Code

**Option A: Using Git (Recommended)**
```cmd
git clone <repository-url>
cd Tokit-Importer
```

**Option B: Download ZIP**
1. Download the repository as a ZIP file
2. Extract it to a folder (e.g., `C:\Users\YourName\Tokit-Importer`)
3. Open Command Prompt and navigate to the folder:
```cmd
cd C:\Users\YourName\Tokit-Importer
```

### Step 2: Create a Virtual Environment (Recommended)

Creating a virtual environment keeps the project dependencies isolated.

```cmd
python -m venv venv
```

**Activate the virtual environment:**
```cmd
venv\Scripts\activate
```

You should see `(venv)` appear at the beginning of your command prompt.

**Note:** You'll need to activate the virtual environment every time you use the application.

### Step 3: Install Python Dependencies

With the virtual environment activated:

```cmd
pip install -r requirements.txt
```

This will install all required packages including:
- anthropic (Claude API)
- playwright (browser automation)
- beautifulsoup4 (web scraping)
- click (CLI interface)
- rich (pretty console output)

**If you get an error about pip being outdated:**
```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install Playwright Browsers

Playwright needs to download browser binaries:

```cmd
playwright install chromium
```

This downloads the Chromium browser for automation. It's about 150-200 MB.

**If you get permission errors:**
Right-click Command Prompt and select "Run as administrator", then try again.

### Step 5: Configure the Application

**Create your configuration file:**
```cmd
copy .env.example .env
```

**Edit the .env file:**
1. Open the `.env` file with Notepad:
```cmd
notepad .env
```

2. Fill in your credentials:
```env
# Required: Your Anthropic API key
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Required: Cooknjoy login credentials
COOKNJOY_EMAIL=your_email@example.com
COOKNJOY_PASSWORD=your_password

# Optional: NYTimes Cooking credentials (for premium recipes)
NYTIMES_EMAIL=your_nytimes_email@example.com
NYTIMES_PASSWORD=your_nytimes_password
```

3. Save and close Notepad

**Getting an Anthropic API Key:**
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy and paste it into your `.env` file

## Testing the Installation

### Test the CLI

```cmd
python main.py --help
```

You should see the help menu with available commands.

### Test with Dry Run

Try importing a recipe without actually uploading:

```cmd
python main.py import-recipe --url "https://cooking.nytimes.com/recipes/1024687-chocolate-chip-cookies" --dry-run
```

This will:
1. Scrape the recipe
2. Convert it using Claude
3. Show you the result
4. NOT upload to cooknjoy (dry run mode)

## Using the Application

### Basic Usage

**Import a single recipe:**
```cmd
python main.py import-recipe --url "https://cooking.nytimes.com/recipes/12345-recipe-name"
```

**Batch import from a file:**
1. Create a text file with URLs (one per line):
```cmd
notepad urls.txt
```

2. Add your URLs:
```
https://cooking.nytimes.com/recipes/1234-first-recipe
https://cooking.nytimes.com/recipes/5678-second-recipe
```

3. Run batch import:
```cmd
python main.py batch --file urls.txt
```

**View a saved recipe:**
```cmd
python main.py show recipes\Recipe_Name.json
```

**Note:** Windows uses backslashes (`\`) for paths instead of forward slashes (`/`).

## Common Windows Issues and Solutions

### Issue 1: "python is not recognized"

**Problem:** Windows can't find Python.

**Solution:**
1. Make sure you checked "Add Python to PATH" during installation
2. Or manually add Python to PATH:
   - Search for "Environment Variables" in Windows
   - Edit "Path" under System Variables
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3x`
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python3x\Scripts`
3. Restart Command Prompt

### Issue 2: "execution of scripts is disabled"

**Problem:** PowerShell security policy blocks scripts.

**Solution:** Use Command Prompt (`cmd`) instead of PowerShell, or:
1. Open PowerShell as Administrator
2. Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
3. Type `Y` to confirm

### Issue 3: pip install fails with SSL error

**Problem:** Corporate firewall or proxy blocking pip.

**Solution:**
```cmd
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Issue 4: Playwright install fails

**Problem:** Permission issues or firewall blocking download.

**Solutions:**
1. Run Command Prompt as Administrator
2. Temporarily disable antivirus/firewall
3. Or install manually:
```cmd
python -m playwright install chromium --with-deps
```

### Issue 5: "ModuleNotFoundError"

**Problem:** Forgot to activate virtual environment or install dependencies.

**Solution:**
1. Make sure virtual environment is activated: `venv\Scripts\activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### Issue 6: Paths with spaces causing issues

**Problem:** Windows paths with spaces (e.g., `C:\My Documents\Tokit-Importer`)

**Solution:** Use quotes around paths:
```cmd
cd "C:\My Documents\Tokit-Importer"
python main.py import-recipe --url "..." --output "C:\My Recipes"
```

### Issue 7: Browser automation window not appearing

**Problem:** Playwright running in headless mode.

**Solution:** The browser runs in headless mode by default (invisible). This is normal. If you need to see the browser for debugging, you'll need to modify the code or check the logs.

## Daily Usage Workflow

Every time you want to use the application:

1. Open Command Prompt
2. Navigate to the project folder:
```cmd
cd C:\Users\YourName\Tokit-Importer
```

3. Activate the virtual environment:
```cmd
venv\Scripts\activate
```

4. Run the application:
```cmd
python main.py import-recipe --url "YOUR_RECIPE_URL"
```

5. When done, deactivate the virtual environment:
```cmd
deactivate
```

## Creating a Shortcut (Optional)

To make it easier to run, create a batch file:

1. Create a new file called `import-recipe.bat`:
```cmd
notepad import-recipe.bat
```

2. Add this content:
```batch
@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python main.py import-recipe --url %1
pause
```

3. Save and close

4. Now you can drag-and-drop or run:
```cmd
import-recipe.bat "https://cooking.nytimes.com/recipes/12345"
```

## Updating the Application

To get the latest changes:

```cmd
git pull origin claude/recipe-converter-omnicook-NXC7L
pip install -r requirements.txt
```

## Uninstalling

To completely remove the application:

1. Deactivate virtual environment: `deactivate`
2. Delete the entire project folder
3. Optional: Uninstall Python if not needed for other projects

## Getting Help

If you encounter issues not covered here:

1. Check the main [README.md](README.md)
2. Look at [QUICKSTART.md](QUICKSTART.md)
3. Open an issue on GitHub
4. Include:
   - Windows version (Win 10/11)
   - Python version (`python --version`)
   - Full error message
   - Steps to reproduce

## Video Tutorial (Coming Soon)

We're working on a video tutorial for Windows users. Check back soon!

## Tips for Windows Users

- **Use Command Prompt** instead of PowerShell to avoid script execution issues
- **Keep paths simple** without spaces when possible
- **Run as Administrator** if you encounter permission errors
- **Disable antivirus temporarily** during installation if it blocks downloads
- **Use Windows Terminal** (available in Microsoft Store) for a better command-line experience
- **Create a desktop shortcut** to your batch file for quick access

## Next Steps

Once installed, check out:
- [QUICKSTART.md](QUICKSTART.md) - Quick usage guide
- [examples/example_usage.py](examples/example_usage.py) - Code examples
- [CONTRIBUTING.md](CONTRIBUTING.md) - Add new recipe sources

Happy cooking with your Tokit Omnicook! 🍳
