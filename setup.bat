@echo off
REM Setup script for Computer Vision Detection System (Windows)
REM Run this file to set up the environment on Windows

echo.
echo ================================
echo CV Detection System Setup
echo ================================
echo.

REM Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)

echo Checking Python version...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip setuptools wheel

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

REM Create output directories
echo Creating output directories...
if not exist "output_images" mkdir output_images
if not exist "results" mkdir results
if not exist "logs" mkdir logs

echo.
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To activate the environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the detection pipeline, execute:
echo   python detect.py
echo.
echo To run tests, execute:
echo   pytest test_detection.py -v
echo.
pause
