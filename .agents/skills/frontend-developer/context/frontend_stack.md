# Frontend Stack & Performance Targets: agy-workshop

## Client Architecture
- **Framework**: unknown
- **Styling Solution**: unknown
- **Package Manager**: unknown

## Google Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: < 2.5s (preload hero media, optimize server rendering).
- **INP (Interaction to Next Paint)**: < 200ms (avoid main thread blocking, optimistic UI).
- **CLS (Cumulative Layout Shift)**: < 0.1 (explicit width/height, reserve aspect-ratio containers).

## Strict Testing Separation Rule
- **NEVER write or execute your own tests**: Only the `tester` subagent creates and runs unit, component, and Playwright E2E tests so that no developer can self-certify passing tests.
- Only run `npx tsc --noEmit` to verify compilation before handing off to the Tester.
