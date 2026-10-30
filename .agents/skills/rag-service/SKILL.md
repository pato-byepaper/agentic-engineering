---
name: rag-service
description: Advanced regex-based Markdown RAG service for large context files. Extracts hierarchical sections, Mermaid diagrams, code blocks, alerts/invariants, tables, sub-agent assignments (@agent-name), task checklists, acceptance criteria, and API endpoints without blowing up token usage.
---

# Markdown RAG Service (Advanced Context Extraction)

You use this service to manage, persist, and retrieve large context files without overflowing the model's token window.

> [!IMPORTANT]
> **Token-Efficiency Rule**: NEVER read an entire large context file at once.
> 1. Run `get-topics` first to discover what topics (`#`), subtopics (`##`), and deep sections (`###`) exist along with line numbers, estimated token counts, task counts, and assigned agents.
> 2. For sub-agents: run `extract-agent-assignments` (e.g. `--agent backend-developer`) or `extract-tasks` to pull **ONLY** your assigned work.
> 3. For testers & managers: run `extract-acceptance-criteria` to pull verifiable criteria and non-negotiable rules.
> 4. Use specialized regex extractors (`extract-diagrams`, `extract-code-blocks`, `extract-alerts`, `extract-tables`, `extract-endpoints`, `extract-env-vars`, `search-rag`) to pull only specific data needed.

---

## Python Regex Operations & Capabilities

All extraction functions use targeted Python regex to parse structured markdown on disk:

### 1. Discover Topics & Sections (`get-topics`)
Discovers all headings `#` through `######` with start/end line boundaries, estimated token usage, pending/completed task metrics, and assigned sub-agents.

**CLI**:
```bash
python3 .agents/tools/rag_service.py get-topics [--depth 4] [--file path/to/file.md]
```
**MCP**: `get_topics(file_path="...", depth=4)`

---

### 2. Extract Sub-Agent In Charge & Assignments (`extract-agent-assignments`)
Extracts tasks, checklists, and instruction blocks assigned to sub-agents via `@agent-name` (e.g. `@backend-developer`, `@data-engineer`, `@frontend-developer`, `@tester`, `@tech-lead`, `@committer`) or `sub-agent-in-charge: <agent>`.

**CLI**:
```bash
# Extract all tasks assigned to backend developer:
python3 .agents/tools/rag_service.py extract-agent-assignments --agent backend-developer --file plans/feature.md

# Extract all agent assignments across document:
python3 .agents/tools/rag_service.py extract-agent-assignments --file plans/feature.md
```
**MCP**: `extract_agent_assignments(agent="backend-developer", file_path="...")`

---

### 3. Extract Task Checklists (`extract-tasks`)
Extracts markdown checklist items (`- [ ]` pending, `- [x]` completed), optionally filtered by status (`pending`, `completed`, `all`) or assigned agent.

**CLI**:
```bash
# Extract pending tasks:
python3 .agents/tools/rag_service.py extract-tasks --status pending --file plans/feature.md

# Extract completed tasks for frontend:
python3 .agents/tools/rag_service.py extract-tasks --status completed --agent frontend-developer --file plans/feature.md
```
**MCP**: `extract_tasks(status="pending", agent="frontend-developer", file_path="...")`

---

### 4. Extract Acceptance Criteria & Invariants (`extract-acceptance-criteria`)
Extracts sections containing Acceptance Criteria, Definition of Done, Invariants, or Non-Negotiable Rules. Essential for Manager validation and Tester test generation!

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-acceptance-criteria --file tickets/issue-123.md
```
**MCP**: `extract_acceptance_criteria(file_path="...")`

---

### 5. Extract In-Between Lines (`extract-from-rag`)
Reads **ONLY** the in-between lines for the targeted section, stopping at the next heading of equal or higher level.

**CLI**:
```bash
# By topic and subtopic:
python3 .agents/tools/rag_service.py extract-from-rag --topic "Database Architecture" --subtopic "PostgreSQL Indexes"

# By deep section title:
python3 .agents/tools/rag_service.py extract-from-rag --topic "Architecture" --section "Cache Invalidation Policy"
```
**MCP**: `extract_from_rag(topic="Database Architecture", subtopic="PostgreSQL Indexes")`

---

### 6. Extract Mermaid Diagrams (`extract-diagrams`)
Finds all ````mermaid ... ```` blocks using regex `r'```mermaid\s*\n(.*?)```'` without loading surrounding prose.

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-diagrams [--topic "Architecture"] [--file path/to/file.md]
```
**MCP**: `extract_diagrams(topic="Architecture", file_path="...")`

---

### 7. Extract Code Blocks by Language (`extract-code-blocks`)
Extracts fenced code snippets filtered by language (`sql`, `typescript`, `python`, `bash`, `json`).

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-code-blocks --language sql [--file path/to/file.md]
```
**MCP**: `extract_code_blocks(language="sql", file_path="...")`

---

### 8. Extract Invariants & Safety Alerts (`extract-alerts`)
Extracts GitHub-style callouts (`> [!WARNING]`, `> [!DANGER]`, `> [!IMPORTANT]`, `> [!CAUTION]`). Always run this before editing high-risk files!

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-alerts [--type DANGER] [--file path/to/file.md]
```
**MCP**: `extract_alerts(type="WARNING", file_path="...")`

---

### 9. Extract Markdown Tables (`extract-tables`)
Parses data tables into structured columns and rows using regex `r'(?:^\|.+?\|\s*$\n?){2,}'`.

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-tables [--file path/to/file.md]
```
**MCP**: `extract_tables(file_path="...")`

---

### 10. Extract HTTP Endpoints & Contracts (`extract-endpoints`)
Extracts all API endpoints (`GET /...`, `POST /...`, `PUT /...`, `DELETE /...`) defined across markdown documents with enclosing section context.

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-endpoints [--file docs/api/spec.md]
```
**MCP**: `extract_endpoints(file_path="...")`

---

### 11. Extract Environment Variables & Config (`extract-env-vars`)
Extracts configuration keys and environment variables (e.g. `DATABASE_URL`, `SUPABASE_KEY`).

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-env-vars [--file docs/setup.md]
```
**MCP**: `extract_env_vars(file_path="...")`

---

### 12. Extract YAML Frontmatter (`extract-frontmatter`)
Extracts header frontmatter metadata (`--- ... ---`).

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-frontmatter --file .agents/skills/rag-service/SKILL.md
```
**MCP**: `extract_frontmatter(file_path="...")`

---

### 13. Section-Bounded Search (`search-rag`)
Searches for text or regex patterns and returns **ONLY** the enclosing section lines and line numbers.

**CLI**:
```bash
python3 .agents/tools/rag_service.py search-rag --query "Row Level Security" [--regex] [--file path/to/file.md]
```
**MCP**: `search_rag(query="Row Level Security", regex=False, file_path="...")`

---

### 14. Save & Append Context (`save-in-rag`)
Appends or updates notes under a heading.

**CLI**:
```bash
python3 .agents/tools/rag_service.py save-in-rag \
  --topic "Auth" \
  --subtopic "Tokens" \
  --content "JWT tokens expire after 1 hour." \
  --mode append
```
**MCP**: `save_in_rag(topic="Auth", subtopic="Tokens", content="...", mode="append")`
