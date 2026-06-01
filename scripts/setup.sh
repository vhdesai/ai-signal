#!/usr/bin/env bash
# One-time environment setup for the AI Signal pipeline (Linux / macOS).
set -euo pipefail

PYTHON="${PYTHON:-python3}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-BAAI/bge-small-en-v1.5}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV="$REPO_ROOT/.venv"
if [ ! -d "$VENV" ]; then
  echo "Creating virtual environment at $VENV"
  "$PYTHON" -m venv "$VENV"
fi
PY="$VENV/bin/python"

echo "Upgrading pip"
"$PY" -m pip install --upgrade pip

echo "Installing the AI Signal pipeline (editable) and dependencies"
"$PY" -m pip install -e ./source

echo "Pre-caching the embedding model: $EMBEDDING_MODEL"
"$PY" ./scripts/precache_model.py "$EMBEDDING_MODEL"

echo "Smoke-testing the CLI"
( cd source && "$PY" -X utf8 -m news_trends --help >/dev/null )

echo "Setup complete. Run the pipeline with ./scripts/run-pipeline.sh"
