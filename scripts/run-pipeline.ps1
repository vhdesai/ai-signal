<#
.SYNOPSIS
  Run the AI Signal pipeline (Windows / PowerShell).
.EXAMPLE
  pwsh ./scripts/run-pipeline.ps1                 # run-all
  pwsh ./scripts/run-pipeline.ps1 repair-urls     # one stage
  pwsh ./scripts/run-pipeline.ps1 clean-repairs   # revert bad URL repairs
  pwsh ./scripts/run-pipeline.ps1 -RepairTimeout 7200   # 2-hour repair time box
  pwsh ./scripts/run-pipeline.ps1 -RepairTimeout 0      # disable the repair time box
  pwsh ./scripts/run-pipeline.ps1 -RepairWorkers 16     # 16 concurrent repair workers
#>
[CmdletBinding()]
param(
    [string]$Stage = "run-all",
    [int]$Limit = 0,
    [double]$RepairTimeout = -1,
    [int]$RepairWorkers = 0,
    [string]$RepairStopFile = "",
    [string]$VenvPath = "C:\dev\ai-signal-venv"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$py = Join-Path $VenvPath "Scripts/python.exe"
if (-not (Test-Path $py)) {
    throw "Virtual environment not found at $VenvPath. Run ./scripts/setup.ps1 first."
}

$cmd = @("-X", "utf8", "-m", "news_trends", "--root", $repoRoot)
if ($Limit -gt 0) { $cmd += @("--limit", "$Limit") }
# RepairTimeout: seconds for the repair-urls network phase. 0 disables the time
# box; -1 (default) leaves the pipeline default (60 min) in place.
if ($RepairTimeout -ge 0) { $cmd += @("--repair-timeout", "$RepairTimeout") }
if ($RepairWorkers -gt 0) { $cmd += @("--repair-workers", "$RepairWorkers") }
if ($RepairStopFile -ne "") { $cmd += @("--repair-stop-file", $RepairStopFile) }
$cmd += $Stage

Push-Location (Join-Path $repoRoot "source")
try { & $py @cmd } finally { Pop-Location }
