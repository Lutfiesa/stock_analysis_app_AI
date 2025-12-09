@echo off
REM Stock Analysis App - Quick Start Script

echo ========================================
echo 🚀 Stock Analysis App - Quick Start
echo ========================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo ❌ Virtual environment not found!
    echo Run setup first: py -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🐍 Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo ✅ Python environment ready!
echo.
echo 📋 Quick Commands:
echo.
echo   1. Start Backend  : python backend/api/server.py
echo   2. Start Frontend : npm run dev
echo   3. Run Both       : Open two terminals and run both commands
echo.
echo 💡 Tip: Press Ctrl+C to stop servers
echo ⚙️  Configuration: Edit .env file for API keys
echo.
echo ========================================

cmd /k
