# PowerShell Script: Run All Backend Pytest Tests and TC1-TC4
Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Running Farmer Mandi Voice Agent Automated Test Suite    " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

$env:PYTHONPATH = "."
backend\.venv\Scripts\python -m pytest backend/tests -v

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nAll 23 automated tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed. Please review the output above." -ForegroundColor Red
}
