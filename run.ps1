# run.ps1

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Args
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) { $venvPython = "python" }

Write-Host ""
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "          SENTINEL DRISHTI - LAUNCHER" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host ""

# First-run detection
& $venvPython -c "import easyocr" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "First run detected. Running setup..." -ForegroundColor Yellow
    & "$Root\setup.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Setup failed. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Streamlit shortcut
if ($Args -contains "--streamlit" -or $Args -contains "streamlit") {
    Write-Host "Launching Streamlit dashboard..." -ForegroundColor Yellow
    Write-Host ""
    & $venvPython -m streamlit run app.py --server.headless false
    exit $LASTEXITCODE
}

# Pass remaining args to sentinel.py
& $venvPython sentinel.py @Args