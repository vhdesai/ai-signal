#!/usr/bin/env bash
# Run the AI Signal pipeline (Linux / macOS).
set -euo pipefail

STAGE="${1:-run-all}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$REPO_ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "Virtual environment not found. Run ./scripts/setup.sh first." >&2
  exit 1
fi

cd "$REPO_ROOT/source"
"$PY" -X utf8 -m news_trends --root "$REPO_ROOT" "$STAGE"
