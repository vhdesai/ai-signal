<#
.SYNOPSIS
  One-time environment setup for the AI Signal pipeline (Windows / PowerShell).
.EXAMPLE
  pwsh ./scripts/setup.ps1
#>
[CmdletBinding()]
param(
    [string]$Python = "python",
    [string]$EmbeddingModel = "BAAI/bge-small-en-v1.5"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    $venv = Join-Path $repoRoot ".venv"
    if (-not (Test-Path $venv)) {
        Write-Host "Creating virtual environment at $venv"
        & $Python -m venv $venv
    }
    $py = Join-Path $venv "Scripts/python.exe"

    Write-Host "Upgrading pip"
    & $py -m pip install --upgrade pip

    Write-Host "Installing the AI Signal pipeline (editable) and dependencies"
    & $py -m pip install -e ./source

    Write-Host "Pre-caching the embedding model: $EmbeddingModel"
    & $py ./scripts/precache_model.py $EmbeddingModel

    Write-Host "Smoke-testing the CLI"
    Push-Location source
    try { & $py -X utf8 -m news_trends --help | Out-Null } finally { Pop-Location }

    Write-Host "Setup complete. Run the pipeline with ./scripts/run-pipeline.ps1"
}
finally {
    Pop-Location
}
