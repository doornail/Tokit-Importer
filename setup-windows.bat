@echo off
setlocal enabledelayedexpansion
REM Tokit Omnicook Recipe Importer - Windows Setup Script
REM This script automates the installation process for Windows users

echo ========================================
echo Tokit Omnicook Recipe Importer
echo Windows Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed!
    echo Please reinstall Python with pip enabled.
    pause
    exit /b 1
)

echo [2/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment!
    pause
    exit /b 1
)
echo Virtual environment created successfully.
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate
echo.

echo [4/5] Installing Python dependencies...
echo This may take a few minutes...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

echo [5/5] Installing Playwright browser...
echo This will download Chromium (about 150-200 MB)...
playwright install chromium
if errorlevel 1 (
    echo WARNING: Playwright installation may have failed.
    echo You can try again later with: playwright install chromium
)
echo.

REM Handle .env file
if exist ".env" (
    echo.
    echo ========================================
    echo Existing .env file found!
    echo ========================================
    echo.
    echo You already have a .env configuration file with your credentials.
    echo.
    set /p OVERWRITE="Do you want to OVERWRITE it with a blank template? (y/N): "

    REM Default to NO if user just presses Enter
    if "!OVERWRITE!"=="" set OVERWRITE=n

    if /i "!OVERWRITE!"=="y" (
        echo.
        echo WARNING: Overwriting existing .env file with blank template...
        copy /Y .env.example .env >nul
        echo.
        echo IMPORTANT: Edit .env file with your credentials:
        echo   - ANTHROPIC_API_KEY (required)
        echo   - COOKNJOY_EMAIL and COOKNJOY_PASSWORD (required)
        echo   - NYTIMES_EMAIL and NYTIMES_PASSWORD (optional)
        echo.
        echo Opening .env file in Notepad...
        timeout /t 2 >nul
        notepad .env
    ) else (
        echo.
        echo [KEEPING EXISTING .env FILE]
        echo Your credentials are safe and unchanged.
        echo.
        echo To edit your .env file manually, run: notepad .env
    )
    goto :skip_env_creation
)

REM Only reaches here if .env does NOT exist
echo Creating new .env configuration file...
copy .env.example .env >nul
echo.
echo IMPORTANT: Edit .env file with your credentials:
echo   - ANTHROPIC_API_KEY (required)
echo   - COOKNJOY_EMAIL and COOKNJOY_PASSWORD (required)
echo   - NYTIMES_EMAIL and NYTIMES_PASSWORD (optional)
echo.
echo Opening .env file in Notepad...
timeout /t 2 >nul
notepad .env

:skip_env_creation

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Your virtual environment is ready!
echo.
echo Quick start:
echo   - Test the installation:
echo     python main.py --help
echo.
echo   - Import a recipe:
echo     python main.py import-recipe --url "RECIPE_URL"
echo.
echo   - Or use the convenience script:
echo     import-recipe.bat "RECIPE_URL"
echo.
echo For detailed instructions, see WINDOWS_INSTALL.md
echo.
echo ========================================
echo Opening new command prompt with virtual environment activated...
echo ========================================
echo.

REM Launch new command prompt with venv activated
REM This keeps you in the virtual environment after setup
cmd /k "venv\Scripts\activate && echo. && echo Virtual environment activated! You can now run: python main.py --help && echo."
