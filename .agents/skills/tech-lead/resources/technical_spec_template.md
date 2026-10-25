# Technical Architecture Specification: <Feature Name>

## 1. High-Level Architecture

```mermaid
flowchart TD
    Client["Frontend UI"] -->|"API Request"| API["Backend Service"]
    API -->|"SQL / ORM Query"| DB[("Database")]
```

## 2. Cross-Service Contract & Interface Definition

```typescript
// Shared Data Contract
export interface FeaturePayload {
  id: string;
  name: string;
  status: 'active' | 'archived';
  createdAt: string;
}
```

---

## 3. Sub-Ticket Breakdown & Delegation

### Ticket 1: Data Engineer (Base Layer)
- **Scope**: Schema definitions, indexes, RLS policies, migrations.
- **Deliverables**: Migration script + query performance validation (`EXPLAIN ANALYZE`).
- **Target Branch**: `feat/<feature>-data` (off `main`)

### Ticket 2: Backend Developer (API & Domain Logic)
- **Scope**: Endpoints, business logic, validation, error handling.
- **Deliverables**: Unit & integration tests, controllers, services.
- **Target Branch**: `feat/<feature>-backend` (stacked on `feat/<feature>-data`)

### Ticket 3: Frontend Developer (UI & User Experience)
- **Scope**: Client components, state management, accessibility, Google Core Web Vitals optimization.
- **Deliverables**: Tested UI components, responsive layout, zero layout shifts (CLS < 0.1).
- **Target Branch**: `feat/<feature>-frontend` (stacked on `feat/<feature>-backend`)

---

## 4. Stacked PR Order & Verification
1. PR #1: Data Layer (`main` <- `feat/<feature>-data`)
2. PR #2: Backend Layer (`feat/<feature>-data` <- `feat/<feature>-backend`)
3. PR #3: Frontend Layer (`feat/<feature>-backend` <- `feat/<feature>-frontend`)
4. Final Hand-off to Tester for end-to-end criteria verification.
