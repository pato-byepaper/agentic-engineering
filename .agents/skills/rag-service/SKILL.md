---
name: rag-service
description: Advanced regex-based Markdown RAG service for large context files. Extracts hierarchical sections, Mermaid diagrams, code blocks, alerts/invariants, tables, and searches without blowing up token usage.
---

# Markdown RAG Service (Advanced Context Extraction)

You use this service to manage, persist, and retrieve large context files without overflowing the model's token window.

> [!IMPORTANT]
> **Token-Efficiency Rule**: NEVER read an entire large context file at once.
> 1. Run `get-topics` first to discover what topics (`#`), subtopics (`##`), and deep sections (`###`) exist along with line numbers.
> 2. ONLY THEN run `extract-from-rag` to read the exact in-between lines for that section.
> 3. Use specialized regex extractors (`extract-diagrams`, `extract-code-blocks`, `extract-alerts`, `extract-tables`, `search-rag`) to pull only the specific data needed.

---

## Python Regex Operations & Capabilities

All extraction functions use targeted Python regex to parse structured markdown on disk:

### 1. Discover Topics & Sections (`get-topics`)
Discovers all headings `#` through `######` with start/end line boundaries.

**CLI**:
```bash
python3 .agents/tools/rag_service.py get-topics [--depth 4] [--file path/to/file.md]
```
**MCP**: `get_topics(file_path="...", depth=4)`

---

### 2. Extract In-Between Lines (`extract-from-rag`)
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

### 3. Extract Mermaid Diagrams (`extract-diagrams`)
Finds all ````mermaid ... ```` blocks using regex `r'```mermaid\s*\n(.*?)```'` without loading surrounding prose.

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-diagrams [--topic "Architecture"] [--file path/to/file.md]
```
**MCP**: `extract_diagrams(topic="Architecture", file_path="...")`

---

### 4. Extract Code Blocks by Language (`extract-code-blocks`)
Extracts fenced code snippets filtered by language (`sql`, `typescript`, `python`, `bash`, `json`).

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-code-blocks --language sql [--file path/to/file.md]
```
**MCP**: `extract_code_blocks(language="sql", file_path="...")`

---

### 5. Extract Invariants & Safety Alerts (`extract-alerts`)
Extracts GitHub-style callouts (`> [!WARNING]`, `> [!DANGER]`, `> [!IMPORTANT]`, `> [!CAUTION]`). Always run this before editing high-risk files!

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-alerts [--type DANGER] [--file path/to/file.md]
```
**MCP**: `extract_alerts(type="WARNING", file_path="...")`

---

### 6. Extract Markdown Tables (`extract-tables`)
Parses data tables into structured columns and rows using regex `r'(?:^\|.+?\|\s*$\n?){2,}'`.

**CLI**:
```bash
python3 .agents/tools/rag_service.py extract-tables [--file path/to/file.md]
```
**MCP**: `extract_tables(file_path="...")`

---

### 7. Section-Bounded Search (`search-rag`)
Searches for text or regex patterns and returns **ONLY** the enclosing section lines and line numbers.

**CLI**:
```bash
python3 .agents/tools/rag_service.py search-rag --query "Row Level Security" [--regex] [--file path/to/file.md]
```
**MCP**: `search_rag(query="Row Level Security", regex=False, file_path="...")`

---

### 8. Save & Append Context (`save-in-rag`)
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
