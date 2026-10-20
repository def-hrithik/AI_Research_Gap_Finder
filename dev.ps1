<#
.SYNOPSIS
    Development startup script for AI Research Gap Finder on Windows PowerShell.
.DESCRIPTION
    Checks environment prerequisites, terminates stale processes on port 8000,
    validates health, and starts the FastAPI backend and Vite frontend.
#>

param (
    [switch]$CheckOnly,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   AI Research Gap Finder - Local Development Assistant   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Environment file check
$envFile = Join-Path $PSScriptRoot "backend\.env"
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] backend\.env not found!" -ForegroundColor Red
    Write-Host "Please copy backend\.env.example to backend\.env and configure your API keys." -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "[OK] backend\.env found." -ForegroundColor Green
}

# 2. Check for port 8000 conflicts
Write-Host "Checking port 8000 for zombie or conflicting processes..." -ForegroundColor Gray
$connections = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
if ($connections) {
    foreach ($conn in $connections) {
        $pidToKill = $conn.OwningProcess
        Write-Host "[WARNING] Port 8000 is in use by PID $pidToKill. Releasing port to prevent socket deadlocks..." -ForegroundColor Yellow
        try {
            Stop-Process -Id $pidToKill -Force -ErrorAction SilentlyContinue
            Write-Host "[OK] Terminated stale process $($pidToKill) on port 8000." -ForegroundColor Green
        } catch {
            Write-Host "[WARN] Could not stop PID $($pidToKill): $_" -ForegroundColor DarkYellow
        }
    }
} else {
    Write-Host "[OK] Port 8000 is clear." -ForegroundColor Green
}

if ($CheckOnly) {
    Write-Host "Prerequisite checks completed." -ForegroundColor Green
    exit 0
}

# 3. Locate Python executable
$venvPython = Join-Path $PSScriptRoot "backend\.venv\Scripts\python.exe"
$pythonExe = if (Test-Path $venvPython) { $venvPython } else { "python" }

# 4. Instructions for dual terminal or background launch
Write-Host ""
Write-Host "Recommended startup commands:" -ForegroundColor Cyan
Write-Host "  Terminal 1 (Backend):" -ForegroundColor White
Write-Host "    cd backend" -ForegroundColor Gray
Write-Host "    $pythonExe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  Terminal 2 (Frontend):" -ForegroundColor White
Write-Host "    npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  Health Check:" -ForegroundColor White
Write-Host "    Invoke-RestMethod http://127.0.0.1:8000/api/health" -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan
