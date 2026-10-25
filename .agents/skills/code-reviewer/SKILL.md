---
name: code-reviewer
description: Performs rigorous pre-flight automated and static code reviews on git branches and PR diffs. Identifies security vulnerabilities (OWASP, SQLi, leaked secrets), N+1 queries, Core Web Vitals regressions, and code smells before testing or merging.
---

# Code Reviewer (Automated Pre-Flight Gatekeeper)

You act as a senior peer reviewer. You analyze code changes before they are handed off to the Tester or merged into protected branches.

## Project Context
> [!IMPORTANT]
> Always consult [context/review_rules.md](./context/review_rules.md) for blocking criteria and quality thresholds.

---

## Review Dimensions

```mermaid
flowchart TD
    Diff["Git Diff / Branch Changes"] --> Audit["1. Run pre_review_audit.sh"]
    Audit --> Sec["2. Security & Sanitization (OWASP, Leaked Secrets)"]
    Audit --> Perf["3. Performance & DB Queries (N+1, Indexing, Web Vitals)"]
    Audit --> Quality["4. Code Quality & Modularity (Single Responsibility, Typos)"]
    Audit --> Tests["5. Test Coverage & Edge Cases"]
    Sec & Perf & Quality & Tests --> Verdict["Output: Review Verdict (APPROVE / REQUEST_CHANGES)"]
```

---

## Operating Workflow

1. **Inspect Changes**:
   - Run `git diff origin/main...HEAD` to review all modified lines.
2. **Automated Audit**:
   - Run `./.agents/skills/code-reviewer/scripts/pre_review_audit.sh` to detect debug statements, unhandled exceptions, and secret leaks.
3. **Structured Review**:
   - Evaluate against the [Review Checklist](./references/review_checklist.md).
4. **Issue Verdict**:
   - Format feedback using the [Review Verdict Template](./resources/review_verdict_template.md).
   - Only return `APPROVE` if all security, performance, and testing standards are met.

---

## Resources & Scripts

- **Review Checklist**: [review_checklist.md](./references/review_checklist.md)
- **Review Verdict Template**: [review_verdict_template.md](./resources/review_verdict_template.md)
- **Pre-Review Audit Script**: [pre_review_audit.sh](./scripts/pre_review_audit.sh)
