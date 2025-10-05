@echo off
REM KEF Teacher Dashboard - Windows Production Setup Script

echo === KEF Teacher Dashboard - Production Setup ===

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is required but not found
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Create necessary directories
echo Creating application directories...
if not exist "logs" mkdir logs
if not exist "instance" mkdir instance
echo ✅ Directories created

REM Set up environment configuration
if not exist ".env" (
    echo Setting up environment configuration...
    copy .env.example .env
    echo ✅ Environment file created from template
    echo ⚠️  IMPORTANT: Edit .env file and set a secure SECRET_KEY!
) else (
    echo ✅ Environment file already exists
)

REM Database initialization
echo Initializing database...
python -c "from app import create_app; app = create_app('production'); app.app_context().push(); app.db_manager.init_database(); print('✅ Database initialized')"

echo.
echo === Setup Complete! ===
echo.
echo Next steps:
echo 1. Edit .env file and set a secure SECRET_KEY
echo 2. Configure your web server (see DEPLOYMENT.md)
echo 3. Start the application:
echo    - Development: python run.py
echo    - Production: python -m gunicorn --bind 0.0.0.0:5000 run:app
echo.
pause