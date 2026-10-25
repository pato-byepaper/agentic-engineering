# Subagents Architecture & Declarations

This directory defines the **Actors / Personas** of the autonomous engineering team.

## Subagents vs. Skills

```mermaid
flowchart LR
    subgraph Subagents [WHO Does the Work]
        A["Subagent Persona (.agents/subagents/)"]
        A --> Model["Model & Tools Configuration"]
        A --> Prompt["Role System Prompt"]
    end

    subgraph Skills [HOW Work Is Executed]
        S["Skills (.agents/skills/)"]
        S --> Runbook["SKILL.md (Procedures)"]
        S --> Tools["Scripts, Templates, References"]
    end

    A -->|"Mounts & Executes"| S
```

- **Skills (`.agents/skills/`)**:
  - Encapsulate procedures, checklists, scripts, and domain knowledge.
  - Examples: `git-publisher`, `schema-review`, `core-web-vitals`, `create-skill`.
  - Reusable across any agent or called on demand.

- **Subagents (`.agents/subagents/`)**:
  - Represent autonomous engineering roles.
  - Define tool access (`enableWriteTools`, `enableSubagentTools`, `enableMCPTools`), execution model (`pro`, `flash`, `inherit`), workspace isolation (`branch`, `share`, `inherit`), and which skills they mount.

---

## Registered Team Subagents

| Subagent | Role | Workspace | Mounted Skills | Permissions | Mandatory Responsibility |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`manager`** | Product & UX Orchestrator | `inherit` | `manager` | Write, Subagents | Multi-ticket intake, capability mapping, autonomous dispatch |
| **`tech-lead`** | System Architect & Coordinator | `inherit` | `tech-lead`, `planner`, `git-publisher` | Write, Subagents | Decomposes tickets into sub-tasks, plans **at least 3 stacked PRs**, autonomous dispatch |
| **`data-engineer`** | Database & Schema Specialist | `branch` | `data-engineer`, `git-publisher` | Write | Schema review, zero testing, hands off to committer (PR 1: Base) |
| **`backend-developer`** | API & Domain Engineer | `branch` | `backend-developer`, `git-publisher` | Write | Domain logic, zero testing, hands off to committer (PR 2: Stacked on PR 1) |
| **`frontend-developer`** | Client & Web Vitals Engineer | `branch` | `frontend-developer`, `git-publisher` | Write | Core Web Vitals UI, zero testing, hands off to committer (PR 3: Stacked on PR 2) |
| **`committer`** / **`git-publisher`** | Committer & PR Publisher | `inherit` | `git-publisher` | Write | **At least 1 commit per task**, builds stacked PRs, zero emojis/AI tags |
| **`tester`** | Independent Verification | `share` | `tester` | Write, MCP | **Exclusive owner of test creation & execution**, live UI verification |

---

## The `TEAM` Trigger Autonomous Execution Flow

When triggered with `TEAM` or `TEAM resolve`:
```mermaid
sequenceDiagram
    autonumber
    actor User as User (Prompt: "TEAM resolve tickets...")
    participant M as Manager
    participant TL as Tech Lead
    participant DE as Data Engineer
    participant BE as Backend Developer
    participant FE as Frontend Developer
    participant GP as Committer (Git Publisher)
    participant T as Tester

    User->>M: Human tickets (1, 2, ...)
    Note over M: Maps capabilities, services & UX promises
    M->>TL: Unified Product Capability Brief
    Note over TL: Decomposes into sub-tasks & enforces 3 Stacked PRs
    TL->>DE: Sub-ticket 1: Schemas & RLS
    DE->>GP: Task finished -> Auto commit & create PR 1 (Base -> main)
    TL->>BE: Sub-ticket 2: APIs & Domain Logic
    BE->>GP: Task finished -> Auto commit & create PR 2 (Stacked -> PR 1)
    TL->>FE: Sub-ticket 3: UI & Core Web Vitals
    FE->>GP: Task finished -> Auto commit & create PR 3 (Stacked -> PR 2)
    TL->>T: 3 Stacked PRs ready for testing
    Note over T: Exclusively writes and runs all tests + UI verification
    T->>M: test-results/<issue>.md
    M->>User: Final Product Acceptance
```
