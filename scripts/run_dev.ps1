# PowerShell Script: Launch Backend and Frontend in Development Mode
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Starting Farmer Mandi Price Voice Agent Development Servers " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

$env:PYTHONPATH = "."

# Start Backend in new window
Write-Host "Starting FastAPI backend server on http://localhost:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PYTHONPATH='.'; backend\.venv\Scripts\python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

# Start Frontend in current window
Write-Host "Starting Vite frontend server on http://localhost:5173..." -ForegroundColor Cyan
Set-Location frontend
npm run dev
