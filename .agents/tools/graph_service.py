#!/usr/bin/env python3
"""
graph_service.py - Dependency and Relationship Graph Service.
Keeps track of architectural dependencies, entity relationships, and service topologies.
Includes a rich catalog of predefined relationships (including DANGEROUS/destructive operations,
testing links, architectural dependencies, and task coordination).
Enables agents to record (add-relationship) and query (get-relationships) connections,
inspect blast radius before editing a file (check-impact), and automatically renders live Mermaid diagrams.
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

# Rich predefined relationship taxonomy
PREDEFINED_RELATIONSHIPS: Dict[str, Dict[str, Any]] = {
    # 1. Critical & Dangerous / Destructive Relations
    "dangerously_destroys": {
        "category": "danger",
        "description": "Irreversibly destroys, deletes data, drops tables, or drops critical state in target",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: DESTROYS]"
    },
    "dangerously_breaks": {
        "category": "danger",
        "description": "Modifications break API contracts, database integrity, or downstream consumers",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: BREAKS]"
    },
    "dangerously_overwrites": {
        "category": "danger",
        "description": "Overwrites existing configuration, storage, or uncommitted files without backup",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: OVERWRITES]"
    },
    "dangerously_exposes": {
        "category": "danger",
        "description": "Exposes protected data, credentials, or private routes to public access",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: EXPOSES]"
    },
    "dangerously_deprecates": {
        "category": "danger",
        "description": "Marks target as deprecated and scheduled for immediate deletion/decommission",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: DEPRECATES]"
    },

    # 2. Testing & Verification Relations
    "tests": {
        "category": "testing",
        "description": "Test file or suite validates the target implementation",
        "is_dangerous": False,
        "badge": "🧪 tests"
    },
    "unit_tests": {
        "category": "testing",
        "description": "Unit test suite verifies isolated target unit, class, or function",
        "is_dangerous": False,
        "badge": "🧪 unit_tests"
    },
    "integration_tests": {
        "category": "testing",
        "description": "Integration test verifies cross-service or DB interaction with target",
        "is_dangerous": False,
        "badge": "🧪 integration_tests"
    },
    "e2e_tests": {
        "category": "testing",
        "description": "End-to-end browser test verifies live user journey for target UI",
        "is_dangerous": False,
        "badge": "🧪 e2e_tests"
    },
    "mocks": {
        "category": "testing",
        "description": "Mock or fixture simulates behavior of target dependency",
        "is_dangerous": False,
        "badge": "🧪 mocks"
    },
    "verifies": {
        "category": "testing",
        "description": "Tester or audit verifies target requirement, ticket, or acceptance criteria",
        "is_dangerous": False,
        "badge": "🧪 verifies"
    },

    # 3. Architectural & Code Dependencies
    "depends_on": {
        "category": "architecture",
        "description": "Component requires target to operate",
        "is_dangerous": False,
        "badge": "depends_on"
    },
    "calls": {
        "category": "architecture",
        "description": "Service, function, or controller invokes target endpoint/method",
        "is_dangerous": False,
        "badge": "calls"
    },
    "imports": {
        "category": "architecture",
        "description": "Source module imports symbols from target file",
        "is_dangerous": False,
        "badge": "imports"
    },
    "implements": {
        "category": "architecture",
        "description": "Class or service implements target contract/interface",
        "is_dangerous": False,
        "badge": "implements"
    },
    "extends": {
        "category": "architecture",
        "description": "Class inherits from target base class",
        "is_dangerous": False,
        "badge": "extends"
    },
    "renders": {
        "category": "architecture",
        "description": "UI component renders target subcomponent or page view",
        "is_dangerous": False,
        "badge": "renders"
    },
    "validates": {
        "category": "architecture",
        "description": "Schema or DTO validator validates target payload or input",
        "is_dangerous": False,
        "badge": "validates"
    },
    "queries": {
        "category": "architecture",
        "description": "Reads data from target database table or view",
        "is_dangerous": False,
        "badge": "queries"
    },
    "mutates": {
        "category": "architecture",
        "description": "Performs write/update/delete operations on target table",
        "is_dangerous": False,
        "badge": "mutates"
    },
    "migrates": {
        "category": "architecture",
        "description": "Database migration modifies target schema/table",
        "is_dangerous": False,
        "badge": "migrates"
    },
    "publishes_to": {
        "category": "architecture",
        "description": "Publishes events or messages to target topic/queue",
        "is_dangerous": False,
        "badge": "publishes_to"
    },
    "subscribes_to": {
        "category": "architecture",
        "description": "Listens for events on target topic/queue",
        "is_dangerous": False,
        "badge": "subscribes_to"
    },
    "configures": {
        "category": "architecture",
        "description": "Configuration file configures target service or runtime",
        "is_dangerous": False,
        "badge": "configures"
    },

    # 4. Coordination & Stacked PR Flow
    "blocks": {
        "category": "coordination",
        "description": "Task or issue blocks progress on target task",
        "is_dangerous": True,
        "badge": "⛔ blocks"
    },
    "stacked_on": {
        "category": "coordination",
        "description": "Git branch or PR is stacked on target base branch",
        "is_dangerous": False,
        "badge": "stacked_on"
    },
    "delegates_to": {
        "category": "coordination",
        "description": "Agent role hands off technical task to target role",
        "is_dangerous": False,
        "badge": "delegates_to"
    },
    "hands_off_to": {
        "category": "coordination",
        "description": "Developer hands off diff to Committer upon completion",
        "is_dangerous": False,
        "badge": "hands_off_to"
    },
    "verifies_for": {
        "category": "coordination",
        "description": "Tester verifies acceptance criteria for target Manager or Issue",
        "is_dangerous": False,
        "badge": "verifies_for"
    }
}


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


def list_relationship_types(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """Returns the catalog of predefined relationships, optionally filtered by category."""
    results = []
    cat_filter = category.strip().lower() if category else None
    for name, info in PREDEFINED_RELATIONSHIPS.items():
        if cat_filter and info["category"] != cat_filter:
            continue
        results.append({
            "name": name,
            "category": info["category"],
            "is_dangerous": info["is_dangerous"],
            "description": info["description"],
            "badge": info["badge"]
        })
    return results


def export_mermaid(data: Dict[str, Any], output_path: Path = DEFAULT_GRAPH_MMD, orientation: str = "TD") -> str:
    """Exports the graph data into a valid Mermaid diagram with danger alerts and test highlights."""
    lines = [f"flowchart {orientation}"]

    def sanitize_id(name: str) -> str:
        return "".join(c if c.isalnum() else "_" for c in name)

    edges = data.get("edges", [])
    if not edges:
        lines.append('    EmptyGraph["(No relationships defined)"]')
    else:
        for idx, edge in enumerate(edges):
            src = edge["source"]
            tgt = edge["target"]
            rel = edge.get("relationship", "relates_to")
            is_dangerous = edge.get("is_dangerous", False)
            src_id = sanitize_id(src)
            tgt_id = sanitize_id(tgt)

            # Determine badge from predefined catalog if available
            rel_info = PREDEFINED_RELATIONSHIPS.get(rel.lower())
            if rel_info:
                label = rel_info["badge"]
                is_dangerous = is_dangerous or rel_info["is_dangerous"]
            else:
                label = rel
                if "danger" in rel.lower() or "destroy" in rel.lower() or "break" in rel.lower():
                    is_dangerous = True
                    label = f"⚠️ [DANGER: {rel}]"

            if is_dangerous:
                # Highlight dangerous connections with thick / red dashed style
                lines.append(f'    {src_id}["{src}"] -.->|"{label}"| {tgt_id}["{tgt}"]')
            elif rel_info and rel_info["category"] == "testing":
                lines.append(f'    {src_id}["{src}"] -.->|"{label}"| {tgt_id}["{tgt}"]')
            else:
                lines.append(f'    {src_id}["{src}"] -->|"{label}"| {tgt_id}["{tgt}"]')

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
    Auto-detects dangerous relationships, updates nodes/edges, and syncs Mermaid.
    """
    data = load_graph(file_path)
    source_clean = source.strip()
    target_clean = target.strip()
    rel_clean = relationship.strip()

    # Predefined catalog lookup
    rel_info = PREDEFINED_RELATIONSHIPS.get(rel_clean.lower())
    is_dangerous = False
    category = "custom"
    if rel_info:
        is_dangerous = rel_info["is_dangerous"]
        category = rel_info["category"]
    elif "danger" in rel_clean.lower() or "destroy" in rel_clean.lower() or "break" in rel_clean.lower():
        is_dangerous = True
        category = "danger"

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
        existing_edge["is_dangerous"] = is_dangerous
        existing_edge["category"] = category
        status = "updated"
        edge_data = existing_edge
    else:
        edge_data = {
            "source": source_clean,
            "relationship": rel_clean,
            "target": target_clean,
            "category": category,
            "is_dangerous": is_dangerous,
            "created_at": now_iso,
            "metadata": metadata or {}
        }
        data["edges"].append(edge_data)
        status = "created"

    save_graph(data, file_path)
    return {
        "status": status,
        "relationship": edge_data,
        "is_dangerous": is_dangerous,
        "warning": "⚠️ CAUTION: Dangerous / destructive relationship recorded!" if is_dangerous else None,
        "total_nodes": len(data["nodes"]),
        "total_edges": len(data["edges"]),
        "graph_file": str(file_path),
        "mermaid_file": str(Path(file_path).with_suffix(".mmd"))
    }


def get_relationships(
    entity: Optional[str] = None,
    relationship: Optional[str] = None,
    direction: str = "all",
    category: Optional[str] = None,
    only_dangerous: bool = False,
    file_path: Path = DEFAULT_GRAPH_JSON
) -> Dict[str, Any]:
    """
    Queries relationships from the graph.
    Filters by entity, relationship, category, danger flag, and direction ('all', 'outgoing', 'incoming').
    """
    data = load_graph(file_path)
    edges = data.get("edges", [])

    filtered: List[Dict[str, Any]] = []
    entity_clean = entity.strip().lower() if entity else None
    rel_clean = relationship.strip().lower() if relationship else None
    cat_clean = category.strip().lower() if category else None

    for edge in edges:
        src = edge["source"].lower()
        tgt = edge["target"].lower()
        rel = edge.get("relationship", "").lower()
        edge_cat = edge.get("category", "").lower()
        is_dang = edge.get("is_dangerous", False)

        if only_dangerous and not is_dang:
            continue
        if cat_clean and edge_cat != cat_clean:
            continue
        if rel_clean and rel_clean != rel:
            continue

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


def check_impact(entity: str, file_path: Path = DEFAULT_GRAPH_JSON) -> Dict[str, Any]:
    """
    Crucial pre-edit check! Evaluates the blast radius of modifying an entity/file:
    Identifies associated test files, incoming consumers that might break,
    and dangerous dependencies connected to it.
    """
    data = load_graph(file_path)
    entity_clean = entity.strip().lower()
    edges = data.get("edges", [])

    tests = []
    consumers = []
    dependencies = []
    dangers = []

    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        rel = edge.get("relationship", "")
        is_dang = edge.get("is_dangerous", False)

        # Incoming edges (Things that call or depend on this entity)
        if tgt.lower() == entity_clean:
            if rel in ["tests", "unit_tests", "integration_tests", "e2e_tests"]:
                tests.append({"test_file": src, "type": rel})
            else:
                consumers.append({"consumer": src, "relationship": rel})
            if is_dang:
                dangers.append({"source": src, "relationship": rel, "target": tgt})

        # Outgoing edges (Things this entity calls, modifies, or destroys)
        if src.lower() == entity_clean:
            dependencies.append({"dependency": tgt, "relationship": rel})
            if is_dang:
                dangers.append({"source": src, "relationship": rel, "target": tgt})

    return {
        "entity": entity,
        "safe_to_edit": len(dangers) == 0,
        "has_associated_tests": len(tests) > 0,
        "associated_tests": tests,
        "downstream_consumers_count": len(consumers),
        "downstream_consumers": consumers,
        "dependencies_count": len(dependencies),
        "dependencies": dependencies,
        "dangerous_relationships": dangers,
        "summary": (
            f"Entity '{entity}' has {len(tests)} test files, {len(consumers)} downstream consumers, "
            f"and {len(dangers)} dangerous relationships."
        )
    }


def list_entities(file_path: Path = DEFAULT_GRAPH_JSON) -> Dict[str, Any]:
    """Lists all nodes in the graph with connection counts and danger flags."""
    data = load_graph(file_path)
    nodes = data.get("nodes", {})
    edges = data.get("edges", [])

    stats: Dict[str, Dict[str, int]] = {n: {"outgoing": 0, "incoming": 0, "dangers": 0} for n in nodes}
    for e in edges:
        s, t = e["source"], e["target"]
        is_dang = e.get("is_dangerous", False)
        if s in stats:
            stats[s]["outgoing"] += 1
            if is_dang:
                stats[s]["dangers"] += 1
        if t in stats:
            stats[t]["incoming"] += 1
            if is_dang:
                stats[t]["dangers"] += 1

    return {
        "total_entities": len(nodes),
        "entities": [
            {
                "name": name,
                "outgoing_count": counts["outgoing"],
                "incoming_count": counts["incoming"],
                "danger_count": counts["dangers"],
                "total_connections": counts["outgoing"] + counts["incoming"]
            }
            for name, counts in stats.items()
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Custom Graph Service for dependencies, dangerous operations, and tests")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add-relationship
    p_add = subparsers.add_parser("add-relationship", help="Add a relationship edge between two entities")
    p_add.add_argument("--source", "-s", required=True, help="Source entity")
    p_add.add_argument("--rel", "-r", required=True, help="Relationship type (e.g. depends_on, dangerously_destroys, tests, calls)")
    p_add.add_argument("--target", "-t", required=True, help="Target entity")
    p_add.add_argument("--meta", "-m", default=None, help="JSON string of optional metadata")
    p_add.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")

    # get-relationships
    p_get = subparsers.add_parser("get-relationships", help="Query relationships for an entity")
    p_get.add_argument("--entity", "-e", default=None, help="Entity name")
    p_get.add_argument("--rel", "-r", default=None, help="Relationship filter")
    p_get.add_argument("--category", "-c", default=None, help="Category filter (danger, testing, architecture, coordination)")
    p_get.add_argument("--dangerous", action="store_true", help="Only show dangerous relationships")
    p_get.add_argument("--direction", "-d", choices=["all", "outgoing", "incoming"], default="all")
    p_get.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")

    # check-impact (blast radius pre-edit check)
    p_check = subparsers.add_parser("check-impact", help="Check blast radius, tests, and dangerous links before editing an entity/file")
    p_check.add_argument("--entity", "-e", required=True, help="Entity or file name to evaluate")
    p_check.add_argument("--file", "-f", default=str(DEFAULT_GRAPH_JSON), help="Graph JSON path")

    # list-types
    p_types = subparsers.add_parser("list-relationship-types", help="List all predefined relationship types and categories")
    p_types.add_argument("--category", "-c", default=None, help="Filter by category (danger, testing, architecture, coordination)")

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
        res = get_relationships(args.entity, args.rel, args.direction, args.category, args.dangerous, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "check-impact":
        res = check_impact(args.entity, Path(args.file))
        print(json.dumps(res, indent=2))
    elif args.command == "list-relationship-types":
        res = list_relationship_types(args.category)
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
