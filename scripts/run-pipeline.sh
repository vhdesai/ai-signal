#!/usr/bin/env bash
# Run the AI Signal pipeline (Linux / macOS).
#
# Optional repair-urls tuning via environment variables:
#   REPAIR_TIMEOUT   seconds for the repair network phase (0 disables the time
#                    box; unset leaves the pipeline default of 60 min)
#   REPAIR_WORKERS   number of concurrent search/fetch workers
#   REPAIR_STOP_FILE sentinel file that requests graceful early termination
#
# Examples:
#   ./scripts/run-pipeline.sh                          # run-all
#   REPAIR_TIMEOUT=7200 ./scripts/run-pipeline.sh      # 2-hour repair time box
#   REPAIR_TIMEOUT=0 ./scripts/run-pipeline.sh         # disable the repair time box
#   REPAIR_WORKERS=16 ./scripts/run-pipeline.sh        # 16 concurrent repair workers
set -euo pipefail

STAGE="${1:-run-all}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$REPO_ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  echo "Virtual environment not found. Run ./scripts/setup.sh first." >&2
  exit 1
fi

ARGS=(-X utf8 -m news_trends --root "$REPO_ROOT")
[ -n "${REPAIR_TIMEOUT:-}" ] && ARGS+=(--repair-timeout "$REPAIR_TIMEOUT")
[ -n "${REPAIR_WORKERS:-}" ] && ARGS+=(--repair-workers "$REPAIR_WORKERS")
[ -n "${REPAIR_STOP_FILE:-}" ] && ARGS+=(--repair-stop-file "$REPAIR_STOP_FILE")
ARGS+=("$STAGE")

cd "$REPO_ROOT/source"
"$PY" "${ARGS[@]}"
