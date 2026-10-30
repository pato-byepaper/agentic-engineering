---
name: rag-service
description: Manages large markdown context files via regex-based topic extraction. Minimizes token usage by discovering topics and reading ONLY the in-between lines (# title, ## subtitle). Use when saving large context or extracting specific sections.
---

# Markdown RAG Service (Token-Efficient Context Memory)

You use this service to manage, persist, and retrieve large context files without overflowing the model's token window.

> [!IMPORTANT]
> **Token-Efficiency Rule**: NEVER read an entire large context file at once.
> 1. First run `get-topics` to discover what topics (`#`) and subtopics (`##`) exist along with their line numbers.
> 2. ONLY THEN run `extract-from-rag` to read the exact in-between lines for that topic/subtopic.

---

## Architecture & Markdown Format

The context file is organized cleanly with markdown headings:
```markdown
# Topic Title
General overview and invariants...

## Subtopic Title
Specific details, schema definitions, or endpoint notes...
```

The underlying Python regex functions (`.agents/tools/rag_service.py`):
- Find where `# ` or `## ` starts.
- Find where the section ends (right where the next `# ` or `## ` starts, or end of file).
- Reads and returns **ONLY** the in-between lines.

---

## Operations & Tool Calls

### 1. Discover Topics (`get-topics`)
Discovers all topics and subtopics in the context file with line boundaries without reading the full body text.

**CLI Execution**:
```bash
python3 .agents/tools/rag_service.py get-topics [--file .agents/context/knowledge_base.md]
```

**MCP Tool Call**:
`get_topics(file_path=".agents/context/knowledge_base.md")`

### 2. Extract Lines for Topic / Subtopic (`extract-from-rag`)
Reads only the in-between lines for the targeted section.

**CLI Execution**:
```bash
# Extract full topic:
python3 .agents/tools/rag_service.py extract-from-rag --topic "Database Architecture"

# Extract specific subtopic:
python3 .agents/tools/rag_service.py extract-from-rag --topic "Database Architecture" --subtopic "Row Level Security"
```

**MCP Tool Call**:
`extract_from_rag(topic="Database Architecture", subtopic="Row Level Security")`

### 3. Save Context (`save-in-rag`)
Appends or updates context under `# ` or `## ` headings.

**CLI Execution**:
```bash
python3 .agents/tools/rag_service.py save-in-rag \
  --topic "Auth Service" \
  --subtopic "JWT Verification" \
  --content "Tokens must be signed with RS256 and rotated every 24h."
```

**MCP Tool Call**:
`save_in_rag(topic="Auth Service", subtopic="JWT Verification", content="Tokens must be signed with RS256.")`

---

## Default Storage Location
- Default Context File: `.agents/context/knowledge_base.md`
- Project Specific Notes: Can be targeted by passing `--file path/to/file.md`
