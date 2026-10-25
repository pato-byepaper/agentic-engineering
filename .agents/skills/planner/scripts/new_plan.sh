#!/usr/bin/env bash
# new_plan.sh
# Wrapper to generate a new structured plan artifact.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/new_plan.py" "$@"
