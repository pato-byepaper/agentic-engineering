# Mandatory Stacked Pull Requests Strategy (`gh stack`)

Stacked PRs break down cross-cutting full-stack features into small, atomic, and reviewable pull requests that build on one another.

---

## 1. The Mandatory 3-PR Stack Architecture

For every full-stack feature touching data, backend, and frontend, the team **MUST produce at least 3 stacked PRs**:

```mermaid
flowchart LR
    Main["main"] <-- "PR 1 (Base Layer)" -- Branch1["feat/<feature>-1-data"]
    Branch1 <-- "PR 2 (API Layer)" -- Branch2["feat/<feature>-2-api"]
    Branch2 <-- "PR 3 (UI Layer)" -- Branch3["feat/<feature>-3-ui"]
```

1. **Layer 1: Data Engineer (PR 1 — Base Layer)**
   - Contains database migrations, indexing, and RLS policies.
   - Branch: `feat/<feature>-1-data`
   - Base target: `main`
2. **Layer 2: Backend Developer (PR 2 — API Layer)**
   - Implements business logic and API endpoints consuming Layer 1.
   - Branch: `feat/<feature>-2-api`
   - Base target: `feat/<feature>-1-data`
3. **Layer 3: Frontend Developer (PR 3 — UI Layer)**
   - Builds UI components and client state consuming Layer 2 contracts.
   - Branch: `feat/<feature>-3-ui`
   - Base target: `feat/<feature>-2-api`

---

## 2. Autonomous Git Commands for Committer

The Committer (`git-publisher`) runs these commands autonomously as each developer finishes:

```bash
# 1. Base Layer (Data Engineer)
git checkout main
git checkout -b feat/<feature>-1-data
# Data Engineer finishes changes & static check
git add <data-files>
git commit -m "feat(data): add schema migrations and RLS policies"
git push -u origin feat/<feature>-1-data
gh pr create --base main --title "feat(data): schema and migrations for <feature>" --body "..."

# 2. Middle Layer (Backend Developer - Stacked on PR 1)
git checkout feat/<feature>-1-data
git checkout -b feat/<feature>-2-api
# Backend Developer finishes changes & static check
git add <backend-files>
git commit -m "feat(api): implement domain logic and endpoints"
git push -u origin feat/<feature>-2-api
gh pr create --base feat/<feature>-1-data --title "feat(api): backend endpoints for <feature>" --body "..."

# 3. Top Layer (Frontend Developer - Stacked on PR 2)
git checkout feat/<feature>-2-api
git checkout -b feat/<feature>-3-ui
# Frontend Developer finishes changes & static check
git add <frontend-files>
git commit -m "feat(ui): responsive user interface for <feature>"
git push -u origin feat/<feature>-3-ui
gh pr create --base feat/<feature>-2-api --title "feat(ui): client components for <feature>" --body "..."
```

---

## 3. Propagation & Rebasing
When changes occur in an earlier layer of the stack during review, the Committer propagates them cleanly:

```bash
git checkout feat/<feature>-2-api
git rebase feat/<feature>-1-data
git push --force-with-lease origin feat/<feature>-2-api

git checkout feat/<feature>-3-ui
git rebase feat/<feature>-2-api
git push --force-with-lease origin feat/<feature>-3-ui
```
