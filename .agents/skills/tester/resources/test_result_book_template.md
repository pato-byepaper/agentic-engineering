# Test Result Book: Issue #<ISSUE_NUMBER>

- **Target Issue**: #<ISSUE_NUMBER>
- **Date Tested**: <TIMESTAMP>
- **Tester Role**: Independent Verification Agent
- **Verdict**: [PASS | FAIL | PARTIAL]

---

## 1. Acceptance Criteria Extracted

- [ ] 1. <Criterion 1>
- [ ] 2. <Criterion 2>
- [ ] 3. <Criterion 3>

---

## 2. Test Execution & Raw Proof

> [!IMPORTANT]
> Raw terminal output must be pasted below. Paraphrasing or stating "it worked" is not valid proof.

### Test 1: <Description of Test Run>
**Command Executed:**
```bash
<COMMAND>
```

**Raw Output:**
```text
<PASTE EXACT TERMINAL OUTPUT HERE>
```

**Result**: [PASS / FAIL]

---

### Test 2: <Description of Edge Case / Regression Run>
**Command Executed:**
```bash
<COMMAND>
```

**Raw Output:**
```text
<PASTE EXACT TERMINAL OUTPUT HERE>
```

**Result**: [PASS / FAIL]

---

## 3. UI & Browser Validation (If Frontend Changes)

- **Local Preview URL**: `http://localhost:<PORT>/<feature>` (e.g. `http://localhost:8080/feature`)
- **Server Command**: `npm run dev` or equivalent local server start
- **Step-by-Step User Actions**:
  1. Navigated to local URL in browser.
  2. Executed user interaction (e.g. clicked button, submitted form, toggled control).
- **Observed UI & State Outcome**:
  - Functional behavior: Describe state change or rendered feedback.
  - Layout stability: Confirmed zero unexpected layout shift (CLS < 0.1).
  - Visual responsiveness: Rendered cleanly across target viewport sizes.
- **UI Verdict**: [PASS / FAIL / N/A]

---

## 4. Files Modified by Tester
List only test files authored. Production files must NEVER be touched:
- `tests/test_<feature>.py`

---

## 5. Unverified / Out of Scope Areas
Explicitly state what was not tested:
- Item 1: Reason why skipped (e.g. requires production credentials, load test > 10k users)

---

## 6. Findings & Discovered Issues
If any bugs or unexpected behaviors were found, document reproduction steps here:
- **Finding 1**: Description
  - **Reproduction**: Exact steps
  - **Severity**: Low / Med / High / Blocker

---

## 7. Final Recommendation to Manager
- **Status**: [Ready for Acceptance | Rejected to Tech Lead / Coder]
- **Justification**: One-sentence clear reason.
