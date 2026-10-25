# Backend Stack & API Conventions: agy-workshop

## Server Architecture
- **Framework / Runtime**: unknown
- **Language**: General / Unspecified
- **Data Layer Integration**: Interacts via unknown / unknown

## Operating Guidelines
- Follow contracts defined by Tech Lead.
- Standard error responses and input validation on all routes.
- Commit clean code referencing issues without emojis or AI co-author tags.

## Verification & Testing Separation Rule
- **STRICT INVARIANT**: Developers NEVER write or run their own unit, integration, or E2E tests. Only the `tester` subagent is authorized to write and execute tests so that no developer can self-certify passing tests.
- Developers may run `npx tsc --noEmit` (or equivalent static type/syntax check) to verify compilation before handing off to the Tester.
