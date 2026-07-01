#!/bin/bash
# Token Dashboard launcher
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"
PYTHONPATH="$SCRIPT_DIR" "$SCRIPT_DIR/.venv/bin/python" -c "from token_dash.app import main; main()"
