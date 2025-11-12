@echo off
REM Run the detection script and validate outputs exist
python scripts\detect.py --images_dir images --output_dir outputs --output_images_dir output_images --weights yolov8n.pt

IF EXIST outputs\summary.json (
  ECHO Summary file created
) ELSE (
  ECHO Missing summary.json
  EXIT /B 1
)

FOR %%f IN (images\*.jpg images\*.png) DO (
  set "b=%%~nxf"
  if exist outputs\%%~nf.json (
    ECHO outputs\%%~nf.json exists
  ) ELSE (
    ECHO Missing outputs\%%~nf.json
    EXIT /B 1
  )
)

echo All tests passed.
