<#
.SYNOPSIS
  Run the AI Signal pipeline (Windows / PowerShell).
.EXAMPLE
  pwsh ./scripts/run-pipeline.ps1                 # run-all
  pwsh ./scripts/run-pipeline.ps1 repair-urls     # one stage
  pwsh ./scripts/run-pipeline.ps1 clean-repairs   # revert bad URL repairs
#>
[CmdletBinding()]
param(
    [string]$Stage = "run-all",
    [int]$Limit = 0
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$py = Join-Path $repoRoot ".venv/Scripts/python.exe"
if (-not (Test-Path $py)) {
    throw "Virtual environment not found. Run ./scripts/setup.ps1 first."
}

$cmd = @("-X", "utf8", "-m", "news_trends", "--root", $repoRoot)
if ($Limit -gt 0) { $cmd += @("--limit", "$Limit") }
$cmd += $Stage

Push-Location (Join-Path $repoRoot "source")
try { & $py @cmd } finally { Pop-Location }
