# Example Issues & Workflow Template

This document provides sample issues demonstrating how tasks are structured and delegated across the autonomous engineering team.

---

## Issue #1: [Data] User Preferences Schema & Row Level Security

**Labels**: `data-engineer`, `database`

### Description
Define the database schema and security policies to store user preferences and notification settings.

### Acceptance Criteria
- Create table `user_preferences` with fields: `id`, `user_id` (UUID), `theme` (VARCHAR), `email_notifications` (BOOLEAN), `updated_at` (TIMESTAMPTZ).
- Add foreign key index on `user_id`.
- Implement Row Level Security (RLS) policies ensuring users can only read and write their own preferences.
- Provide reversible migration script (`UP` and `DOWN`).

---

## Issue #2: [Backend] User Preferences REST API & Validation

**Labels**: `backend-developer`, `api`
**Depends on**: Issue #1 (Stacked PR)

### Description
Implement service domain logic and HTTP endpoints for retrieving and updating user preferences.

### Acceptance Criteria
- `GET /api/v1/users/me/preferences`: Returns JSON payload with 200 OK.
- `PUT /api/v1/users/me/preferences`: Validates payload schema, updates record, and returns updated preferences.
- Returns 400 Bad Request with standard error payload on invalid theme values.
- 100% unit and integration test coverage for service and controller layers.

---

## Issue #3: [Frontend] User Preferences Settings View

**Labels**: `frontend-developer`, `ui`
**Depends on**: Issue #2 (Stacked PR)

### Description
Build the settings interface allowing users to toggle email notifications and select application themes.

### Acceptance Criteria
- Responsive settings component matching design specifications.
- Optimistic UI updates with instant feedback on toggle (INP < 200ms).
- Zero layout shifts when preferences finish loading (CLS < 0.1).
- Accessible keyboard navigation and WCAG AA contrast compliance.
- Independent verification pass by Tester recorded in `test-results/3.md`.
