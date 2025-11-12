@echo off
REM Run test script for Computer Vision Detection System (Windows)

echo.
echo ================================
echo CV Detection System - Test Suite
echo ================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

REM Run detection on sample images
echo Running detection pipeline on sample images...
python detect.py

echo.
echo Checking output files...
if exist "detections.json" (
    echo [OK] Detection results saved to detections.json
) else (
    echo [FAIL] detections.json not found
)

if exist "statistics.json" (
    echo [OK] Statistics saved to statistics.json
) else (
    echo [FAIL] statistics.json not found
)

if exist "output_images" (
    echo [OK] Annotated images saved to output_images/
) else (
    echo [FAIL] output_images not found
)

echo.
echo Running unit tests...
pytest test_detection.py -v --tb=short

echo.
echo ================================
echo Test Suite Completed!
echo ================================
echo.
pause
