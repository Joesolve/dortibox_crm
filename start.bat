@echo off
echo ======================================
echo Waste Collection Management System
echo ======================================
echo.
echo Starting the application...
echo.
echo The app will be available at: http://localhost:5000
echo.
echo Default Login Credentials:
echo -------------------------
echo Admin:
echo   Username: admin
echo   Password: admin123
echo.
echo Collector:
echo   Username: collector
echo   Password: collector123
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0"
python app.py
pause
