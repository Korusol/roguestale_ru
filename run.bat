@echo off
chcp 65001 >nul 2>&1
cd /d "%~dp0"

echo ========================================
echo    Roguetale - Translation Editor
echo ========================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

python -c "import PySide6" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PySide6...
    pip install PySide6
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install PySide6.
        pause
        exit /b 1
    )
)

echo Starting editor...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Application exited with error.
    pause
)
