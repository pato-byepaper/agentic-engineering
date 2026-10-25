# Backend Stack & API Conventions: agy-workshop

## Server Architecture
- **Framework / Runtime**: unknown
- **Language**: General / Unspecified
- **Data Layer Integration**: Interacts via unknown / unknown
- **Stacked Branch**: `feat/<feature>-2-api` (PR 2, targeting `feat/<feature>-1-data`)

## Operating Guidelines
- Follow contracts defined by Tech Lead.
- Standard error responses and input validation on all routes.
- Commit clean code referencing issues without emojis or AI co-author tags.

## Verification, Testing Separation & Committer Handoff
- **STRICT INVARIANT**: Developers NEVER write or run their own unit, integration, or E2E tests. Only the `tester` subagent is authorized to write and execute tests so that no developer can self-certify passing tests.
- Developers may run `npx tsc --noEmit` to verify compilation before handing off.
- **At Least 1 Commit Per Task**: As soon as code changes and type checks pass, immediately hand off to Committer (`git-publisher`) to commit on `feat/<feature>-2-api` and update the stacked PR. Never leave tasks uncommitted.
