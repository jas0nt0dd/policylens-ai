# PolicyLens AI — PowerShell Startup Script
# Runs both backend and frontend in parallel

Write-Host @"

╔═══════════════════════════════════════════════════════════╗
║           PolicyLens AI — Full Stack Startup             ║
║                                                           ║
║  Backend:   http://127.0.0.1:8000                        ║
║  Frontend:  http://localhost:3000                        ║
║  API Docs:  http://127.0.0.1:8000/docs                 ║
╚═══════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "📋 Creating .env from .env.example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env created!" -ForegroundColor Green
}

$python = if (Test-Path ".\venv\Scripts\python.exe") {
    (Resolve-Path ".\venv\Scripts\python.exe").Path
} elseif (Test-Path "..\venv\Scripts\python.exe") {
    (Resolve-Path "..\venv\Scripts\python.exe").Path
} else {
    "python"
}

$npm = if (Get-Command "npm.cmd" -ErrorAction SilentlyContinue) {
    "npm.cmd"
} else {
    "npm"
}

# Start backend
Write-Host "🚀 Starting Backend (port 8000)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath $python -ArgumentList "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8000"

# Wait for backend to start
Start-Sleep -Seconds 2

# Start frontend
Write-Host "🎨 Starting Frontend (port 3000)..." -ForegroundColor Green
Push-Location frontend
Start-Process -NoNewWindow -FilePath $npm -ArgumentList "run", "dev"
Pop-Location

Write-Host @"

✅ Both servers are running!
   - Backend:  http://127.0.0.1:8000
   - Frontend: http://localhost:3000

Press Ctrl+C in each window to stop the servers.

"@ -ForegroundColor Cyan
