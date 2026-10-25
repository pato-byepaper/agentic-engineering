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
# Command or test script that reproduces the bug
<REPRO_COMMAND>
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

## 5. Phased Fix Strategy
1. **Write Failing Test**: Author a test that specifically reproduces the failure.
2. **Minimal Surgical Fix**: Apply the smallest necessary change to make the test pass.
3. **Full Suite Verification**: Re-run the entire test suite to guarantee zero regression.

---

## 6. Verification Gate
- [ ] Reproducing test passes.
- [ ] Full regression suite is green.
- [ ] Tester independently validates in `test-results/<issue>.md`.
