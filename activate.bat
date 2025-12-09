@echo off
echo 🐍 Activating Python Virtual Environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated!
echo.
echo 📋 Available commands:
echo   - python backend/api/server.py  : Start backend server
echo   - npm run dev                   : Start frontend dev server  
echo   - pip list                      : Show installed packages
echo   - deactivate                    : Exit virtual environment
echo.
