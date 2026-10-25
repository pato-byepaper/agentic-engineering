#!/usr/bin/env bash
# check_bundle_budget.sh
# Scans output directory (dist, build, out, or src) to detect oversized files exceeding budget thresholds.

set -euo pipefail

TARGET_DIR="${1:-dist}"
MAX_JS_KB=150
MAX_CSS_KB=50

echo "==> Auditing frontend bundle size in: $TARGET_DIR"

if [ ! -d "$TARGET_DIR" ]; then
    echo "Directory '$TARGET_DIR' not found. If this is a source-only check, specify the folder: ./check_bundle_budget.sh src"
    exit 0
fi

FAILED=0

# Scan JS files
while IFS= read -r file; do
    size_kb=$(du -k "$file" | cut -f1)
    if [ "$size_kb" -gt "$MAX_JS_KB" ]; then
        echo "⚠️  WARNING: JS file '$file' is ${size_kb}KB (Budget: ${MAX_JS_KB}KB)"
        FAILED=1
    fi
done < <(find "$TARGET_DIR" -type f \( -name "*.js" -o -name "*.jsx" -o -name "*.ts" -o -name "*.tsx" \))

# Scan CSS files
while IFS= read -r file; do
    size_kb=$(du -k "$file" | cut -f1)
    if [ "$size_kb" -gt "$MAX_CSS_KB" ]; then
        echo "⚠️  WARNING: CSS file '$file' is ${size_kb}KB (Budget: ${MAX_CSS_KB}KB)"
        FAILED=1
    fi
done < <(find "$TARGET_DIR" -type f \( -name "*.css" -o -name "*.scss" \))

if [ "$FAILED" -eq 0 ]; then
    echo "✅ All scanned bundle assets are within performance budgets."
else
    echo "❌ Some assets exceeded performance budgets. Consider code-splitting or asset compression."
fi

exit "$FAILED"
