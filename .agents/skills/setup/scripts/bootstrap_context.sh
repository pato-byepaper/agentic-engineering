#!/usr/bin/env bash
# bootstrap_context.sh
# Wrapper to run the context bootstrap script.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/bootstrap_context.py"
