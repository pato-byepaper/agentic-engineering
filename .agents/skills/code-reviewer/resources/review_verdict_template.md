# Code Review Report: <Branch / PR Name>

- **Reviewer**: Code Review Gatekeeper
- **Date**: <TIMESTAMP>
- **Target Branch**: `<BRANCH_NAME>`
- **Verdict**: [APPROVE | REQUEST_CHANGES | COMMENT]

---

## 1. Executive Summary
Brief evaluation of the pull request changes, intent, and overall risk.

---

## 2. Findings & Action Items

### 🔴 Critical / Blocking (Must fix before merge)
- **File**: `path/to/file.ext` (Line XX)
  - **Issue**: Description of security flaw, N+1 query, or broken contract.
  - **Suggested Fix**:
    ```language
    // Corrected code snippet
    ```

### 🟡 Minor / Improvement (Non-blocking)
- **File**: `path/to/file.ext` (Line XX)
  - **Suggestion**: Naming clarity, minor refactoring, or additional test case.

---

## 3. Automated Pre-Review Audit Output
```text
<PASTE OUTPUT OF pre_review_audit.sh HERE>
```

---

## 4. Final Verdict Justification
- **Verdict**: [APPROVE | REQUEST_CHANGES]
- **Reason**: Single concise sentence explaining the conclusion.
