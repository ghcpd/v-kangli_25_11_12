@echo off
REM Setup script for Windows

echo Setting up Computer Vision Detection System...

REM Check Python version
python --version
if errorlevel 1 (
    echo Python is not installed or not in PATH. Please install Python 3.8+ first.
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "images" mkdir images
if not exist "output_images" mkdir output_images

echo Setup complete!
echo.
echo To use the system:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Place images in the 'images\' directory
echo 3. Run: python detector.py
echo.
echo For testing:
echo python test_detector.py

pause

