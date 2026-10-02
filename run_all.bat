@echo off
echo ====================================
echo Starting LeetLens Full Stack...
echo ====================================
start "LeetLens Backend (Port 8000)" cmd /k "%~dp0run_backend.bat"
start "LeetLens Frontend (Port 3000)" cmd /k "%~dp0run_frontend.bat"
echo Both servers are launching in separate windows!
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://localhost:3000
