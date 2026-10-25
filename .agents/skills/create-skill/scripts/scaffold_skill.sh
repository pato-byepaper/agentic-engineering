#!/usr/bin/env bash
# scaffold_skill.sh
# Wrapper to scaffold a new Antigravity skill directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/scaffold_skill.py" "$@"
