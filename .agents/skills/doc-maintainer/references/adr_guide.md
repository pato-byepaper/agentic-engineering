# Architecture Decision Record (ADR) Guide

An Architecture Decision Record (ADR) captures an important architectural decision made along with its context and consequences.

---

## 1. When to Write an ADR
Write an ADR when:
- Selecting or swapping a database, ORM, or third-party service.
- Adopting a new API protocol (e.g. REST to GraphQL, gRPC, WebSockets).
- Changing state management or frontend rendering strategy (e.g. SSR vs. SPA).
- Introducing breaking changes or major system refactoring.

---

## 2. ADR Lifecycle Statuses
- **PROPOSED**: Under review by Tech Lead and team.
- **ACCEPTED**: Approved and actively being implemented.
- **SUPERSEDED**: Replaced by a subsequent ADR (link the superseding ADR).
- **REJECTED**: Evaluated and discarded (documents why we did NOT choose this path).

---

## 3. Storage & Naming
- Location: `docs/adr/`
- Pattern: `NNNN-short-descriptive-title.md` (e.g. `0001-use-postgresql-with-rls.md`).
