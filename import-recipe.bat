@echo off
REM Tokit Omnicook Recipe Importer - Windows Batch Script
REM Usage: import-recipe.bat "https://cooking.nytimes.com/recipes/12345"

setlocal

REM Get the directory where this batch file is located
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup first: python -m venv venv
    echo Then install dependencies: venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Check if URL was provided
if "%~1"=="" (
    echo Usage: import-recipe.bat "URL" [OPTIONS]
    echo.
    echo Examples:
    echo   import-recipe.bat "https://cooking.nytimes.com/recipes/12345"
    echo   import-recipe.bat "URL" --dry-run
    echo   import-recipe.bat "URL" --no-upload
    echo.
    pause
    exit /b 1
)

REM Run the import
echo.
echo ========================================
echo Tokit Omnicook Recipe Importer
echo ========================================
echo.
python main.py import-recipe --url %*

REM Deactivate virtual environment
call deactivate

echo.
echo ========================================
echo Import complete!
echo ========================================
pause
