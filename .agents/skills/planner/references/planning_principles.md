# Core Principles of Engineering Planning

When creating implementation plans with AI agents, follow these principles:

---

## 1. Plan Before Code
Never permit an agent to start writing production code or creating branches until a plan artifact is drafted and approved. The plan clarifies ambiguous requirements and aligns expectations.

---

## 2. Match Plan Structure to Task Nature
- Greenfield features need interface contracts and stack sequencing.
- Bugs need reproduction proofs and blast radius checks.
- Refactors need invariant definitions and dual-run paths.
- Performance issues need numerical baseline metrics and budgets.

---

## 3. Explicit Verification Gates
Every phase in a plan must end with an objective verification gate:
- "Run `npm test` and show green output."
- "Execute `EXPLAIN ANALYZE` and verify index scan."
- "Verify that LCP is < 2.5s and bundle size is within budget."

---

## 4. "Stop and Ask" Checkpoints
If an agent discovers an unexpected dependency, failing migration, or broken premise during execution, it must stop immediately, document the surprise in the plan, and consult the Tech Lead or User rather than guessing.
