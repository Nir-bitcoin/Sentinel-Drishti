@echo off
echo.
echo ========================================
echo   Sentinel Drishti - Demo Launcher
echo ========================================
echo.

echo [1/2] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Please install Python 3.10+
    pause
    exit /b 1
)

echo [2/2] Starting Streamlit app...
echo.
echo Browser will open automatically.
echo Press Ctrl+C to stop.
echo.

python -m streamlit run app.py

pause