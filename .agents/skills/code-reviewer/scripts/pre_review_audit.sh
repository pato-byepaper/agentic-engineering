#!/usr/bin/env bash
# pre_review_audit.sh
# Performs automated sanity checks on git diff before human or tester review:
# 1. Scans for forbidden emojis in added code lines
# 2. Scans for hardcoded secrets / API keys
# 3. Scans for leftover debug statements (debugger, console.log)
# 4. Scans for AI co-author trailers or watermarks
# 5. Scans for merge conflict markers

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
ADDED_LINES=$(echo "$DIFF" | grep -E "^\+[^\+]" || true)

# 1. Scan for forbidden emojis in added lines
EMOJI_MATCHES=$(python3 -c '
import sys, re
lines = sys.argv[1]
pattern = re.compile(r"[\U0001F300-\U0001FAFF\U00002700-\U000027BF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF]")
matches = pattern.findall(lines)
if matches:
    sys.stdout.write(" ".join(set(matches)) + "\n")
' "$ADDED_LINES")

if [ -n "$EMOJI_MATCHES" ]; then
    echo "ERROR: Forbidden emoji detected in added lines: $EMOJI_MATCHES"
    echo "Code, commits, and diffs must contain zero emojis."
    FAILED=1
fi

# 2. Secret patterns
if echo "$ADDED_LINES" | grep -Ei "(\"|')(ghp_|gho_|sk_live_|AKIA|AIza)[a-zA-Z0-9_-]+" >/dev/null; then
    echo "CRITICAL: Potential hardcoded secret or API key found in added lines!"
    FAILED=1
fi

# 3. Merge conflict markers
if echo "$ADDED_LINES" | grep -E "(<{7}|={7}|>{7})" >/dev/null; then
    echo "CRITICAL: Unresolved merge conflict markers detected in added lines!"
    FAILED=1
fi

# 4. AI Co-Author / Watermarks in commits
if git log -n 5 2>/dev/null | grep -Ei "Co-authored-by:.*(bot|ai|agent|assistant|copilot|gemini)" >/dev/null; then
    echo "WARNING: AI Co-Authored trailer detected in recent commit logs."
    FAILED=1
fi

# 5. Stray debug statements in added lines
DEBUG_MATCHES=$(echo "$ADDED_LINES" | grep -Ei "(console\.log\(|debugger;|var_dump\()" || true)
if [ -n "$DEBUG_MATCHES" ]; then
    echo "WARNING: Stray debug statements detected in added code:"
    echo "$DEBUG_MATCHES" | head -n 5
fi

if [ "$FAILED" -eq 0 ]; then
    echo "SUCCESS: Automated pre-review audit passed cleanly."
    exit 0
else
    echo "ERROR: Automated pre-review audit encountered blocking issues."
    exit 1
fi
