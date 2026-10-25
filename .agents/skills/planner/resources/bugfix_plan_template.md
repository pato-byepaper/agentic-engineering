# Bugfix & Incident RCA Plan: <Issue Name>

- **Type**: Defect / Bugfix
- **Severity**: Low | Medium | High | Critical
- **Issue Reference**: #<ISSUE_NUMBER>

---

## 1. Defect Description & Observed Failure
- **Expected Behavior**: What should happen.
- **Observed Behavior**: What actually happened (include logs or error stack traces).

---

## 2. Minimal Reproduction Steps
```bash
# Command or user steps that reproduce the bug
<REPRO_STEPS>
```
- **Observed Failure Output**:
```text
<RAW_ERROR_OUTPUT>
```

---

## 3. Root Cause Hypothesis
- **Underlying Cause**: Why does the error occur?
- **Invalid Assumption**: What assumption in the code was broken?

---

## 4. Blast Radius & Regression Analysis
- **Directly Affected Files**:
  - `path/to/file.py`
- **Downstream Consumers**: Modules, APIs, or database records touched.

---

## 5. Phased Fix & Exclusive Testing Strategy
1. **Minimal Surgical Fix (Developer)**: Apply the smallest necessary production code change and verify compilation (`npx tsc --noEmit`). **Developers NEVER write or run tests.**
2. **Pre-Flight Audit (Code Reviewer)**: Audit diff for regressions, security, and rule compliance.
3. **Exclusive Test Creation & Verification (Tester)**: Only the `tester` subagent writes the reproducing regression test, runs the full test suite, and records the proof in `test-results/<issue>.md`.

---

## 6. Verification Gate
- [ ] Static compilation passes (`npx tsc --noEmit`).
- [ ] Tester authors reproducing test and verifies full regression suite is green.
- [ ] Tester independently validates in `test-results/<issue>.md`.
