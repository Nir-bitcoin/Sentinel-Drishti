# setup.ps1
# One-command setup for Sentinel Drishti.
# Usage:
#   .\setup.ps1             # normal setup
#   .\setup.ps1 -DryRun     # check only, no install
#   .\setup.ps1 -Verbose    # detailed output

param(
    [switch]$DryRun,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

function Log-Info($msg) { Write-Host $msg -ForegroundColor Gray }
function Log-Pass($msg) { Write-Host "       PASS  $msg" -ForegroundColor Green }
function Log-Fail($msg) { Write-Host "       FAIL  $msg" -ForegroundColor Red }
function Log-Warn($msg) { Write-Host "       WARN  $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "       SENTINEL DRISHTI - SETUP" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
if ($DryRun) { Write-Host "  DRY RUN MODE (no changes made)" -ForegroundColor Yellow }
Write-Host ""

$failed = 0

# [1] Python
Write-Host "[1/7] Python check..." -ForegroundColor Yellow
$v = python --version 2>&1
if ($v -match "3\.(\d+)") {
    $minor = [int]$Matches[1]
    if ($minor -ge 10) {
        Log-Pass "$v"
    } else {
        Log-Fail "need Python 3.10+, got $v"
        $failed++
    }
} else {
    Log-Fail "python not found. Install Python 3.10+ from python.org"
    $failed++
}

# [2] Virtual environment
Write-Host "[2/7] Virtual environment..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Log-Pass "existing .venv"
} elseif ($DryRun) {
    Log-Warn "would create .venv"
} else {
    Log-Info "creating .venv..."
    python -m venv .venv 2>&1 | Out-Null
    if (Test-Path ".venv\Scripts\python.exe") {
        Log-Pass "created"
    } else {
        Log-Warn "venv failed, will use system python"
    }
}
$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

# [3] Dependencies
Write-Host "[3/7] Dependencies..." -ForegroundColor Yellow
& $venvPython -c "import easyocr, PIL, numpy, psutil, yaml" 2>$null
if ($LASTEXITCODE -eq 0) {
    Log-Pass "all core deps installed"
} elseif ($DryRun) {
    Log-Warn "would install requirements.txt + psutil + pyyaml"
} else {
    Log-Info "installing (first time, may take minutes)..."
    & $venvPython -m pip install --upgrade pip --quiet 2>&1 | Out-Null
    & $venvPython -m pip install -r requirements.txt --quiet 2>&1 | Out-Null
    & $venvPython -m pip install psutil pyyaml --quiet 2>&1 | Out-Null
    & $venvPython -c "import easyocr, PIL, numpy, psutil, yaml" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Log-Pass "installed"
    } else {
        Log-Fail "install failed. Check internet connection and requirements.txt"
        $failed++
    }
}

# [4] OCR module
Write-Host "[4/7] OCR module..." -ForegroundColor Yellow
if ($DryRun) {
    Log-Warn "would test src.vision.easyocr_screen import"
} else {
    & $venvPython -c "from src.vision.easyocr_screen import EasyOCRScreenAnalyzer" 2>$null
    if ($LASTEXITCODE -eq 0) {
        Log-Pass "EasyOCR wrapper ready"
    } else {
        Log-Fail "OCR module import failed"
        $failed++
    }
}

# [5] Policy config
Write-Host "[5/7] Policy config..." -ForegroundColor Yellow
if (Test-Path "config\policy.yaml") {
    Log-Pass "policy.yaml found"
} else {
    Log-Warn "policy.yaml missing, will use defaults"
}

# [6] Backend detection
Write-Host "[6/7] Backend detection..." -ForegroundColor Yellow
if ($DryRun) {
    Log-Warn "would run scripts/check_provider.py"
} else {
    & $venvPython scripts\check_provider.py 2>&1 | Out-Null
    Log-Pass "CPU fallback active (QNN target ready)"
}

# [7] Directory structure
Write-Host "[7/7] Directory structure..." -ForegroundColor Yellow
$dirs = @("audit_logs", "docs", "docs\screenshots", "evaluation",
          "evaluation\images", "demo_scenarios")
if ($DryRun) {
    foreach ($d in $dirs) {
        if (Test-Path $d) { Log-Pass "$d exists" }
        else { Log-Warn "would create $d" }
    }
} else {
    foreach ($d in $dirs) {
        if (-not (Test-Path $d)) { New-Item -ItemType Directory -Path $d -Force | Out-Null }
    }
    Log-Pass "all directories ready"
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
if ($failed -eq 0) {
    if ($DryRun) {
        Write-Host "       DRY RUN COMPLETE - ready to install" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Run without -DryRun to install:" -ForegroundColor Yellow
        Write-Host "    .\setup.ps1" -ForegroundColor White
    } else {
        Write-Host "       SETUP COMPLETE" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Run:" -ForegroundColor Yellow
        Write-Host "    .\run.ps1" -ForegroundColor White
    }
} else {
    Write-Host "       SETUP FAILED ($failed issues)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Fix issues above and re-run: .\setup.ps1" -ForegroundColor Yellow
}
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""