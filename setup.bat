@echo off
echo ============================================
echo   Idea Analyzer - Windows Setup Script
echo ============================================
echo.

:: Check for Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed!
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    echo After installation, restart this script.
    pause
    exit /b 1
)
echo [OK] Docker found

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python from: https://python.org
    pause
    exit /b 1
)
echo [OK] Python found

:: Check for FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] FFmpeg not found. Installing via winget...
    winget install Gyan.FFmpeg
)
echo [OK] FFmpeg found

:: Create virtual environment
echo.
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

:: Install Python dependencies
echo.
echo Installing extractor dependencies...
pip install -r extractor\requirements.txt

echo.
echo Installing slack-bot dependencies...
pip install -r slack-bot\requirements.txt

:: Install additional dependencies
echo.
echo Installing additional dependencies...
pip install pymupdf python-docx

:: Create .env file if not exists
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo [ACTION REQUIRED] Please edit .env file with your Slack tokens
)

:: Start Docker services
echo.
echo Starting Docker services (Postgres, Redis, PostgREST)...
docker-compose up -d

:: Wait for services to be ready
echo.
echo Waiting for services to start...
timeout /t 10 /nobreak >nul

echo.
echo ============================================
echo   Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file with your Slack tokens
echo 2. Run: start-extractor.bat
echo 3. Run: start-slack-bot.bat (in another terminal)
echo.
pause
