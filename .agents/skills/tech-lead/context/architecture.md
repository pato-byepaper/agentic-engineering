# Architecture & Technical Roadmap: agy-workshop

## System Topology & Contracts
- **Primary Languages**: General / Unspecified
- **Backend Architecture**: unknown
- **Frontend Architecture**: unknown
- **Database Engine & ORM**: unknown | unknown
- **Package Management**: unknown

## Engineering Standards, Full-Team Flow & Testing Separation
- **Full-Team Pipeline**: `manager` -> `tech-lead` (`planner`) -> `data-engineer` -> `backend-developer` -> `frontend-developer` -> `code-reviewer` -> `tester` -> `doc-maintainer` / `git-publisher`.
- **Stacked PR Convention**: Enforce branch stacking (`gh stack`) for dependent tasks (`Data -> Backend -> Frontend`).
- **Contracts First**: Contracts must be explicitly defined (interfaces / schemas) before coders start work.
- **Strict Testing Separation**: Coders NEVER write or execute tests (only static compilation checks like `npx tsc --noEmit`). Only `tester` writes and executes unit, integration, component, and E2E tests.
