@echo off
REM Autom8 Installation Script for Windows
REM Automated installation and setup

echo ========================================
echo Autom8 Installation Script
echo ========================================
echo.

REM Check Python version
echo [1/8] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Create virtual environment
echo [2/8] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping...
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)
echo.

REM Activate virtual environment
echo [3/8] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo.

REM Upgrade pip
echo [4/8] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo Pip upgraded successfully
echo.

REM Install dependencies
echo [5/8] Installing dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Install development dependencies
echo [6/8] Installing development dependencies...
pip install -r requirements-dev.txt --quiet
if errorlevel 1 (
    echo WARNING: Failed to install development dependencies
    echo Continuing anyway...
)
echo Development dependencies installed
echo.

REM Setup environment file
echo [7/8] Setting up environment configuration...
if exist .env (
    echo .env file already exists, skipping...
) else (
    if exist .env.example (
        copy .env.example .env >nul
        echo .env file created from template
        echo IMPORTANT: Please edit .env file with your configuration
    ) else (
        echo WARNING: .env.example not found
    )
)
echo.

REM Initialize database
echo [8/8] Initializing database...
python autom8\init_database.py
if errorlevel 1 (
    echo ERROR: Failed to initialize database
    pause
    exit /b 1
)
echo Database initialized successfully
echo.

REM Generate encryption keys
echo Generating encryption keys...
if exist generate_keys.py (
    python generate_keys.py
    echo Encryption keys generated
) else (
    echo WARNING: generate_keys.py not found, skipping...
)
echo.

REM Install pre-commit hooks (optional)
echo Installing pre-commit hooks...
pre-commit install >nul 2>&1
if errorlevel 1 (
    echo WARNING: Failed to install pre-commit hooks (optional)
) else (
    echo Pre-commit hooks installed
)
echo.

REM Installation complete
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Edit .env file with your configuration
echo   2. Start the API: python -m autom8.api
echo   3. Or use CLI: autom8 api start
echo.
echo For more information, see README.md
echo.
pause
