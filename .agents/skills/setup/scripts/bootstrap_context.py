#!/usr/bin/env python3
"""
bootstrap_context.py
Scans the current repository and populates specialized 'context/' directories
inside each agent's skill folder. This turns generic base skills into project-specific
expert agents with zero context loss.
"""

import json
import os
import subprocess
from pathlib import Path


def run_cmd(cmd: str) -> str:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=False)
        return res.stdout.strip()
    except Exception:
        return ""


def detect_git_info(root: Path):
    branch = run_cmd("git branch --show-current") or "main"
    remote = run_cmd("git remote get-url origin") or "Not configured"
    return {"default_branch": branch, "remote": remote}


def detect_stack(root: Path):
    stack = {
        "languages": [],
        "package_manager": "unknown",
        "backend": "unknown",
        "frontend": "unknown",
        "database": "unknown",
        "orm_or_migrations": "unknown",
        "testing": "unknown",
        "styling": "unknown",
        "monorepo": False,
        "entrypoints": []
    }

    # 1. Check monorepo
    if (root / "pnpm-workspace.yaml").exists() or (root / "lerna.json").exists() or (root / "turborepo.json").exists():
        stack["monorepo"] = True

    # 2. Check Node / JS / TS
    pkg_json_path = root / "package.json"
    if pkg_json_path.exists():
        try:
            with open(pkg_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            stack["languages"].append("TypeScript" if (root / "tsconfig.json").exists() or "typescript" in deps else "JavaScript")

            # Package manager
            if (root / "pnpm-lock.yaml").exists():
                stack["package_manager"] = "pnpm"
            elif (root / "yarn.lock").exists():
                stack["package_manager"] = "yarn"
            elif (root / "bun.lockb").exists():
                stack["package_manager"] = "bun"
            else:
                stack["package_manager"] = "npm"

            # Frontend detection
            if "next" in deps:
                stack["frontend"] = f"Next.js ({deps.get('next')})"
            elif "react" in deps:
                stack["frontend"] = f"React ({deps.get('react')})"
            elif "vue" in deps:
                stack["frontend"] = f"Vue ({deps.get('vue')})"
            elif "svelte" in deps or "@sveltejs/kit" in deps:
                stack["frontend"] = "Svelte / SvelteKit"
            elif "astro" in deps:
                stack["frontend"] = "Astro"

            # Styling
            if "tailwindcss" in deps:
                stack["styling"] = "Tailwind CSS"
            elif "@emotion/react" in deps or "styled-components" in deps:
                stack["styling"] = "CSS-in-JS"

            # Backend detection
            if "@nestjs/core" in deps:
                stack["backend"] = "NestJS"
            elif "express" in deps:
                stack["backend"] = "Express.js"
            elif "fastify" in deps:
                stack["backend"] = "Fastify"
            elif "next" in deps and stack["backend"] == "unknown":
                stack["backend"] = "Next.js API Routes / Server Actions"

            # Database & ORM
            if "prisma" in deps or "@prisma/client" in deps or (root / "prisma").exists():
                stack["orm_or_migrations"] = "Prisma"
            elif "drizzle-orm" in deps:
                stack["orm_or_migrations"] = "Drizzle ORM"
            elif "typeorm" in deps:
                stack["orm_or_migrations"] = "TypeORM"
            elif "mongoose" in deps:
                stack["database"] = "MongoDB"
                stack["orm_or_migrations"] = "Mongoose"
            elif "pg" in deps or "@vercel/postgres" in deps:
                stack["database"] = "PostgreSQL"
            elif "mysql2" in deps:
                stack["database"] = "MySQL"
            elif "better-sqlite3" in deps or "sqlite3" in deps:
                stack["database"] = "SQLite"

            # Testing
            test_runners = []
            if "vitest" in deps:
                test_runners.append("Vitest")
            if "jest" in deps:
                test_runners.append("Jest")
            if "@playwright/test" in deps:
                test_runners.append("Playwright")
            if "cypress" in deps:
                test_runners.append("Cypress")
            if test_runners:
                stack["testing"] = ", ".join(test_runners)
        except Exception as e:
            pass

    # 3. Check Python
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists() or (root / "Pipfile").exists():
        stack["languages"].append("Python")
        if (root / "poetry.lock").exists():
            stack["package_manager"] = "Poetry"
        elif (root / "Pipfile").exists():
            stack["package_manager"] = "Pipenv"
        elif (root / "pyproject.toml").exists():
            stack["package_manager"] = "uv / pip / flit"

        reqs = ""
        for req_file in ["requirements.txt", "pyproject.toml"]:
            p = root / req_file
            if p.exists():
                reqs += p.read_text(encoding="utf-8", errors="ignore")

        if "fastapi" in reqs.lower():
            stack["backend"] = "FastAPI"
        elif "django" in reqs.lower():
            stack["backend"] = "Django"
        elif "flask" in reqs.lower():
            stack["backend"] = "Flask"

        if "sqlalchemy" in reqs.lower():
            stack["orm_or_migrations"] = "SQLAlchemy / Alembic"
        elif "psycopg" in reqs.lower():
            stack["database"] = "PostgreSQL"

        if "pytest" in reqs.lower():
            stack["testing"] = "Pytest"

    # 4. Check Go
    if (root / "go.mod").exists():
        stack["languages"].append("Go")
        stack["package_manager"] = "Go Modules"
        stack["testing"] = "go test"

    # 5. Check Rust
    if (root / "Cargo.toml").exists():
        stack["languages"].append("Rust")
        stack["package_manager"] = "Cargo"
        stack["testing"] = "cargo test"

    # Deduplicate languages
    stack["languages"] = list(set(stack["languages"]))
    if not stack["languages"]:
        stack["languages"] = ["General / Unspecified"]

    return stack


def write_file_if_needed(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {path}")


def populate_agent_contexts(root: Path, stack: dict, git_info: dict):
    skills_dir = root / ".agents" / "skills"
    proj_name = root.resolve().name

    langs_str = ", ".join(stack["languages"])
    pkg_str = stack["package_manager"]
    be_str = stack["backend"]
    fe_str = stack["frontend"]
    db_str = stack["database"]
    orm_str = stack["orm_or_migrations"]
    test_str = stack["testing"]
    styling_str = stack["styling"]

    # 1. Manager Context
    mgr_ctx = f"""# Project Overview & Business Domain: {proj_name}

## Business Objective & Vision
- **Project**: {proj_name}
- **Primary Domain**: [To be refined with user during setup interview]
- **Target Audience / End Users**: [To be refined with user]

## Architectural Summary
- **Languages / Core Stack**: {langs_str}
- **Frontend Layer**: {fe_str}
- **Backend Services**: {be_str}
- **Data Persistence**: {db_str} (ORM/Migrations: {orm_str})

## Key Invariants for Manager
- Never inspect or edit source code directly.
- Natively ingest multi-ticket requests and map high-level capabilities, services, promises, and acceptance criteria.
- Autonomous dispatch: Hand off directly to Tech Lead without waiting for manual human prompts.
- Enforce strict testing separation: developers never write or execute tests; only `tester` writes and executes tests.
- Accept feature completion only via Tester verification book (`test-results/<issue>.md`).
"""
    write_file_if_needed(skills_dir / "manager" / "context" / "project_overview.md", mgr_ctx)

    # 2. Tech Lead Context
    tl_ctx = f"""# Architecture & Technical Roadmap: {proj_name}

## System Topology & Contracts
- **Primary Languages**: {langs_str}
- **Backend Architecture**: {be_str}
- **Frontend Architecture**: {fe_str}
- **Database Engine & ORM**: {db_str} | {orm_str}
- **Package Management**: {pkg_str}

## Engineering Standards, Full-Team Flow & Mandatory 3 Stacked PRs
- **Full-Team Pipeline**: `manager` -> `tech-lead` (`planner`) -> `data-engineer` -> `backend-developer` -> `frontend-developer` -> `code-reviewer` -> `tester` -> `doc-maintainer` / `git-publisher`.
- **Mandatory At Least 3 Stacked PRs**: For full-stack features touching data, backend, and frontend, enforce at least 3 stacked PRs (`PR 1: Data -> main`, `PR 2: Backend -> PR 1`, `PR 3: Frontend -> PR 2`).
- **Autonomous Dispatch**: Actively invoke subagents without waiting for manual human prompts.
- **Contracts First**: Contracts must be explicitly defined (interfaces / schemas) before coders start work.
- **Strict Testing Separation**: Coders NEVER write or execute tests (only static compilation checks like `npx tsc --noEmit`). Only `tester` writes and executes unit, integration, component, and E2E tests.
"""
    write_file_if_needed(skills_dir / "tech-lead" / "context" / "architecture.md", tl_ctx)

    # 3. Data Engineer Context
    de_ctx = f"""# Data Layer & Database Stack: {proj_name}

## Database Configuration
- **Database Engine**: {db_str}
- **ORM / Query Builder / Migrations**: {orm_str}
- **Migration Directory / Tooling**: [Check schema files in repo]

## Mandatory Invariants
- **Always review schema first** before code is written.
- Check indexing on foreign keys and high-frequency filter columns.
- Ensure Row Level Security (RLS) policies exist if multi-tenant isolation is required.
- Write reversible, zero-downtime migrations.
- Base of the stack: Forms PR 1 (`feat/<feature>-1-data` targeting `main`).

## Verification, Testing Separation & Committer Handoff
- **STRICT INVARIANT**: Developers NEVER write or run unit, integration, or E2E tests. Only the `tester` subagent is authorized to write and execute tests so that no developer can self-certify passing tests.
- **At Least 1 Commit Per Task**: As soon as schema changes and syntax checks pass, immediately hand off to Committer (`git-publisher`) to create at least one commit on the stacked branch.
- Do not manually push to production; CI/CD executes migrations.
"""
    write_file_if_needed(skills_dir / "data-engineer" / "context" / "data_stack.md", de_ctx)

    # 4. Backend Developer Context
    be_ctx = f"""# Backend Stack & API Conventions: {proj_name}

## Server Architecture
- **Framework / Runtime**: {be_str}
- **Language**: {langs_str}
- **Data Layer Integration**: Interacts via {orm_str} / {db_str}
- **Stacked Branch**: `feat/<feature>-2-api` (PR 2, targeting `feat/<feature>-1-data`)

## Operating Guidelines
- Follow contracts defined by Tech Lead.
- Standard error responses and input validation on all routes.
- Commit clean code referencing issues without emojis or AI co-author tags.

## Verification, Testing Separation & Committer Handoff
- **STRICT INVARIANT**: Developers NEVER write or run their own unit, integration, or E2E tests. Only the `tester` subagent is authorized to write and execute tests so that no developer can self-certify passing tests.
- Developers may run `npx tsc --noEmit` to verify compilation before handing off.
- **At Least 1 Commit Per Task**: As soon as code changes and type checks pass, immediately hand off to Committer (`git-publisher`) to commit on `feat/<feature>-2-api` and update the stacked PR. Never leave tasks uncommitted.
"""
    write_file_if_needed(skills_dir / "backend-developer" / "context" / "backend_stack.md", be_ctx)

    # 5. Frontend Developer Context
    fe_ctx = f"""# Frontend Stack & Performance Targets: {proj_name}

## Client Architecture
- **Framework**: {fe_str}
- **Styling Solution**: {styling_str}
- **Package Manager**: {pkg_str}
- **Stacked Branch**: `feat/<feature>-3-ui` (PR 3, targeting `feat/<feature>-2-api`)

## Google Core Web Vitals Targets
- **LCP (Largest Contentful Paint)**: < 2.5s (preload hero media, optimize server rendering).
- **INP (Interaction to Next Paint)**: < 200ms (avoid main thread blocking, optimistic UI).
- **CLS (Cumulative Layout Shift)**: < 0.1 (explicit width/height, reserve aspect-ratio containers).

## Strict Testing Separation & Committer Handoff
- **NEVER write or execute your own tests**: Only the `tester` subagent creates and runs unit, component, and Playwright E2E tests so that no developer can self-certify passing tests.
- Only run `npx tsc --noEmit` to verify compilation and provide a local preview URL.
- **At Least 1 Commit Per Task**: Immediately hand off to Committer (`git-publisher`) upon completing UI changes to commit on `feat/<feature>-3-ui` and update the stacked PR.
"""
    write_file_if_needed(skills_dir / "frontend-developer" / "context" / "frontend_stack.md", fe_ctx)

    # 6. Tester Context
    tester_ctx = f"""# Testing Stack & Verification Guide: {proj_name}

## Test Environment
- **Test Runner / Framework**: {test_str}
- **Verification Target Directory**: `test-results/<issue>.md`

## Exclusive Testing Authority & Operating Guidelines
- **EXCLUSIVE OWNER**: Only the `tester` subagent is authorized to write and execute unit, component, integration, and E2E tests. Developers (`data-engineer`, `backend-developer`, `frontend-developer`, `coder`) NEVER write or run tests.
- Perform independent verification against acceptance criteria.
- Never fix bugs or touch production files.
- Always include raw command outputs and live UI verification proofs in the Test Result Book.
"""
    write_file_if_needed(skills_dir / "tester" / "context" / "test_stack.md", tester_ctx)

    # 7. Git Publisher Context
    git_ctx = f"""# Git & Repository Conventions: {proj_name}

## Repository Settings
- **Default Branch**: {git_info['default_branch']}
- **Remote**: {git_info['remote']}

## Rules
- **At Least 1 Commit Per Task**: Proactively commit developer changes as soon as tasks finish without waiting for manual human prompts.
- **Mandatory At Least 3 Stacked PRs**: For full-stack features, enforce the 3-PR stack (`PR 1: Data -> main`, `PR 2: Backend -> PR 1`, `PR 3: Frontend -> PR 2`).
- Never add emojis, AI Co-Authored trailers, or AI watermarks.
- Follow Conventional Commits: `feat:`, `fix:`, `refactor:`, `test:`, `chore:`.
- Include dual simple `()->()->` Mermaid diagrams in PR descriptions.
"""
    write_file_if_needed(skills_dir / "git-publisher" / "context" / "git_conventions.md", git_ctx)

    # 8. RAG Knowledge Base and Relationship Graph Scaffolding
    kb_path = root / ".agents" / "context" / "knowledge_base.md"
    if not kb_path.exists():
        kb_content = f"""# Knowledge Base: {proj_name}

Core architecture invariants, domain notes, and large context repository.

## System Topology
- Project: {proj_name}
- Stack: {langs_str} ({fe_str} | {be_str} | {db_str})
- Orchestration: Multi-agent autonomous workflow via AGY Gemini models.

## Architecture Invariants
- Mandatory at least 3 stacked PRs for full-stack tasks.
- Zero developer self-testing (assigned exclusively to tester).
- At least 1 commit per task via Committer.
"""
        write_file_if_needed(kb_path, kb_content)

    graph_path = root / ".agents" / "graph" / "dependencies.json"
    if not graph_path.exists():
        graph_data = {
            "version": "1.0",
            "project": proj_name,
            "nodes": {
                proj_name: {"label": proj_name}
            },
            "edges": []
        }
        write_file_if_needed(graph_path, json.dumps(graph_data, indent=2))
        write_file_if_needed(root / ".agents" / "graph" / "dependencies.mmd", f"flowchart TD\n    {proj_name}[\"{proj_name}\"]\n")


def main():
    root = Path.cwd()
    print(f"==> Bootstrapping project context in: {root}")
    stack = detect_stack(root)
    git_info = detect_git_info(root)
    populate_agent_contexts(root, stack, git_info)
    print("==> Context directories populated for all specialist agents successfully.")


if __name__ == "__main__":
    main()
