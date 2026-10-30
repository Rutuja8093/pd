@echo off
echo ====================================================
echo Starting All Services (MongoDB + Backend + Frontend)
echo ====================================================
start "MongoDB Server" cmd /k "%~dp0start_mongo.bat"
timeout /t 3 /nobreak >nul
start "FastAPI Backend" cmd /k "%~dp0start_backend.bat"
timeout /t 2 /nobreak >nul
start "React Frontend" cmd /k "%~dp0start_frontend.bat"
echo.
echo ====================================================
echo All services launched!
echo Backend:  http://localhost:8001
echo Frontend: http://localhost:3000
echo ====================================================
pause
