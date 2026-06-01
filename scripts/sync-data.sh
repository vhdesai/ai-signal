#!/usr/bin/env bash
# Sync pipeline data (SQLite DB + ChromaDB) between Obsidian and ext-host.
#
# Usage:
#   ./scripts/sync-data.sh                              # Obsidian -> ext-host
#   ./scripts/sync-data.sh --reverse                    # ext-host -> Obsidian
#   ./scripts/sync-data.sh --obsidian-root /path/to/obs # custom Obsidian path
set -euo pipefail

REVERSE=false
OBSIDIAN_ROOT=""
EXT_HOST_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reverse) REVERSE=true; shift ;;
    --obsidian-root) OBSIDIAN_ROOT="$2"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

if [ -z "$OBSIDIAN_ROOT" ]; then
  OBSIDIAN_ROOT="$(dirname "$EXT_HOST_ROOT")/Obsidian"
fi

if [ ! -d "$OBSIDIAN_ROOT" ]; then
  echo "Obsidian root not found at: $OBSIDIAN_ROOT" >&2
  echo "Use --obsidian-root to specify." >&2
  exit 1
fi

OBS_IDX="$OBSIDIAN_ROOT/indexes"
EXT_IDX="$EXT_HOST_ROOT/indexes"

if $REVERSE; then
  SRC_DB="$EXT_IDX/news_trends.db"; DST_DB="$OBS_IDX/news_trends.db"
  SRC_CHROMA="$EXT_IDX/chroma";     DST_CHROMA="$OBS_IDX/chroma"
  DIR="ext-host -> Obsidian"
else
  SRC_DB="$OBS_IDX/news_trends.db"; DST_DB="$EXT_IDX/news_trends.db"
  SRC_CHROMA="$OBS_IDX/chroma";     DST_CHROMA="$EXT_IDX/chroma"
  DIR="Obsidian -> ext-host"
fi

echo "Syncing data: $DIR"
mkdir -p "$(dirname "$DST_DB")"

if [ -f "$SRC_DB" ]; then
  cp "$SRC_DB" "$DST_DB"
  echo "  Copied news_trends.db"
else
  echo "  WARNING: Source DB not found at $SRC_DB"
fi

if [ -d "$SRC_CHROMA" ]; then
  rm -rf "$DST_CHROMA"
  cp -r "$SRC_CHROMA" "$DST_CHROMA"
  echo "  Copied chroma/ directory"
else
  echo "  WARNING: Source ChromaDB not found at $SRC_CHROMA"
fi

echo "Sync complete ($DIR)"
