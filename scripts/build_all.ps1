# PowerShell Script: Verify Backend & Build Production Frontend
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Building Full Project Production Deliverables            " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# 1. Run Tests
Write-Host "`n1. Running Pytest Suite..." -ForegroundColor Cyan
$env:PYTHONPATH = "."
backend\.venv\Scripts\python -m pytest backend/tests
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed! Aborting build." -ForegroundColor Red
    exit 1
}

# 2. Build Frontend
Write-Host "`n2. Building React TypeScript Production Bundle..." -ForegroundColor Cyan
Set-Location frontend
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed! Aborting." -ForegroundColor Red
    Set-Location ..
    exit 1
}
Set-Location ..

Write-Host "`nProject build complete and ready for deployment!" -ForegroundColor Green
