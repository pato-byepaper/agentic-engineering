# Architecture & Technical Roadmap: agy-workshop

## System Topology & Contracts
- **Primary Languages**: General / Unspecified
- **Backend Architecture**: unknown
- **Frontend Architecture**: unknown
- **Database Engine & ORM**: unknown | unknown
- **Package Management**: unknown

## Engineering Standards, Full-Team Flow & Mandatory 3 Stacked PRs
- **Full-Team Pipeline**: `manager` -> `tech-lead` (`planner`) -> `data-engineer` -> `backend-developer` -> `frontend-developer` -> `code-reviewer` -> `tester` -> `doc-maintainer` / `git-publisher`.
- **Mandatory At Least 3 Stacked PRs**: For full-stack features touching data, backend, and frontend, enforce at least 3 stacked PRs (`PR 1: Data -> main`, `PR 2: Backend -> PR 1`, `PR 3: Frontend -> PR 2`).
- **Autonomous Dispatch**: Actively invoke subagents without waiting for manual human prompts.
- **Contracts First**: Contracts must be explicitly defined (interfaces / schemas) before coders start work.
- **Strict Testing Separation**: Coders NEVER write or execute tests (only static compilation checks like `npx tsc --noEmit`). Only `tester` writes and executes unit, integration, component, and E2E tests.
