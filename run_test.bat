@echo off
REM One-click test runner script for Windows

echo ==========================================
echo Computer Vision Detection System - Tests
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run tests
echo Running test suite...
echo.
python test_detector.py

echo.
echo ==========================================
echo Tests completed!
echo Check test_report.json for detailed results
echo ==========================================
pause

