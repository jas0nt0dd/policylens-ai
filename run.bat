@echo off
REM PolicyLens AI — Windows Startup Script
REM Runs both backend and frontend in parallel

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║           PolicyLens AI — Full Stack Startup             ║
echo ║                                                           ║
echo ║  Backend: http://127.0.0.1:8000                          ║
echo ║  Frontend: http://localhost:3000                         ║
echo ║  API Docs: http://127.0.0.1:8000/docs                  ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Create .env if it doesn't exist
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
)

set "PYTHON_BIN=python"
if exist venv\Scripts\python.exe set "PYTHON_BIN=venv\Scripts\python.exe"
if exist ..\venv\Scripts\python.exe set "PYTHON_BIN=..\venv\Scripts\python.exe"

set "NPM_BIN=npm"
if exist "%ProgramFiles%\nodejs\npm.cmd" set "NPM_BIN=%ProgramFiles%\nodejs\npm.cmd"

REM Start backend in a new window
echo 🚀 Starting Backend (port 8000)...
start "PolicyLens Backend" cmd /k %PYTHON_BIN% -m uvicorn backend.main:app --reload --port 8000

REM Wait 2 seconds before starting frontend
timeout /t 2 /nobreak

REM Start frontend in a new window
echo 🎨 Starting Frontend (port 3000)...
cd frontend
start "PolicyLens Frontend" cmd /k %NPM_BIN% run dev

echo.
echo ✅ Both servers are starting in separate windows!
echo.
pause
