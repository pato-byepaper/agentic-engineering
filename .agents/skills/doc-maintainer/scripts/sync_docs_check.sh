#!/usr/bin/env bash
# sync_docs_check.sh
# Verifies that code changes altering schemas or API endpoints
# include corresponding updates in documentation or ADRs.

set -euo pipefail

BASE_REF="${1:-main}"
echo "==> Auditing documentation sync against: $BASE_REF"

DIFF_FILES=$(git diff --name-only "$BASE_REF...HEAD" 2>/dev/null || git diff --name-only HEAD~1..HEAD 2>/dev/null || echo "")

if [ -z "$DIFF_FILES" ]; then
    echo "No changed files detected. Skipping check."
    exit 0
fi

API_CHANGED=0
DOCS_CHANGED=0

while IFS= read -r file; do
    if echo "$file" | grep -Ei "(api|controller|routes|schema|migration)" >/dev/null; then
        API_CHANGED=1
    fi
    if echo "$file" | grep -Ei "(docs/|README|\.md)" >/dev/null; then
        DOCS_CHANGED=1
    fi
done <<< "$DIFF_FILES"

if [ "$API_CHANGED" -eq 1 ] && [ "$DOCS_CHANGED" -eq 0 ]; then
    echo "⚠️  WARNING: Changes detected in API/Schema routes without corresponding documentation updates."
    echo "   Consider updating docs/adr/, README.md, or API specs."
else
    echo "✅ Documentation sync check passed."
fi

exit 0
