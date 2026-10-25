# Comprehensive Code Review Checklist

---

## 1. Security & Data Protection
- [ ] **No Hardcoded Secrets**: Ensure no API keys, private tokens, passwords, or credentials exist in code or comments.
- [ ] **SQL Injection Prevention**: Ensure all database queries use parameterized statements or ORM abstractions; never concatenate user input into SQL.
- [ ] **Cross-Site Scripting (XSS)**: Ensure user input rendered in HTML is sanitized/escaped.
- [ ] **Authorization & Tenant Isolation**: Verify that endpoints enforce tenant check (`tenant_id`) and user permission checks.

---

## 2. Database & Query Performance
- [ ] **No N+1 Queries**: Check loops that query the database inside iteration blocks; ensure eager loading (`include`/`join`) is used.
- [ ] **Foreign Key Indexing**: Ensure any newly created foreign key or filtered column has a corresponding database index.
- [ ] **Safe Migrations**: Verify that migrations are non-blocking and reversible.

---

## 3. Frontend & Web Performance
- [ ] **Google Core Web Vitals**:
  - Image elements have explicit `width` and `height` or aspect-ratio (CLS target < 0.1).
  - Heavy dynamic bundles are code-split (LCP target < 2.5s).
  - No blocking CPU computation in main interaction handlers (INP target < 200ms).
- [ ] **Accessibility (a11y)**: Buttons and interactive elements have accessible labels and ARIA roles where required.

---

## 4. Code Quality & Modularity
- [ ] **Single Responsibility**: Each function or class does exactly one thing cleanly.
- [ ] **Error Handling**: Exceptions are caught specifically; no silent swallowed errors (`except: pass`).
- [ ] **No Lingering Debug Code**: No stray `console.log`, `debugger`, `print()`, or temporary dump files.
- [ ] **Authorship Cleanliness**: No AI Co-Author trailers or AI generation watermarks.
