#!/usr/bin/env python3
"""
graph_service.py - Dependency and Relationship Graph Service.
Keeps track of architectural dependencies, entity relationships, and service topologies.
Enables agents to record (add-relationship) and query (get-relationships) connections,
and automatically renders live Mermaid diagrams.
Designed for AGY Gemini models.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_GRAPH_JSON = Path(".agents/graph/dependencies.json")
DEFAULT_GRAPH_MMD = Path(".agents/graph/dependencies.mmd")


def ensure_graph_files(file_path: Path) -> Path:
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        initial_data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "nodes": {},
            "edges": []
        }
        file_path.write_text(json.dumps(initial_data, indent=2), encoding="utf-8")
    return file_path


def load_graph(file_path: Path = DEFAULT_GRAPH_JSON) -> Dict[str, Any]:
    file_path = ensure_graph_files(file_path)
    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
        if "nodes" not in data:
            data["nodes"] = {}
        if "edges" not in data:
            data["edges"] = []
        return data
    except Exception:
        return {"version": "1.0", "updated_at": datetime.now().isoformat(), "nodes": {}, "edges": []}


def save_graph(data: Dict[str, Any], file_path: Path = DEFAULT_GRAPH_JSON):
    file_path = Path(file_path)
    data["updated_at"] = datetime.now().isoformat()
    file_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # Automatically update the corresponding Mermaid file
    mmd_path = file_path.with_suffix(".mmd")
    export_mermaid(data, mmd_path)


def export_mermaid(data: Dict[str, Any], output_path: Path = DEFAULT_GRAPH_MMD, orientation: str = "TD") -> str:
    """Exports the graph data into a valid Mermaid diagram."""
    lines = [f"flowchart {orientation}"]
    
    # Sanitize node ID for Mermaid
    def sanitize_id(name: str) -> str:
        return "".join(c if c.isalnum() else "_" for c in name)

    # Add edges
    edges = data.get("edges", [])
    if not edges:
        lines.append('    EmptyGraph["(No relationships defined)"]')
    else:
        for edge in edges:
            src = edge["source"]
            tgt = edge["target"]
            rel = edge.get("relationship", "relates_to")
            src_id = sanitize_id(src)
            tgt_id = sanitize_id(tgt)
            lines.append(f'    {src_id}["{src}"] -->|"{rel}"| {tgt_id}["{tgt}"]')

    content = "\n".join(lines) + "\n"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return content


def add_relationship(
    source: str,
    relationship: str,
    target: str,
    metadata: Optional[Dict[str, Any]] = None,
    file_path: Path = DEFAULT_GRAPH_JSON
) -> Dict[str, Any]:
    """
    Adds a directed relationship (edge) from source to target.
    Updates the graph nodes, edges list, and regenerates the Mermaid diagram.
    """
    data = load_graph(file_path)
    source_clean = source.strip()
    target_clean = target.strip()
    rel_clean = relationship.strip()

    # Ensure nodes exist
    if source_clean not in data["nodes"]:
        data["nodes"][source_clean] = {"label": source_clean, "created_at": datetime.now().isoformat()}
    if target_clean not in data["nodes"]:
        data["nodes"][target_clean] = {"label": target_clean, "created_at": datetime.now().isoformat()}

    # Check if edge already exists
    existing_edge = None
    for edge in data["edges"]:
        if edge["source"] == source_clean and edge["target"] == target_clean and edge["relationship"] == rel_clean:
            existing_edge = edge
            break

    now_iso = datetime.now().isoformat()
    if existing_edge:
        if metadata:
            existing_edge.setdefault("metadata", {}).update(metadata)
        existing_edge["updated_at"] = now_iso
        status = "updated"
        edge_data = existing_edge
    else:
        edge_data = {
            "source": source_clean,
            "relationship": rel_clean,
            "target": target_clean,
            "created_at": now_iso,
            "metadata": metadata or {}
        }
        data["edges"].append(edge_data)
        status = "created"

    save_graph(data, file_path)
    return {
        "status": status,
        "relationship": edge_data,
        "total_nodes": len(data["nodes"]),
        "total_edges": len(data["edges"]),
        "graph_file": str(file_path),
        "mermaid_file": str(Path(file_path).with_suffix(".mmd"))
    }


def get_relationships(
    entity: Optional[str] = None,
    relationship: Optional[str] = None,
    direction: str = "all",
    file_path: Path = DEFAULT_GRAPH_JSON
) -> Dict[str, Any]:
    """
    Queries relationships from the graph.
    Filters by entity (source or target), relationship type, and direction ('all', 'outgoing', 'incoming').
    """
    data = load_graph(file_path)
    edges = data.get("edges", [])

    filtered: List[Dict[str, Any]] = []
    entity_clean = entity.strip().lower() if entity else None
    rel_clean = relationship.strip().lower() if relationship else None

    for edge in edges:
        src = edge["source"].lower()
        tgt = edge["target"].lower()
        rel = edge.get("relationship", "").lower()

        # Relationship filter
        if rel_clean and rel_clean != rel:
            continue

        # Entity filter & direction
        if entity_clean:
            if direction == "outgoing":
                if src == entity_clean:
                    filtered.append(edge)
            elif direction == "incoming":
                if tgt == entity_clean:
                    filtered.append(edge)
            else:  # all
                if src == entity_clean or tgt == entity_clean:
                    filtered.append(edge)
        else:
            filtered.append(edge)

    return {
        "entity_queried": entity,
        "relationship_queried": relationship,
        "direction": direction,
        "count": len(filtered),
        "relationships": filtered
    }


def list_entities(file_path: Path = DEFAULT_GRAPH_JSON) -> Dict[str, Any]:
    """Lists all nodes in the graph with outgoing and incoming connection counts."""
    data = load_graph(file_path)
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])

    stats: Dict[str, Dict[str, int]] = {n: {"outgoing": 0, "incoming": 0} for n in nodes}
    for e in edges:
        s, t = e["source"], e["target"]
        if s in stats:
            stats[s]["outgoing"] += 1
        if t in stats:
            stats[t]["incoming"] += 1

    return {
        "total_entities": len(nodes),
        "entities": [
            {
                "name": name,
                "outgoing_count": counts["outgoing"],
                "incoming_count": counts["incoming"],
                "total_connections": counts["outgoing"] + counts["incoming"]
            }
            for name, counts in stats.items()
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Custom Graph Service for dependencies and relationships")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-relationship
    p_add = subparsers.add_parser("add-relationship", help="Add a relationship edge between two entities")
    p_add.add_argument("--source", "-s", required=True, help="Source entity")
    p_add.add_argument("--rel", "-r", required=True, help="Relationship type (e.g. depends_on, calls, implements)")
    p_add.add_argument("--target", "-t", required=True, help="Target entity")
    p_add.add_argument("--meta", "-m", default=None, help="JSON string of optional metadata")
    p_add.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")

    # get-relationships
    p_get = subparsers.add_parser("get-relationships", help="Query relationships for an entity")
    p_get.add_argument("--entity", "-e", default=None, help="Entity name")
    p_get.add_argument("--rel", "-r", default=None, help="Relationship filter")
    p_get.add_argument("--direction", "-d", choices=["all", "outgoing", "incoming"], default="all")
    p_get.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")

    # list-entities
    p_list = subparsers.add_parser("list-entities", help="List all entities and degree centrality")
    p_list.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")

    # export-mermaid
    p_export = subparsers.add_parser("export-mermaid", help="Export graph to Mermaid diagram")
    p_export.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")
    p_export.add_argument("--output", "-o", default=str(DEFAULT_GRAPH_MMD), help="Mermaid output file path")
    p_export.add_argument("--orientation", default="TD", choices=["TD", "LR"], help="Flowchart orientation")

    args = parser.parse_args()

    if args.command == "add-relationship":
        meta = None
        if args.meta:
            try:
                meta = json.loads(args.meta)
            except Exception as ex:
                print(f"Warning: Invalid JSON metadata: {ex}", file=sys.stderr)
        res = add_relationship(args.source, args.rel, args.target, meta, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "get-relationships":
        res = get_relationships(args.entity, args.rel, args.direction, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "list-entities":
        res = list_entities(Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "export-mermaid":
        data = load_graph(Path(args.file))
        res = export_mermaid(data, Path(args.output), args.orientation)
        print(res)


if __name__ == "__main__":
    main()
