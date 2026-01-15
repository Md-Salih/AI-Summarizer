# Start the Summarizer Application

Write-Host "`n==================================================================" -ForegroundColor Cyan
Write-Host "   STARTING SUMMARIZER APPLICATION" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Start Backend Server (Flask with FLAN-T5) in new window
Write-Host "`n[1/2] Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .venv\Scripts\activate; python backend\app.py" -WindowStyle Normal

# Wait for backend to initialize
Write-Host "      Waiting for model to load (this may take a moment)..." -ForegroundColor Gray
Start-Sleep -Seconds 8

# Start Frontend Server (Vite React) in new window
Write-Host "`n[2/2] Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal

# Wait and verify
Start-Sleep -Seconds 5

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host "   APPLICATION STARTED" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host "`n  Backend:  http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "`n  Open http://localhost:3000 in your browser to use the app!" -ForegroundColor Yellow
Write-Host "  Both servers are running in separate windows." -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
