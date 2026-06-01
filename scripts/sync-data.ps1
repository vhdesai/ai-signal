<#
.SYNOPSIS
  Sync pipeline data (SQLite DB + ChromaDB) between Obsidian and ext-host.

.DESCRIPTION
  Copies the SQLite database and ChromaDB directory from the Obsidian pipeline
  to the ext-host pipeline (or vice versa with -Reverse). Both pipelines use
  identical schemas, making the data fully portable.

.EXAMPLE
  pwsh ./scripts/sync-data.ps1                                    # Obsidian -> ext-host
  pwsh ./scripts/sync-data.ps1 -Reverse                           # ext-host -> Obsidian
  pwsh ./scripts/sync-data.ps1 -ObsidianRoot "D:\my\obsidian"     # custom path
#>
[CmdletBinding()]
param(
    [string]$ObsidianRoot = "",
    [switch]$Reverse
)

$ErrorActionPreference = "Stop"
$extHostRoot = Split-Path -Parent $PSScriptRoot

if (-not $ObsidianRoot) {
    # Default: sibling Obsidian directory
    $ObsidianRoot = Join-Path (Split-Path -Parent $extHostRoot) "Obsidian"
}

if (-not (Test-Path $ObsidianRoot)) {
    throw "Obsidian root not found at: $ObsidianRoot. Use -ObsidianRoot to specify."
}

$obsIndexes = Join-Path $ObsidianRoot "indexes"
$extIndexes = Join-Path $extHostRoot "indexes"

if ($Reverse) {
    $srcDb     = Join-Path $extIndexes "news_trends.db"
    $srcChroma = Join-Path $extIndexes "chroma"
    $dstDb     = Join-Path $obsIndexes "news_trends.db"
    $dstChroma = Join-Path $obsIndexes "chroma"
    $direction = "ext-host -> Obsidian"
} else {
    $srcDb     = Join-Path $obsIndexes "news_trends.db"
    $srcChroma = Join-Path $obsIndexes "chroma"
    $dstDb     = Join-Path $extIndexes "news_trends.db"
    $dstChroma = Join-Path $extIndexes "chroma"
    $direction = "Obsidian -> ext-host"
}

Write-Host "Syncing data: $direction"

# Ensure destination exists
New-Item -ItemType Directory -Path (Split-Path $dstDb) -Force | Out-Null

# Copy SQLite DB
if (Test-Path $srcDb) {
    Copy-Item $srcDb $dstDb -Force
    Write-Host "  Copied news_trends.db"
} else {
    Write-Host "  WARNING: Source DB not found at $srcDb"
}

# Copy ChromaDB directory
if (Test-Path $srcChroma) {
    if (Test-Path $dstChroma) { Remove-Item $dstChroma -Recurse -Force }
    Copy-Item $srcChroma $dstChroma -Recurse -Force
    Write-Host "  Copied chroma/ directory"
} else {
    Write-Host "  WARNING: Source ChromaDB not found at $srcChroma"
}

Write-Host "Sync complete ($direction)"
