@echo off
echo ============================================
echo PlanMySky Frontend Setup
echo ============================================
echo.

echo Step 1: Installing dependencies...
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 2: Checking for .env file...
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env and add your Google Maps API key!
    echo File location: %cd%\.env
    echo.
    pause
) else (
    echo .env file already exists
)
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next steps:
echo 1. Edit .env file and add your Google Maps API key
echo 2. Start the backend API: cd backend/api && python weather_api.py
echo 3. Start the frontend: npm run dev
echo.
echo Press any key to exit...
pause >nul
