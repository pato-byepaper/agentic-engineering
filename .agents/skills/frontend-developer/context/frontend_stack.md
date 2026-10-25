# Frontend Stack & Performance Targets: agy-workshop

## Client Architecture
- **Framework**: unknown
- **Styling Solution**: unknown
- **Package Manager**: unknown
- **Stacked Branch**: `feat/<feature>-3-ui` (PR 3, targeting `feat/<feature>-2-api`)

## Google Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: < 2.5s (preload hero media, optimize server rendering).
- **INP (Interaction to Next Paint)**: < 200ms (avoid main thread blocking, optimistic UI).
- **CLS (Cumulative Layout Shift)**: < 0.1 (explicit width/height, reserve aspect-ratio containers).

## Strict Testing Separation & Committer Handoff
- **NEVER write or execute your own tests**: Only the `tester` subagent creates and runs unit, component, and Playwright E2E tests so that no developer can self-certify passing tests.
- Only run `npx tsc --noEmit` to verify compilation and provide a local preview URL.
- **At Least 1 Commit Per Task**: Immediately hand off to Committer (`git-publisher`) upon completing UI changes to commit on `feat/<feature>-3-ui` and update the stacked PR.
