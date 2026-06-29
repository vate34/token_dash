#!/bin/bash
# Token Dashboard launcher
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"
PYTHONPATH="$PROJECT_DIR" "$SCRIPT_DIR/.venv/bin/python" -c "from token_dash.app import main; main()"
