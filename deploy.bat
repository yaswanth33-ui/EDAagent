@echo off
REM Production deployment script for EDA Agent (Windows)
title EDA Agent - Deployment

echo ========================================
echo    EDA Agent - Production Deployment
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.11+ and add it to your PATH.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/5] Checking Python installation...
python --version

REM Check if .env file exists
if not exist "server\.env" (
    echo.
    echo ERROR: server\.env file not found!
    echo Please create a .env file in the server directory with your API keys.
    echo Example:
    echo   OPENROUTER_API_KEY=your_api_key_here
    echo   SECRET_KEY=your_secret_key_here
    echo   FLASK_ENV=production
    echo.
    pause
    exit /b 1
)

echo [2/5] Environment file found...

REM Install/update dependencies
echo [3/5] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to install dependencies!
    echo Try running as Administrator or check your internet connection.
    pause
    exit /b 1
)

REM Run database setup
echo [4/5] Setting up database...
cd server
python -c "from database import Database; db = Database(); print('Database initialized successfully!')"
if %ERRORLEVEL% neq 0 (
    echo ERROR: Database setup failed!
    cd ..
    pause
    exit /b 1
)

echo [5/5] Starting application...
echo.
echo ========================================
echo  EDA Agent is starting...
echo  
echo  Production URL: http://localhost:8000
echo  
echo  Press Ctrl+C to stop the server
echo ========================================
echo.

REM Check if Gunicorn is available and start the application
where gunicorn >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo Starting with Gunicorn (Production server)...
    echo.
    gunicorn --config ..\gunicorn.conf.py app:app
) else (
    echo Gunicorn not found, starting with Flask development server...
    echo WARNING: This is not recommended for production use!
    echo.
    python app.py
)

cd ..
echo.
echo Application stopped.
pause
