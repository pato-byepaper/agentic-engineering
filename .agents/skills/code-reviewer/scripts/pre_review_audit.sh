#!/usr/bin/env bash
# pre_review_audit.sh
# Performs automated sanity checks on git diff before human or tester review:
# 1. Scans for hardcoded secrets / API keys
# 2. Scans for leftover debug statements (debugger, console.log, print)
# 3. Scans for AI co-author trailers or watermarks
# 4. Scans for merge conflict markers

set -euo pipefail

BASE_REF="${1:-main}"
echo "==> Auditing changes against base: $BASE_REF"

DIFF=$(git diff "$BASE_REF...HEAD" 2>/dev/null || git diff HEAD~1..HEAD 2>/dev/null || echo "")

if [ -z "$DIFF" ]; then
    echo "No diff found to audit. Checking staged changes..."
    DIFF=$(git diff --cached 2>/dev/null || echo "")
fi

if [ -z "$DIFF" ]; then
    echo "No changes detected."
    exit 0
fi

FAILED=0

# 1. Secret patterns
if echo "$DIFF" | grep -Ei "(\"|')(ghp_|gho_|sk_live_|AKIA|AIza)[a-zA-Z0-9_-]+" >/dev/null; then
    echo "❌ CRITICAL: Potential hardcoded secret or API key found in diff!"
    FAILED=1
fi

# 2. Merge conflict markers
if echo "$DIFF" | grep -E "^(\+|<{7}|={7}|>{7})" | grep -E "(<{7}|={7}|>{7})" >/dev/null; then
    echo "❌ CRITICAL: Unresolved merge conflict markers detected!"
    FAILED=1
fi

# 3. AI Co-Author / Watermarks in commits
if git log -n 5 2>/dev/null | grep -Ei "Co-authored-by:.*(bot|ai|agent|assistant|copilot|gemini)" >/dev/null; then
    echo "❌ WARNING: AI Co-Authored trailer detected in recent commit logs."
    FAILED=1
fi

# 4. Stray debug statements in added lines
DEBUG_MATCHES=$(echo "$DIFF" | grep -E "^\+" | grep -Ei "(console\.log\(|debugger;|print\(|var_dump\()" || true)
if [ -n "$DEBUG_MATCHES" ]; then
    echo "⚠️  WARNING: Stray debug statements detected in added code:"
    echo "$DEBUG_MATCHES" | head -n 5
fi

if [ "$FAILED" -eq 0 ]; then
    echo "✅ Automated pre-review audit passed cleanly."
    exit 0
else
    echo "❌ Automated pre-review audit encountered blocking issues."
    exit 1
fi
