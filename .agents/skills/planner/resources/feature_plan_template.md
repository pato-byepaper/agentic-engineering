# Feature Implementation Plan: <Feature Name>

- **Type**: New Feature
- **Status**: Draft | Approved | In Progress | Complete
- **Issue Reference**: #<ISSUE_NUMBER>

---

## 1. Goal & Architecture Overview
- **User Objective**: What user need or capability is unlocked?
- **Architecture Diagram**:
```mermaid
flowchart LR
    Client["Client UI"] --> API["Backend API"]
    API --> DB[("Database")]
```

---

## 2. Phase 1: Data Layer (Data Engineer)
- [ ] Schema changes & migrations.
- [ ] Primary key & foreign key indexing.
- [ ] Row Level Security (RLS) policies.
- **Verification Gate**: Migration runs and rolls back cleanly (`EXPLAIN ANALYZE` proof).
- **Branch**: `feat/<name>-data` (targets `main`)

---

## 3. Phase 2: API & Domain Logic (Backend Developer)
- [ ] Interface types & DTO validation.
- [ ] Domain service logic & business rules.
- [ ] Controller endpoints & standardized error codes.
- **Verification Gate**: Unit and integration test suite passing with raw output.
- **Branch**: `feat/<name>-api` (stacked on `feat/<name>-data`)

---

## 4. Phase 3: User Interface & Experience (Frontend Developer)
- [ ] Responsive components & design system integration.
- [ ] State management, optimistic updates, and loading skeletons.
- [ ] Google Core Web Vitals audit (LCP < 2.5s, INP < 200ms, CLS < 0.1).
- **Verification Gate**: Zero layout shift, bundle budget respected.
- **Branch**: `feat/<name>-ui` (stacked on `feat/<name>-api`)

---

## 5. Phase 4: Independent Verification (Tester)
- [ ] End-to-end user scenario testing.
- [ ] Edge cases and invalid inputs.
- [ ] Output recorded in `test-results/<issue>.md`.
