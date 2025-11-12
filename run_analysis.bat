@echo off
REM 运行图片分析脚本
echo ==========================================
echo 计算机视觉检测系统 - 图片分析
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo.
    echo 请先安装Python 3.8或更高版本，然后运行：
    echo   setup.bat
    echo.
    pause
    exit /b 1
)

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [警告] 虚拟环境不存在，使用系统Python
    echo 建议先运行 setup.bat 创建虚拟环境
    echo.
)

REM 检查依赖是否安装
python -c "import ultralytics; import easyocr" >nul 2>&1
if errorlevel 1 (
    echo [错误] 缺少必要的依赖包！
    echo.
    echo 正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败！
        pause
        exit /b 1
    )
)

REM 创建输出目录
if not exist "output_images" mkdir output_images

REM 运行检测
echo.
echo 开始分析图片...
echo.
python detector.py --input images/ --output output_images/ --results results.json --stats statistics.json

if errorlevel 1 (
    echo.
    echo [错误] 分析过程中出现错误！
    pause
    exit /b 1
)

echo.
echo ==========================================
echo 分析完成！
echo ==========================================
echo.
echo 结果文件：
echo   - results.json (检测结果)
echo   - statistics.json (统计信息)
echo   - output_images\ (标注后的图片)
echo.
pause

