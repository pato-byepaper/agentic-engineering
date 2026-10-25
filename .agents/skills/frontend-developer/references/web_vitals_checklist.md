# Google Core Web Vitals & Web Performance Guide

This reference provides technical rules and optimization checklists for high-speed web interfaces.

---

## 1. Largest Contentful Paint (LCP) — Target: < 2.5s

LCP measures perceived load speed. It marks the point when the main content of a page has likely loaded.

### Optimization Checklist
- [ ] **Preload LCP Hero Elements**: Preload hero images, critical SVGs, or key fonts using `<link rel="preload" as="image" href="..." fetchpriority="high">`.
- [ ] **Avoid Lazy Loading Above-the-Fold Media**: Never add `loading="lazy"` to the hero image or primary viewport banner.
- [ ] **Optimize Asset Delivery**:
  - Convert images to modern formats (`WebP` or `AVIF`).
  - Compress SVGs and remove unnecessary metadata.
- [ ] **Minimize TTFB (Time to First Byte)**:
  - Cache dynamic data with appropriate `Cache-Control` headers (e.g., `stale-while-revalidate`).
  - Avoid chaining redirects.
- [ ] **Critical CSS**: Inline critical path CSS and defer non-critical stylesheets.

---

## 2. Interaction to Next Paint (INP) — Target: < 200ms

INP measures responsiveness by observing the latency of all user interactions (clicks, taps, key presses) throughout the page lifecycle.

### Optimization Checklist
- [ ] **Avoid Long Tasks (> 50ms) on Main Thread**:
  - Break long computational tasks into smaller chunks using `scheduler.yield()` or `setTimeout(..., 0)`.
- [ ] **Use Optimistic UI Updates**:
  - Immediately reflect UI changes upon user action before awaiting network response (with fallback rollback on failure).
- [ ] **Debounce & Throttle High-Frequency Inputs**:
  - Debounce search inputs and auto-save events (e.g., 200-300ms).
  - Use `requestAnimationFrame` for scroll and resize listeners.
- [ ] **React / Modern Frameworks**:
  - Wrap non-urgent state updates in `startTransition` or `useDeferredValue`.
  - Avoid unnecessary re-renders with `React.memo`, `useMemo`, and `useCallback` on hot paths.

---

## 3. Cumulative Layout Shift (CLS) — Target: < 0.1

CLS measures visual stability. Unexpected layout shifts disorient users and cause accidental clicks.

### Optimization Checklist
- [ ] **Explicit Dimensions**:
  - Always set explicit `width` and `height` attributes or CSS `aspect-ratio` on all `<img>`, `<video>`, `<iframe>`, and canvas elements.
- [ ] **Reserve Space for Dynamic & Async Content**:
  - Use skeleton screens or placeholder containers with fixed min-heights for async widgets (banners, recommendations, ads).
- [ ] **Avoid Inserting Content Above Existing Content**:
  - Do not dynamically inject notification bars or DOM elements above existing viewport content unless in response to direct user action.
- [ ] **Font Layout Stability**:
  - Use `font-display: swap` or `font-display: optional` combined with size-adjust matching to eliminate layout shifting when custom web fonts swap in.

---

## 4. Asset Budget & Best Practices

- **Initial JS Bundle Budget**: Max 150KB gzip compressed per entry chunk.
- **Code Splitting**: Dynamic imports for heavy routes, modal dialogues, and third-party visualization libraries.
- **Tree Shaking**: Ensure ESM imports (`import { x } from 'lib'`) rather than importing entire packages (`import * as lib from 'lib'`).
