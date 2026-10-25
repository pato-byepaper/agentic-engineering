# Code Review Rules & Thresholds

- **Blocking Thresholds**:
  - Any potential secret or API token committed to code.
  - Unindexed foreign key or unparameterized SQL queries.
  - Test suites failing or missing test coverage for new business logic.
  - Cumulative Layout Shift regressions or missing image dimensions.
  - AI Co-Author trailers or AI watermarks.
- **Review Cycle**:
  - The reviewer does not fix code.
  - Issues are returned to the specialized coder (`backend-developer`, `frontend-developer`, `data-engineer`).
