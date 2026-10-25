# Project Overview & Business Domain: agy-workshop

## Business Objective & Vision
- **Project**: agy-workshop
- **Primary Domain**: [To be refined with user during setup interview]
- **Target Audience / End Users**: [To be refined with user]

## Architectural Summary
- **Languages / Core Stack**: General / Unspecified
- **Frontend Layer**: unknown
- **Backend Services**: unknown
- **Data Persistence**: unknown (ORM/Migrations: unknown)

## Key Invariants for Manager
- Never inspect or edit source code directly.
- Always orchestrate the full specialist team via Tech Lead (`data-engineer`, `backend-developer`, `frontend-developer`, `code-reviewer`, `tester`, `git-publisher`).
- Enforce strict testing separation: developers never write or execute tests; only `tester` writes and executes tests.
- Accept feature completion only via Tester verification book (`test-results/<issue>.md`).
