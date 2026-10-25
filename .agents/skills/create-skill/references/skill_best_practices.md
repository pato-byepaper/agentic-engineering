# Antigravity Skill Best Practices & Quality Standards

Follow these rules to ensure newly created skills are maintainable, efficient, and reliable:

---

## 1. Frontmatter Trigger Description
- The `description` field is the single most critical field. The model reads this description to decide whether to activate the skill.
- Always use **third-person** phrasing.
- State clearly **what** the skill does AND **when** to use it:
  ```yaml
  description: >-
    Automates database indexing analysis and creates missing composite indexes.
    Use when query performance degrades or when asked to optimize slow database queries.
  ```

---

## 2. Progressive Disclosure
- Avoid packing long documentation into `SKILL.md`.
- Keep `SKILL.md` under 100 lines: step-by-step procedure and clear relative links.
- Place bulky specifications, extensive guides, and API schemas in `references/`.
- Place templates and boilerplates in `resources/`.
- The agent only reads `references/` when the specific step demands it, conserving context tokens.

---

## 3. Executable Helper Scripts
- Encapsulate fragile multi-line bash or python commands into executable scripts under `scripts/`.
- Always set executable permissions: `chmod +x scripts/*.sh`.
- Reference them with relative markdown links: `[run_audit.sh](./scripts/run_audit.sh)`.

---

## 4. Verification & Validation Steps
- Never leave an agent without an objective verification mechanism.
- Every skill must define how to check that the action succeeded (e.g., test command, dry-run, exit code check).
