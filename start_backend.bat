@echo off
echo ====================================================
echo Starting FastAPI Backend (http://localhost:8001)...
echo ====================================================
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
python -m uvicorn server:app --host 0.0.0.0 --port 8001 --reload
pause
