@echo off
echo ====================================================
echo Starting React Frontend (http://localhost:3000)...
echo ====================================================
cd /d "%~dp0frontend"
call yarn start
pause
