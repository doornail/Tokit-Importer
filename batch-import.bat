@echo off
REM Tokit Omnicook Recipe Importer - Batch Import Script for Windows
REM Usage: batch-import.bat urls.txt

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

REM Check if file was provided
if "%~1"=="" (
    echo Usage: batch-import.bat FILE [OPTIONS]
    echo.
    echo Examples:
    echo   batch-import.bat urls.txt
    echo   batch-import.bat urls.txt --dry-run
    echo.
    pause
    exit /b 1
)

REM Check if file exists
if not exist "%~1" (
    echo ERROR: File not found: %~1
    pause
    exit /b 1
)

REM Run the batch import
echo.
echo ========================================
echo Tokit Omnicook Batch Import
echo ========================================
echo.
python main.py batch --file %*

REM Deactivate virtual environment
call deactivate

echo.
echo ========================================
echo Batch import complete!
echo ========================================
pause
