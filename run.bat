@echo off
echo ================================================
echo    Disk Scheduling Algorithm Visualizer
echo ================================================
echo.
echo Starting application...
echo.

python disk_scheduler_gui.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to start application
    echo Please ensure Python is installed and in PATH
    echo.
    pause
)