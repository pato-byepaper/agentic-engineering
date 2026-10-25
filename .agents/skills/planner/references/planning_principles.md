# Core Principles of Engineering Planning

When creating implementation plans with AI agents, follow these principles:

---

## 1. Plan Before Code
Never permit an agent to start writing production code or creating branches until a plan artifact is drafted and approved. The plan clarifies ambiguous requirements and aligns expectations across the entire team (`manager`, `tech-lead`, `data-engineer`, `backend-developer`, `frontend-developer`, `code-reviewer`, `tester`, `git-publisher`).

---

## 2. Match Plan Structure to Task Nature
- Greenfield features need interface contracts and stack sequencing.
- Bugs need reproduction proofs and blast radius checks.
- Refactors need invariant definitions and dual-run paths.
- Performance issues need numerical baseline metrics and budgets.

---

## 3. Explicit Verification Gates & Strict Testing Separation
Every phase in a plan must end with an objective verification gate that respects role boundaries:
- **Developers (`data-engineer`, `backend-developer`, `frontend-developer`)**: NEVER write or run unit, component, integration, or E2E tests. Their verification gate is strictly static compilation/type checking (`npx tsc --noEmit`), query plan inspection (`EXPLAIN ANALYZE`), and bundle budget checks.
- **Tester (`tester`)**: Exclusively authors and executes all unit, component, integration, and E2E tests, plus interactive browser validation, recording proofs in `test-results/<issue>.md`.

---

## 4. "Stop and Ask" Checkpoints
If an agent discovers an unexpected dependency, failing migration, or broken premise during execution, it must stop immediately, document the surprise in the plan, and consult the Tech Lead or User rather than guessing.
