@echo off
echo ========================================
echo   AI Study Assistant - Startup Script
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate
echo.

REM Check if requirements are installed
echo Checking dependencies...
pip show Flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
    echo.
    echo ⚠️  Please edit .env file and add your SECRET_KEY
    echo    (OpenAI API key is optional)
    echo.
    pause
)

REM Start the application
echo ========================================
echo   Starting AI Study Assistant...
echo ========================================
echo.
echo 🚀 Application will be available at:
echo    http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
