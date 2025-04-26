@echo off
echo Starting Project Management System...

REM Change to the script directory to ensure consistent behavior
cd /d "%~dp0"

REM Skip unnecessary checks which slow down the startup
echo Launching application...

REM Start the application without the slow checks
start "" pythonw Group_1_Project_Management_System.py

echo.
echo If you don't see the application window after a few seconds:
echo 1. Check if it's minimized in the taskbar
echo 2. Try running: python Group_1_Project_Management_System.py
echo 3. Make sure the database container is running

echo.
echo Application started. You can close this window. 