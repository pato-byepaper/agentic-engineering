#!/usr/bin/env python3
"""
rag_service.py - Lightweight Markdown-based RAG service for large context files.
Enables token-efficient retrieval by using regex to discover topics and extract
ONLY the lines between markdown headings (# title, ## subtitle).
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
HEADING_REGEX = re.compile(r"^(#{1,2})\s+(.+?)\s*$", re.MULTILINE)


def ensure_file_exists(file_path: Path) -> Path:
    """Ensures the parent directory and file exist."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        file_path.write_text("# Knowledge Base\n\nInitial repository context.\n", encoding="utf-8")
    return file_path


def get_topics(file_path: Path = DEFAULT_RAG_FILE) -> List[Dict[str, Any]]:
    """
    Parses a markdown file using regex to extract all topics (#) and subtopics (##).
    Calculates start_line and end_line boundaries for each section without loading
    unnecessary body lines into memory.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return []

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    total_lines = len(lines)

    # Find all headings with their line numbers (1-indexed)
    headings: List[Dict[str, Any]] = []
    heading_pattern = re.compile(r"^(#{1,2})\s+(.+?)\s*$")

    for idx, line in enumerate(lines, start=1):
        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))  # 1 for '#', 2 for '##'
            raw_title = match.group(2).strip()
            # Clean optional colon or whitespace if provided like '# something: is a title'
            headings.append({
                "level": level,
                "title": raw_title,
                "start_line": idx,
                "end_line": total_lines,  # will be adjusted
            })

    # Adjust end_line: a section ends where the next heading of equal or higher level starts,
    # or next heading starts
    for i in range(len(headings)):
        current = headings[i]
        for j in range(i + 1, len(headings)):
            next_head = headings[j]
            # If current is level 1 (#), it encompasses level 2 until next level 1
            # If current is level 2 (##), it ends at next level 2 or next level 1
            if current["level"] == 2:
                # Level 2 ends at the very next heading (either # or ##)
                current["end_line"] = next_head["start_line"] - 1
                break
            elif current["level"] == 1:
                if next_head["level"] == 1:
                    current["end_line"] = next_head["start_line"] - 1
                    break

    # Format structured output with hierarchical topic and subtopic relationships
    topics: List[Dict[str, Any]] = []
    current_topic: Optional[Dict[str, Any]] = None

    for h in headings:
        if h["level"] == 1:
            current_topic = {
                "topic": h["title"],
                "start_line": h["start_line"],
                "end_line": h["end_line"],
                "line_count": max(0, h["end_line"] - h["start_line"] + 1),
                "subtopics": []
            }
            topics.append(current_topic)
        elif h["level"] == 2:
            subtopic = {
                "subtopic": h["title"],
                "parent_topic": current_topic["topic"] if current_topic else None,
                "start_line": h["start_line"],
                "end_line": h["end_line"],
                "line_count": max(0, h["end_line"] - h["start_line"] + 1)
            }
            if current_topic:
                current_topic["subtopics"].append(subtopic)
            else:
                topics.append(subtopic)

    return topics


def extract_from_rag(
    topic: str,
    subtopic: Optional[str] = None,
    file_path: Path = DEFAULT_RAG_FILE
) -> Dict[str, Any]:
    """
    Uses regex boundaries to read ONLY the in-between lines for the targeted topic
    or subtopic. This keeps token usage minimal while managing large context files.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        return {
            "error": f"File not found: {file_path}",
            "content": "",
            "lines_read": 0
        }

    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)
    total_lines = len(lines)

    target_title = (subtopic if subtopic else topic).strip().lower()
    target_level = 2 if subtopic else 1

    # Locate the heading using regex
    found_idx: Optional[int] = None
    heading_pattern = re.compile(r"^(#{1,2})\s+(.+?)\s*$")

    # If subtopic is requested, we also ensure parent topic matches if specified
    current_parent = ""
    for idx, line in enumerate(lines):
        m = heading_pattern.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            if level == 1:
                current_parent = title
            
            # Match check
            if subtopic:
                if level == 2 and (target_title in title.lower() or title.lower() in target_title):
                    if not topic or (topic.strip().lower() in current_parent.lower()):
                        found_idx = idx
                        target_level = 2
                        break
            else:
                if level == 1 and (target_title in title.lower() or title.lower() in target_title):
                    found_idx = idx
                    target_level = 1
                    break

    if found_idx is None:
        return {
            "error": f"Topic '{topic}' (subtopic: '{subtopic}') not found in {file_path}",
            "content": "",
            "lines_read": 0
        }

    # Find the end boundary where the next heading of equal or higher level appears
    end_idx = total_lines
    for idx in range(found_idx + 1, total_lines):
        m = heading_pattern.match(lines[idx])
        if m:
            next_level = len(m.group(1))
            if target_level == 2:
                # Level 2 section ends at next # or ##
                end_idx = idx
                break
            elif target_level == 1:
                # Level 1 section ends at next #
                if next_level == 1:
                    end_idx = idx
                    break

    # Extract ONLY the in-between lines
    # (including the heading line and lines up to end_idx - 1)
    extracted_lines = lines[found_idx:end_idx]
    content = "".join(extracted_lines)

    return {
        "file": str(file_path),
        "topic": topic,
        "subtopic": subtopic,
        "start_line": found_idx + 1,
        "end_line": end_idx,
        "line_count": len(extracted_lines),
        "content": content
    }


def save_in_rag(
    topic: str,
    content: str,
    subtopic: Optional[str] = None,
    file_path: Path = DEFAULT_RAG_FILE,
    mode: str = "append"
) -> Dict[str, Any]:
    """
    Saves context into the markdown RAG file under # topic or ## subtopic.
    If the section already exists:
      - mode='append': appends content to the existing section
      - mode='replace': replaces the section content
    If the section does not exist: creates it cleanly.
    """
    file_path = ensure_file_exists(file_path)
    raw_text = file_path.read_text(encoding="utf-8")
    lines = raw_text.splitlines(keepends=True)
    total_lines = len(lines)

    heading_pattern = re.compile(r"^(#{1,2})\s+(.+?)\s*$")
    content_clean = content.strip()

    # Search for existing topic or subtopic
    topic_clean = topic.strip()
    subtopic_clean = subtopic.strip() if subtopic else None

    topic_idx: Optional[int] = None
    subtopic_idx: Optional[int] = None
    next_after_topic: Optional[int] = None
    next_after_subtopic: Optional[int] = None

    for idx, line in enumerate(lines):
        m = heading_pattern.match(line)
        if m:
            lvl = len(m.group(1))
            title = m.group(2).strip()
            if lvl == 1:
                if title.lower() == topic_clean.lower():
                    topic_idx = idx
                elif topic_idx is not None and next_after_topic is None:
                    next_after_topic = idx
            elif lvl == 2 and topic_idx is not None and next_after_topic is None:
                if subtopic_clean and title.lower() == subtopic_clean.lower():
                    subtopic_idx = idx
                elif subtopic_idx is not None and next_after_subtopic is None:
                    next_after_subtopic = idx

    # If topic does not exist, append it at the end of the file
    if topic_idx is None:
        new_block = f"\n\n# {topic_clean}\n"
        if subtopic_clean:
            new_block += f"\n## {subtopic_clean}\n\n{content_clean}\n"
        else:
            new_block += f"\n{content_clean}\n"
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(new_block)
        return {
            "status": "created",
            "topic": topic_clean,
            "subtopic": subtopic_clean,
            "file": str(file_path)
        }

    # Topic exists. Now check subtopic
    if subtopic_clean:
        if subtopic_idx is None:
            # Insert subtopic right before next topic or at end of topic
            insert_pos = next_after_topic if next_after_topic is not None else total_lines
            new_sub_block = [f"\n## {subtopic_clean}\n\n{content_clean}\n\n"]
            lines[insert_pos:insert_pos] = new_sub_block
            file_path.write_text("".join(lines), encoding="utf-8")
            return {
                "status": "subtopic_created",
                "topic": topic_clean,
                "subtopic": subtopic_clean,
                "file": str(file_path)
            }
        else:
            # Subtopic exists
            end_pos = next_after_subtopic if next_after_subtopic is not None else (
                next_after_topic if next_after_topic is not None else total_lines
            )
            if mode == "replace":
                lines[subtopic_idx + 1:end_pos] = [f"\n{content_clean}\n\n"]
            else:
                lines[end_pos:end_pos] = [f"\n{content_clean}\n"]
            file_path.write_text("".join(lines), encoding="utf-8")
            return {
                "status": f"subtopic_{mode}ed",
                "topic": topic_clean,
                "subtopic": subtopic_clean,
                "file": str(file_path)
            }
    else:
        # Save directly under topic
        end_pos = next_after_topic if next_after_topic is not None else total_lines
        if mode == "replace":
            lines[topic_idx + 1:end_pos] = [f"\n{content_clean}\n\n"]
        else:
            lines[end_pos:end_pos] = [f"\n{content_clean}\n"]
        file_path.write_text("".join(lines), encoding="utf-8")
        return {
            "status": f"topic_{mode}ed",
            "topic": topic_clean,
            "subtopic": None,
            "file": str(file_path)
        }


def main():
    parser = argparse.ArgumentParser(description="Markdown-based token-efficient RAG service")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # get-topics
    p_topics = subparsers.add_parser("get-topics", help="List topics and subtopics with line boundaries")
    p_topics.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # extract-from-rag
    p_extract = subparsers.add_parser("extract-from-rag", help="Extract in-between lines for topic/subtopic")
    p_extract.add_argument("--topic", "-t", required=True, help="Topic title (#)")
    p_extract.add_argument("--subtopic", "-s", default=None, help="Subtopic title (##)")
    p_extract.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    # save-in-rag
    p_save = subparsers.add_parser("save-in-rag", help="Save content under topic/subtopic")
    p_save.add_argument("--topic", "-t", required=True, help="Topic title (#)")
    p_save.add_argument("--subtopic", "-s", default=None, help="Subtopic title (##)")
    p_save.add_argument("--content", "-c", required=True, help="Content to store")
    p_save.add_argument("--mode", "-m", choices=["append", "replace"], default="append")
    p_save.add_argument("--file", "-f", default=str(DEFAULT_RAG_FILE), help="Markdown file path")

    args = parser.parse_args()

    if args.command == "get-topics":
        res = get_topics(Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "extract-from-rag":
        res = extract_from_rag(args.topic, args.subtopic, Path(args.file))
        if "error" in res and res["error"]:
            print(f"Error: {res['error']}", file=sys.stderr)
            sys.exit(1)
        print(res["content"])
    elif args.command == "save-in-rag":
        res = save_in_rag(args.topic, args.content, args.subtopic, Path(args.file), args.mode)
        print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
