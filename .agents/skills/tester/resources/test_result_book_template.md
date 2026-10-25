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

## 3. Files Modified by Tester
List only test files authored. Production files must NEVER be touched:
- `tests/test_<feature>.py`

---

## 4. Unverified / Out of Scope Areas
Explicitly state what was not tested:
- Item 1: Reason why skipped (e.g. requires production credentials, load test > 10k users)

---

## 5. Findings & Discovered Issues
If any bugs or unexpected behaviors were found, document reproduction steps here:
- **Finding 1**: Description
  - **Reproduction**: Exact steps
  - **Severity**: Low / Med / High / Blocker

---

## 6. Final Recommendation to Manager
- **Status**: [Ready for Acceptance | Rejected to Tech Lead / Coder]
- **Justification**: One-sentence clear reason.
