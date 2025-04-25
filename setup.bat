@echo off
echo Project Management System - Setup

REM Check for Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in the PATH. Please install Python and try again.
    pause
    exit /b 1
)

REM Check for pip installation
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pip is not installed or not in the PATH. Please ensure pip is installed with Python.
    pause
    exit /b 1
)

REM Check for Docker installation
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed or not in the PATH. Please install Docker Desktop and try again.
    echo You can download Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Install required Python packages
echo Installing required Python packages...
pip install -r requirments.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check the error message above.
    pause
    exit /b 1
)

REM Ask user if they want to set up the database using Docker
echo.
echo === PostgreSQL Database Setup ===
echo.
echo Choose setup method:
echo 1. Set up using Docker (recommended)
echo 2. Skip database setup (I'll set it up manually)
echo.

set /p setup_choice="Enter your choice (1-2): "

if "%setup_choice%"=="1" (
    echo.
    echo Setting up PostgreSQL using Docker...
    
    REM Start PostgreSQL container using Docker Compose
    docker-compose up -d
    
    if %errorlevel% neq 0 (
        echo Failed to start PostgreSQL container. Please check the error message above.
        pause
        exit /b 1
    )
    
    echo.
    echo PostgreSQL database has been set up successfully with the following details:
    echo   - Database Name: project_management
    echo   - Username: postgres
    echo   - Password: Baseball1023
    echo   - Host: localhost
    echo   - Port: 5432
) else (
    echo.
    echo You've chosen to skip the database setup.
    echo.
    echo Before running the application, you need to:
    echo 1. Install PostgreSQL
    echo 2. Create a database called 'project_management'
    echo 3. Run the 'init-db.sql' script to create tables
    echo 4. Update connection settings in the application if needed
    echo.
)

echo.
echo Setup completed. You can now run the application with:
echo start.bat
echo.
pause 