# Testing Stack & Verification Guide: agy-workshop

## Test Environment
- **Test Runner / Framework**: unknown
- **Verification Target Directory**: `test-results/<issue>.md`

## Exclusive Testing Authority & Operating Guidelines
- **EXCLUSIVE OWNER**: Only the `tester` subagent is authorized to write and execute unit, component, integration, and E2E tests. Developers (`data-engineer`, `backend-developer`, `frontend-developer`, `coder`) NEVER write or run tests.
- Perform independent verification against acceptance criteria.
- Never fix bugs or touch production files.
- Always include raw command outputs and live UI verification proofs in the Test Result Book.
