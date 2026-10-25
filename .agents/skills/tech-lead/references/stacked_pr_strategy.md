# Stacked Pull Requests Strategy (`gh stack`)

Stacked PRs break down large, cross-cutting features into small, atomic, and reviewable pull requests that depend on one another.

---

## 1. The Stack Sequence

```mermaid
flowchart LR
    Main["main"] <-- "PR 1 (Base)" -- Branch1["feat/01-data-model"]
    Branch1 <-- "PR 2 (Stacked)" -- Branch2["feat/02-backend-api"]
    Branch2 <-- "PR 3 (Stacked)" -- Branch3["feat/03-frontend-ui"]
```

1. **Layer 1: Data Engineer (PR 1)**
   - Contains database migrations, indexing, and RLS policies.
   - Base branch: `main`.
2. **Layer 2: Backend Developer (PR 2)**
   - Implements business logic and API endpoints consuming Layer 1.
   - Base branch: `feat/01-data-model`.
3. **Layer 3: Frontend Developer (PR 3)**
   - Builds UI components and client state consuming Layer 2 contracts.
   - Base branch: `feat/02-backend-api`.

---

## 2. Git Branching Commands

```bash
# 1. Base Layer
git checkout main
git checkout -b feat/01-data-model
# ... implement and commit ...
gh pr create --base main --title "feat(data): add feature schema and RLS"

# 2. Middle Layer (Stacked)
git checkout feat/01-data-model
git checkout -b feat/02-backend-api
# ... implement and commit ...
gh pr create --base feat/01-data-model --title "feat(backend): implement feature API"

# 3. Top Layer (Stacked)
git checkout feat/02-backend-api
git checkout -b feat/03-frontend-ui
# ... implement and commit ...
gh pr create --base feat/02-backend-api --title "feat(frontend): user interface for feature"
```

---

## 3. Handling Upstream Updates & Rebasing

When PR 1 receives changes during review, propagate changes down the stack:

```bash
# Rebase PR 2 on updated PR 1
git checkout feat/02-backend-api
git rebase feat/01-data-model

# Rebase PR 3 on updated PR 2
git checkout feat/03-frontend-ui
git rebase feat/02-backend-api
```

---

## 4. Merging Order

Merge sequentially from base to top:
1. Merge PR 1 into `main`.
2. Update PR 2's base to `main` and merge.
3. Update PR 3's base to `main` and merge.
*(If using `gh-stack` or automated tooling, this is handled automatically)*.
