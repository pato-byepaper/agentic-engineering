# Code Review Rules & Thresholds

- **Blocking Thresholds**:
  - Any potential secret or API token committed to code.
  - Unindexed foreign key or unparameterized SQL queries.
  - Developer self-testing violation: any unit, integration, component, or E2E test file created or modified by a developer (`data-engineer`, `backend-developer`, `frontend-developer`, `coder`) instead of `tester`.
  - Static compilation or type check (`npx tsc --noEmit`) failing.
  - Cumulative Layout Shift regressions or missing image dimensions.
  - Emojis, AI Co-Author trailers, or AI watermarks.
- **Review Cycle**:
  - The reviewer does not fix code or write tests.
  - Issues are returned to the specialized coder (`backend-developer`, `frontend-developer`, `data-engineer`), and approved diffs proceed to `tester` for exclusive test creation and execution.
