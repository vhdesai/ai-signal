<#
.SYNOPSIS
  One-time environment setup for the AI Signal pipeline (Windows / PowerShell).

  The virtual environment is created at C:\dev\ai-signal-venv (outside OneDrive)
  to avoid Purview/sync issues with .pem files in Python packages.

.EXAMPLE
  pwsh ./scripts/setup.ps1
  pwsh ./scripts/setup.ps1 -VenvPath "D:\my\venv"
#>
[CmdletBinding()]
param(
    [string]$Python = "python",
    [string]$EmbeddingModel = "BAAI/bge-small-en-v1.5",
    [string]$VenvPath = "C:\dev\ai-signal-venv"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    if (-not (Test-Path $VenvPath)) {
        Write-Host "Creating virtual environment at $VenvPath (outside OneDrive)"
        New-Item -ItemType Directory -Path (Split-Path $VenvPath) -Force | Out-Null
        & $Python -m venv $VenvPath
    }
    $py = Join-Path $VenvPath "Scripts/python.exe"

    Write-Host "Upgrading pip"
    & $py -m pip install --upgrade pip

    Write-Host "Installing the AI Signal pipeline (editable) and dependencies"
    & $py -m pip install -e ./source

    Write-Host "Pre-caching the embedding model: $EmbeddingModel"
    & $py ./scripts/precache_model.py $EmbeddingModel

    Write-Host "Smoke-testing the CLI"
    Push-Location source
    try { & $py -X utf8 -m news_trends --help | Out-Null } finally { Pop-Location }

    Write-Host "Setup complete."
    Write-Host "  Venv: $VenvPath"
    Write-Host "  Run the pipeline with: pwsh ./scripts/run-pipeline.ps1"
}
finally {
    Pop-Location
}
