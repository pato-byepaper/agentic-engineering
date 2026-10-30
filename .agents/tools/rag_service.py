#!/usr/bin/env python3
"""
rag_service.py - Advanced Markdown-based RAG service for large context files.
Enables token-efficient retrieval by using Python regex to:
1. Discover hierarchical topics (# through ######) and extract ONLY the lines in between.
2. Extract all Mermaid diagrams (flowcharts, sequence diagrams, ERDs) without reading surrounding prose.
3. Extract code blocks by language (sql, ts, python, bash, json).
4. Extract alerts and critical invariants (> [!WARNING], > [!DANGER], > [!IMPORTANT]).
5. Extract structured markdown tables.
6. Search by keyword/pattern to pull only matching sections.
Designed for AGY Gemini models.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DEFAULT_RAG_FILE = Path(".agents/context/knowledge_base.md")

# Heading regex matching # through ######
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# Mermaid fenced code block regex
MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)
# Generic code block regex with optional language tag
CODE_BLOCK_PATTERN = re.compile(r"```([a-zA-Z0-9_\-\+]+)?\s*\n(.*?)```", re.DOTALL)
# Markdown alert/callout regex (> [!TYPE])
ALERT_PATTERN = re.compile(r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|DANGER)\]\s*\n((?:^>.*$\n?)*)", re.MULTILINE)
# Markdown table regex (header + separator + rows)
TABLE_PATTERN = re.compile(r"((?:^\|.+?\|\s*$\n?){2,})", re.MULTILINE)


def ensure_file_exists(file_path: Path) -> Path:
    """Ensures the parent directory and file exist."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        file_path.write_text("# Knowledge Base\n\nInitial repository context.\n", encoding="utf-8")
    return file_path


def parse_headings_with_boundaries(lines: List[str], max_depth: int = 6) -> List[Dict[str, Any]]:
    """
    Parses all headings (# through ######) and calculates precise start_line and end_line
    boundaries where the next heading of equal or higher level appears.
    """
    total_lines = len(lines)
    headings = []
    line_heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$")

    for idx, line in enumerate(lines, start=1):
        match = line_heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            if level <= max_depth:
                headings.append({
                    "level": level,
                    "title": match.group(2).strip(),
                    "start_line": idx,
                    "end_line": total_lines
                })

    # Adjust end_line: ends right before the next heading of equal or higher level (<= current level)
    for i in range(len(headings)):
        curr = headings[i]
        for j in range(i + 1, len(headings)):
            next_head = headings[j]
            if next_head["level"] <= curr["level"]:
                curr["end_line"] = next_head["start_line"] - 1
                break

    return headings


def get_topics(file_path: Path = DEFAULT_RAG_FILE, max_depth: int = 4) -> List[Dict[str, Any]]:
    """
    Discovers all headings up to max_depth (# through ####) and builds a nested topic hierarchy
    with start/end line numbers and line counts.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    headings = parse_headings_with_boundaries(lines, max_depth=max_depth)

    # Build hierarchical tree
    root_nodes: List[Dict[str, Any]] = []
    stack: List[Dict[str, Any]] = []

    for h in headings:
        node = {
            "level": h["level"],
            "title": h["title"],
            "start_line": h["start_line"],
            "end_line": h["end_line"],
            "line_count": max(0, h["end_line"] - h["start_line"] + 1),
            "children": []
        }

        while stack and stack[-1]["level"] >= node["level"]:
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
        else:
            root_nodes.append(node)

        stack.append(node)

    return root_nodes


def extract_from_rag(
    topic: str,
    subtopic: Optional[str] = None,
    section: Optional[str] = None,
    file_path: Path = DEFAULT_RAG_FILE
) -> Dict[str, Any]:
    """
    Extracts ONLY the in-between lines for a given topic (#), subtopic (##), or deep section (###).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return {"error": f"File not found: {file_path}", "content": "", "lines_read": 0}

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    headings = parse_headings_with_boundaries(lines, max_depth=6)

    # Find the matching heading
    target_needle = (section or subtopic or topic).strip().lower()
    matched_heading = None

    for h in headings:
        htitle = h["title"].strip().lower()
        if target_needle == htitle or target_needle in htitle or htitle in target_needle:
            matched_heading = h
            break

    if not matched_heading:
        return {
            "error": f"Section matching '{target_needle}' not found in {file_path}",
            "content": "",
            "lines_read": 0
        }

    start_idx = matched_heading["start_line"] - 1
    end_idx = matched_heading["end_line"]

    extracted_lines = lines[start_idx:end_idx]
    return {
        "file": str(file_path),
        "matched_title": matched_heading["title"],
        "level": matched_heading["level"],
        "start_line": matched_heading["start_line"],
        "end_line": matched_heading["end_line"],
        "line_count": len(extracted_lines),
        "content": "".join(extracted_lines)
    }


def extract_diagrams(topic: Optional[str] = None, file_path: Path = DEFAULT_RAG_FILE) -> List[Dict[str, Any]]:
    """
    Extracts all Mermaid diagrams (flowcharts, sequence diagrams, state diagrams, class diagrams)
    from the file or within a specific topic section.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    if topic:
        section_data = extract_from_rag(topic=topic, file_path=file_path)
        raw_text = section_data.get("content", "")
        base_line = section_data.get("start_line", 1)
    else:
        raw_text = file_path.read_text(encoding="utf-8")
        base_line = 1

    diagrams = []
    # Find all mermaid blocks with regex
    for idx, match in enumerate(MERMAID_PATTERN.finditer(raw_text), start=1):
        code = match.group(1).strip()
        first_line = code.splitlines()[0].strip() if code else "unknown"
        diagram_type = first_line.split()[0] if first_line else "unknown"

        # Calculate line position
        start_char = match.start()
        line_offset = raw_text[:start_char].count("\n")
        start_line = base_line + line_offset
        end_line = start_line + match.group(0).count("\n")

        diagrams.append({
            "diagram_index": idx,
            "type": diagram_type,
            "start_line": start_line,
            "end_line": end_line,
            "mermaid_code": code
        })

    return diagrams


def extract_code_blocks(
    language: Optional[str] = None,
    topic: Optional[str] = None,
    file_path: Path = DEFAULT_RAG_FILE
) -> List[Dict[str, Any]]:
    """
    Extracts fenced code blocks matching a specific programming language (e.g. sql, ts, py, bash)
    or all code blocks if language is None.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    if topic:
        section_data = extract_from_rag(topic=topic, file_path=file_path)
        raw_text = section_data.get("content", "")
        base_line = section_data.get("start_line", 1)
    else:
        raw_text = file_path.read_text(encoding="utf-8")
        base_line = 1

    blocks = []
    lang_clean = language.strip().lower() if language else None

    for idx, match in enumerate(CODE_BLOCK_PATTERN.finditer(raw_text), start=1):
        lang = match.group(1) or "plaintext"
        code = match.group(2).strip()

        if lang_clean and lang.lower() != lang_clean:
            continue
        # Skip mermaid if looking for code
        if lang.lower() == "mermaid" and lang_clean != "mermaid":
            continue

        start_char = match.start()
        line_offset = raw_text[:start_char].count("\n")
        start_line = base_line + line_offset
        end_line = start_line + match.group(0).count("\n")

        blocks.append({
            "block_index": idx,
            "language": lang,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": len(code.splitlines()),
            "code": code
        })

    return blocks


def extract_alerts(
    alert_type: Optional[str] = None,
    topic: Optional[str] = None,
    file_path: Path = DEFAULT_RAG_FILE
) -> List[Dict[str, Any]]:
    """
    Extracts GitHub-style callouts/alerts (> [!WARNING], > [!IMPORTANT], > [!CAUTION], > [!DANGER]).
    Essential for checking safety invariants before modifying code!
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    if topic:
        section_data = extract_from_rag(topic=topic, file_path=file_path)
        raw_text = section_data.get("content", "")
        base_line = section_data.get("start_line", 1)
    else:
        raw_text = file_path.read_text(encoding="utf-8")
        base_line = 1

    alerts = []
    type_clean = alert_type.strip().upper() if alert_type else None

    for match in ALERT_PATTERN.finditer(raw_text):
        atype = match.group(1).upper()
        if type_clean and atype != type_clean:
            continue

        body_raw = match.group(2)
        # Strip leading '> ' from each line
        body_lines = [re.sub(r"^>\s?", "", line) for line in body_raw.splitlines()]
        body = "\n".join(body_lines).strip()

        start_char = match.start()
        start_line = base_line + raw_text[:start_char].count("\n")
        end_line = start_line + match.group(0).count("\n")

        alerts.append({
            "type": atype,
            "start_line": start_line,
            "end_line": end_line,
            "content": body
        })

    return alerts


def extract_tables(topic: Optional[str] = None, file_path: Path = DEFAULT_RAG_FILE) -> List[Dict[str, Any]]:
    """
    Extracts and parses all markdown tables into structured columns and rows.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    if topic:
        section_data = extract_from_rag(topic=topic, file_path=file_path)
        raw_text = section_data.get("content", "")
        base_line = section_data.get("start_line", 1)
    else:
        raw_text = file_path.read_text(encoding="utf-8")
        base_line = 1

    tables = []
    for idx, match in enumerate(TABLE_PATTERN.finditer(raw_text), start=1):
        table_raw = match.group(1).strip()
        lines = [l.strip() for l in table_raw.splitlines() if l.strip()]
        if len(lines) < 2:
            continue

        # Header
        headers = [c.strip() for c in lines[0].strip("|").split("|")]
        # Data rows (skip line 1 which is separator like |---|---|)
        rows = []
        for line in lines[2:]:
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) == len(headers):
                rows.append(dict(zip(headers, cols)))
            else:
                rows.append({"raw": line})

        start_char = match.start()
        start_line = base_line + raw_text[:start_char].count("\n")

        tables.append({
            "table_index": idx,
            "start_line": start_line,
            "headers": headers,
            "row_count": len(rows),
            "rows": rows
        })

    return tables


def search_rag(
    query: str,
    regex: bool = False,
    case_sensitive: bool = False,
    file_path: Path = DEFAULT_RAG_FILE
) -> List[Dict[str, Any]]:
    """
    Searches for a query or regex across sections in the markdown file and returns
    ONLY the enclosing section (heading + in-between lines), with matched line numbers.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    headings = parse_headings_with_boundaries(lines, max_depth=6)

    flags = 0 if case_sensitive else re.IGNORECASE
    if regex:
        matcher = re.compile(query, flags)
    else:
        matcher = re.compile(re.escape(query), flags)

    results = []
    for h in headings:
        start_idx = h["start_line"] - 1
        end_idx = h["end_line"]
        section_lines = lines[start_idx:end_idx]

        matched_lines = []
        for offset, l in enumerate(section_lines, start=h["start_line"]):
            if matcher.search(l):
                matched_lines.append({"line_number": offset, "text": l.strip()})

        if matched_lines:
            results.append({
                "section": h["title"],
                "level": h["level"],
                "start_line": h["start_line"],
                "end_line": h["end_line"],
                "match_count": len(matched_lines),
                "matched_lines": matched_lines,
                "content_preview": "".join(section_lines[:15])  # first 15 lines preview
            })

    return results


def save_in_rag(
    topic: str,
    content: str,
    subtopic: Optional[str] = None,
    section: Optional[str] = None,
    file_path: Path = DEFAULT_RAG_FILE,
    mode: str = "append"
) -> Dict[str, Any]:
    """
    Saves or appends context into the markdown RAG file under # topic, ## subtopic, or ### section.
    """
    file_path = ensure_file_exists(file_path)
    raw_text = file_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines(keepends=True)

    content_clean = content.strip()
    target_heading = section or subtopic or topic
    target_level = 3 if section else (2 if subtopic else 1)

    # Check if section exists
    headings = parse_headings_with_boundaries(lines, max_depth=6)
    target_idx = None
    for h in headings:
        if h["title"].lower() == target_heading.strip().lower():
            target_idx = h
            break

    if target_idx is None:
        # Append as new block at end
        prefix = "#" * target_level
        new_block = f"\n\n{prefix} {target_heading.strip()}\n\n{content_clean}\n"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(new_block)
        status = "created"
    else:
        start_line = target_idx["start_line"]
        end_line = target_idx["end_line"]
        if mode == "replace":
            prefix = "#" * target_idx["level"]
            lines[start_line - 1:end_line] = [f"{prefix} {target_idx['title']}\n\n{content_clean}\n\n"]
            status = "replaced"
        else:
            lines.insert(end_line, f"\n{content_clean}\n")
            status = "appended"
        file_path.write_text("".join(lines), encoding="utf-8")

    return {
        "status": status,
        "heading": target_heading,
        "level": target_level,
        "file": str(file_path)
    }


def main():
    parser = argparse.ArgumentParser(description="Advanced token-efficient Markdown RAG service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-topics
    p_topics = subparsers.add_parser("get-topics", help="List topics and subtopics with line boundaries")
    p_topics.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")
    p_topics.add_argument("--depth", "-d", type=int, default=4, help="Max heading depth (# through ####)")

    # extract-from-rag
    p_extract = subparsers.add_parser("extract-from-rag", help="Extract in-between lines for topic/subtopic")
    p_extract.add_argument("--topic", "-t", required=True, help="Topic title (#)")
    p_extract.add_argument("--subtopic", "-s", default=None, help="Subtopic title (##)")
    p_extract.add_argument("--section", default=None, help="Deep section title (###)")
    p_extract.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # extract-diagrams
    p_diag = subparsers.add_parser("extract-diagrams", help="Extract all Mermaid diagrams from markdown")
    p_diag.add_argument("--topic", "-t", default=None, help="Optional topic filter")
    p_diag.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # extract-code-blocks
    p_code = subparsers.add_parser("extract-code-blocks", help="Extract code blocks by language")
    p_code.add_argument("--language", "-l", default=None, help="Filter by language (e.g. sql, ts, py, bash)")
    p_code.add_argument("--topic", "-t", default=None, help="Optional topic filter")
    p_code.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # extract-alerts
    p_alert = subparsers.add_parser("extract-alerts", help="Extract all [!WARNING], [!DANGER], [!IMPORTANT] alerts")
    p_alert.add_argument("--type", default=None, help="Filter by alert type (e.g. WARNING, DANGER, IMPORTANT)")
    p_alert.add_argument("--topic", "-t", default=None, help="Optional topic filter")
    p_alert.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # extract-tables
    p_table = subparsers.add_parser("extract-tables", help="Extract and parse markdown data tables")
    p_table.add_argument("--topic", "-t", default=None, help="Optional topic filter")
    p_table.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # search-rag
    p_search = subparsers.add_parser("search-rag", help="Search pattern across sections and return matching lines")
    p_search.add_argument("--query", "-q", required=True, help="Search string or regex")
    p_search.add_argument("--regex", "-r", action="store_true", help="Treat query as regular expression")
    p_search.add_argument("--case-sensitive", action="store_true", help="Case sensitive search")
    p_search.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # save-in-rag
    p_save = subparsers.add_parser("save-in-rag", help="Save content under topic/subtopic")
    p_save.add_argument("--topic", "-t", required=True, help="Topic title (#)")
    p_save.add_argument("--subtopic", "-s", default=None, help="Subtopic title (##)")
    p_save.add_argument("--section", default=None, help="Deep section title (###)")
    p_save.add_argument("--content", "-c", required=True, help="Content to store")
    p_save.add_argument("--mode", "-m", choices=["append", "replace"], default="append")
    p_save.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    args = parser.parse_args()

    if args.command == "get-topics":
        res = get_topics(Path(args.file), args.depth)
        print(json.dumps(res, indent=2))
    elif args.command == "extract-from-rag":
        res = extract_from_rag(args.topic, args.subtopic, args.section, Path(args.file))
        if "error" in res and res["error"]:
            print(f"Error: {res['error']}", file=sys.stderr)
            sys.exit(1)
        print(res["content"])
    elif args.command == "extract-diagrams":
        res = extract_diagrams(args.topic, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "extract-code-blocks":
        res = extract_code_blocks(args.language, args.topic, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "extract-alerts":
        res = extract_alerts(args.type, args.topic, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "extract-tables":
        res = extract_tables(args.topic, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "search-rag":
        res = search_rag(args.query, args.regex, args.case_sensitive, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "save-in-rag":
        res = save_in_rag(args.topic, args.content, args.subtopic, args.section, Path(args.file), args.mode)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
