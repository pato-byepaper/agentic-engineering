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
    "dangerously_drops_table": {
        "category": "danger",
        "description": "Drops or truncates an entire database table, destroying schema and data",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: DROPS TABLE]"
    },
    "dangerously_drops_column": {
        "category": "danger",
        "description": "Drops or renames a database column with active read/write traffic",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: DROPS COLUMN]"
    },
    "dangerously_bypasses_rls": {
        "category": "danger",
        "description": "Bypasses or disables Row Level Security, allowing unauthorized table access",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: BYPASSES RLS]"
    },
    "dangerously_bypasses_auth": {
        "category": "danger",
        "description": "Skips authentication or authorization guards on an endpoint or service",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: BYPASSES AUTH]"
    },
    "dangerously_leaks_pii": {
        "category": "danger",
        "description": "Emits personally identifiable information, passwords, or tokens into logs or payloads",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: LEAKS PII]"
    },
    "dangerously_locks_table": {
        "category": "danger",
        "description": "Acquires exclusive table locks causing database connection pool exhaustion",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: LOCKS TABLE]"
    },
    "dangerously_unbounded_query": {
        "category": "danger",
        "description": "Executes query without pagination limit, risking memory exhaustion / OOM crashes",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: UNBOUNDED QUERY]"
    },
    "dangerously_blocks_event_loop": {
        "category": "danger",
        "description": "Executes synchronous CPU-heavy work on the main event loop thread",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: BLOCKS EVENT LOOP]"
    },
    "dangerously_invalidates_cache": {
        "category": "danger",
        "description": "Triggers global cache flush leading to downstream database cache stampede",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: CACHE STAMPEDE]"
    },
    "dangerously_disables_cors": {
        "category": "danger",
        "description": "Disables CORS restrictions or allows wildcard origins on authenticated endpoints",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: DISABLES CORS]"
    },
    "dangerously_downgrades_security": {
        "category": "danger",
        "description": "Weakens encryption ciphers, hashing rounds, or authentication requirements",
        "is_dangerous": True,
        "badge": "⚠️ [DANGER: DOWNGRADES SECURITY]"
    },

    # 2. Testing & Verification Relations
    "tests": {
        "category": "testing",
        "description": "Test suite validates the target implementation",
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
        "description": "End-to-end browser test verifies live user journey and Core Web Vitals for target UI",
        "is_dangerous": False,
        "badge": "🧪 e2e_tests"
    },
    "regression_tests": {
        "category": "testing",
        "description": "Dedicated regression test suite guards against past defects or regressions",
        "is_dangerous": False,
        "badge": "🧪 regression_tests"
    },
    "smoke_tests": {
        "category": "testing",
        "description": "Fast smoke/sanity test verifying core functionality post-deployment",
        "is_dangerous": False,
        "badge": "🧪 smoke_tests"
    },
    "contract_tests": {
        "category": "testing",
        "description": "Consumer-driven contract test validates API payload compatibility",
        "is_dangerous": False,
        "badge": "🧪 contract_tests"
    },
    "benchmarks": {
        "category": "testing",
        "description": "Performance benchmark validates latency and throughput budgets",
        "is_dangerous": False,
        "badge": "🧪 benchmarks"
    },
    "snapshots": {
        "category": "testing",
        "description": "Snapshot test captures and asserts UI markup or serialized data structure",
        "is_dangerous": False,
        "badge": "🧪 snapshots"
    },
    "fuzzes": {
        "category": "testing",
        "description": "Fuzz testing generates pseudorandom input permutations to expose unexpected panics",
        "is_dangerous": False,
        "badge": "🧪 fuzzes"
    },
    "mocks": {
        "category": "testing",
        "description": "Mock or fixture simulates behavior of target dependency",
        "is_dangerous": False,
        "badge": "🧪 mocks"
    },
    "seeds": {
        "category": "testing",
        "description": "Provides seed records or mock database state for testing target",
        "is_dangerous": False,
        "badge": "🧪 seeds"
    },
    "verifies": {
        "category": "testing",
        "description": "Tester or audit verifies target requirement, ticket, or acceptance criteria",
        "is_dangerous": False,
        "badge": "🧪 verifies"
    },

    # 3. Database, Storage & Persistence Relations
    "migrates": {
        "category": "data",
        "description": "Database migration script creates or alters target table/schema",
        "is_dangerous": False,
        "badge": "migrates"
    },
    "enforces_rls_on": {
        "category": "data",
        "description": "Row Level Security policy defines tenant/role isolation on target table",
        "is_dangerous": False,
        "badge": "enforces_rls_on"
    },
    "indexes": {
        "category": "data",
        "description": "Database index accelerates lookup queries on target table/columns",
        "is_dangerous": False,
        "badge": "indexes"
    },
    "foreign_keys_to": {
        "category": "data",
        "description": "Foreign key constraint links to target parent table",
        "is_dangerous": False,
        "badge": "foreign_keys_to"
    },
    "queries": {
        "category": "data",
        "description": "Reads records from target database table or view",
        "is_dangerous": False,
        "badge": "queries"
    },
    "mutates": {
        "category": "data",
        "description": "Performs insert, update, or soft-delete on target table",
        "is_dangerous": False,
        "badge": "mutates"
    },
    "partitions": {
        "category": "data",
        "description": "Database partitioning strategy distributes target table data",
        "is_dangerous": False,
        "badge": "partitions"
    },
    "triggers": {
        "category": "data",
        "description": "Database trigger fires automated logic on target table event",
        "is_dangerous": False,
        "badge": "triggers"
    },
    "materializes": {
        "category": "data",
        "description": "Materializes query results into view or precalculated cache table",
        "is_dangerous": False,
        "badge": "materializes"
    },
    "stores_blob": {
        "category": "data",
        "description": "Persists binary files, images, or documents to target bucket/storage",
        "is_dangerous": False,
        "badge": "stores_blob"
    },

    # 4. API, Protocols, Schemas & Contracts
    "exposes_endpoint": {
        "category": "contract",
        "description": "Route controller exposes target HTTP/RPC endpoint",
        "is_dangerous": False,
        "badge": "exposes_endpoint"
    },
    "consumes_endpoint": {
        "category": "contract",
        "description": "Client or backend service calls target remote HTTP/RPC endpoint",
        "is_dangerous": False,
        "badge": "consumes_endpoint"
    },
    "validates_schema": {
        "category": "contract",
        "description": "Schema validator (Zod, Pydantic, Joi) asserts payload structure for target",
        "is_dangerous": False,
        "badge": "validates_schema"
    },
    "implements_spec": {
        "category": "contract",
        "description": "Service implements OpenAPI, GraphQL, or Protobuf interface specification",
        "is_dangerous": False,
        "badge": "implements_spec"
    },
    "serializes": {
        "category": "contract",
        "description": "Serializes domain entity into target DTO or transport representation",
        "is_dangerous": False,
        "badge": "serializes"
    },
    "deserializes": {
        "category": "contract",
        "description": "Deserializes incoming transport payload into target domain entity",
        "is_dangerous": False,
        "badge": "deserializes"
    },
    "transforms": {
        "category": "contract",
        "description": "Transforms data between domain and external contract shapes",
        "is_dangerous": False,
        "badge": "transforms"
    },
    "authenticates": {
        "category": "contract",
        "description": "Verifies caller identity (JWT, OAuth, API key) for target endpoint",
        "is_dangerous": False,
        "badge": "authenticates"
    },
    "authorizes": {
        "category": "contract",
        "description": "Enforces role/permission check on caller for target action",
        "is_dangerous": False,
        "badge": "authorizes"
    },

    # 5. UI, DOM, State Management & Web Vitals
    "renders": {
        "category": "ui_state",
        "description": "UI component renders target subcomponent or page view",
        "is_dangerous": False,
        "badge": "renders"
    },
    "manages_state_of": {
        "category": "ui_state",
        "description": "State store (Zustand, Redux, Context) manages reactive state for target",
        "is_dangerous": False,
        "badge": "manages_state_of"
    },
    "subscribes_to_store": {
        "category": "ui_state",
        "description": "Component subscribes to state slice in target store",
        "is_dangerous": False,
        "badge": "subscribes_to_store"
    },
    "dispatches_action": {
        "category": "ui_state",
        "description": "UI event handler dispatches action or command to target store",
        "is_dangerous": False,
        "badge": "dispatches_action"
    },
    "lazy_loads": {
        "category": "ui_state",
        "description": "Dynamically imports target module on demand to protect LCP budget",
        "is_dangerous": False,
        "badge": "lazy_loads"
    },
    "styles": {
        "category": "ui_state",
        "description": "Applies styling rules, theme tokens, or CSS classes to target component",
        "is_dangerous": False,
        "badge": "styles"
    },
    "affects_web_vitals": {
        "category": "ui_state",
        "description": "Component or script directly impacts LCP, INP, or CLS performance budgets",
        "is_dangerous": False,
        "badge": "affects_web_vitals"
    },

    # 6. Infrastructure, Runtime, Caching & Messaging
    "caches": {
        "category": "infrastructure",
        "description": "Stores computed results in target cache (Redis, CDN, in-memory)",
        "is_dangerous": False,
        "badge": "caches"
    },
    "invalidates_cache": {
        "category": "infrastructure",
        "description": "Evicts target cache entry when underlying entity changes",
        "is_dangerous": False,
        "badge": "invalidates_cache"
    },
    "publishes_to": {
        "category": "infrastructure",
        "description": "Publishes events or messages to target message broker / queue",
        "is_dangerous": False,
        "badge": "publishes_to"
    },
    "subscribes_to": {
        "category": "infrastructure",
        "description": "Listens for events on target broker, queue, or event bus",
        "is_dangerous": False,
        "badge": "subscribes_to"
    },
    "rate_limits": {
        "category": "infrastructure",
        "description": "Enforces rate limiting or concurrency throttling on target resource",
        "is_dangerous": False,
        "badge": "rate_limits"
    },
    "encrypts": {
        "category": "infrastructure",
        "description": "Applies cryptographic encryption to target payload or field",
        "is_dangerous": False,
        "badge": "encrypts"
    },
    "decrypts": {
        "category": "infrastructure",
        "description": "Decrypts ciphertext from target secure storage or payload",
        "is_dangerous": False,
        "badge": "decrypts"
    },
    "reads_env": {
        "category": "infrastructure",
        "description": "Reads environment variable or secret configuration for target runtime",
        "is_dangerous": False,
        "badge": "reads_env"
    },
    "cron_triggers": {
        "category": "infrastructure",
        "description": "Scheduled cron job periodically executes target handler",
        "is_dangerous": False,
        "badge": "cron_triggers"
    },
    "provisions": {
        "category": "infrastructure",
        "description": "Infrastructure-as-Code (Terraform, Dockerfile) provisions target resource",
        "is_dangerous": False,
        "badge": "provisions"
    },
    "deploys_to": {
        "category": "infrastructure",
        "description": "CI/CD pipeline builds and deploys target artifact to target environment",
        "is_dangerous": False,
        "badge": "deploys_to"
    },

    # 7. Architecture & Code Dependency Relations
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
    "configures": {
        "category": "architecture",
        "description": "Configuration file configures target service or runtime",
        "is_dangerous": False,
        "badge": "configures"
    },
    "injects": {
        "category": "architecture",
        "description": "Dependency injection container supplies target instance to consumer",
        "is_dangerous": False,
        "badge": "injects"
    },

    # 8. Governance, Policies & Documentation
    "documents": {
        "category": "governance",
        "description": "Documentation or API specification documents target implementation",
        "is_dangerous": False,
        "badge": "documents"
    },
    "adheres_to_adr": {
        "category": "governance",
        "description": "Implementation strictly complies with target Architecture Decision Record",
        "is_dangerous": False,
        "badge": "adheres_to_adr"
    },
    "governed_by_policy": {
        "category": "governance",
        "description": "Module is bound by target security, data retention, or engineering policy",
        "is_dangerous": False,
        "badge": "governed_by_policy"
    },
    "replaces": {
        "category": "governance",
        "description": "Modern implementation replaces or supersedes target legacy component",
        "is_dangerous": False,
        "badge": "replaces"
    },
    "deprecated_by": {
        "category": "governance",
        "description": "Target component is marked deprecated and replaced by source",
        "is_dangerous": False,
        "badge": "deprecated_by"
    },

    # 9. Coordination & Stacked PR Flow
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

            if rel.lower() == "blocks":
                lines.append(f'    {src_id}["{src}"] ==>|"{label}"| {tgt_id}["{tgt}"]')
            elif is_dangerous:
                # Highlight dangerous connections with dashed alert style
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
    dangerous dependencies, schema/contract implications, and overall risk rating.
    """
    data = load_graph(file_path)
    entity_clean = entity.strip().lower()
    edges = data.get("edges", [])

    tests = []
    consumers = []
    dependencies = []
    dangers = []
    data_impacts = []
    contract_impacts = []
    ui_impacts = []

    for edge in edges:
        src = edge["source"]
        tgt = edge["target"]
        rel = edge.get("relationship", "")
        rel_lower = rel.lower()
        is_dang = edge.get("is_dangerous", False)
        rel_info = PREDEFINED_RELATIONSHIPS.get(rel_lower, {})
        cat = edge.get("category") or rel_info.get("category", "custom")
        if rel_info.get("is_dangerous", False):
            is_dang = True

        is_test_rel = (
            cat == "testing"
            or "test" in rel_lower
            or rel_lower in ["mocks", "seeds", "snapshots", "benchmarks", "fuzzes", "verifies"]
        )

        # Incoming edges (Things that call, test, or depend on this entity)
        if tgt.lower() == entity_clean:
            if is_test_rel:
                tests.append({"test_file": src, "type": rel, "badge": rel_info.get("badge", rel)})
            else:
                consumers.append({"consumer": src, "relationship": rel, "category": cat})

            if is_dang:
                dangers.append({"source": src, "relationship": rel, "target": tgt, "direction": "incoming"})

            if cat == "data":
                data_impacts.append({"source": src, "relationship": rel, "target": tgt})
            elif cat == "contract":
                contract_impacts.append({"source": src, "relationship": rel, "target": tgt})
            elif cat == "ui_state":
                ui_impacts.append({"source": src, "relationship": rel, "target": tgt})

        # Outgoing edges (Things this entity calls, modifies, mutates, or destroys)
        if src.lower() == entity_clean:
            if is_test_rel:
                tests.append({"test_file": tgt, "type": rel, "badge": rel_info.get("badge", rel)})
            else:
                dependencies.append({"dependency": tgt, "relationship": rel, "category": cat})

            if is_dang:
                dangers.append({"source": src, "relationship": rel, "target": tgt, "direction": "outgoing"})

            if cat == "data":
                data_impacts.append({"source": src, "relationship": rel, "target": tgt})
            elif cat == "contract":
                contract_impacts.append({"source": src, "relationship": rel, "target": tgt})
            elif cat == "ui_state":
                ui_impacts.append({"source": src, "relationship": rel, "target": tgt})

    # Calculate risk rating
    if any(d["relationship"].startswith("dangerously_") for d in dangers) or len(dangers) > 1:
        risk_rating = "CRITICAL"
    elif len(dangers) > 0 or (len(consumers) > 3 and len(tests) == 0):
        risk_rating = "HIGH"
    elif len(consumers) > 0 or len(data_impacts) > 0 or len(contract_impacts) > 0:
        risk_rating = "MEDIUM"
    else:
        risk_rating = "LOW"

    return {
        "entity": entity,
        "risk_rating": risk_rating,
        "safe_to_edit": len(dangers) == 0,
        "has_associated_tests": len(tests) > 0,
        "associated_tests_count": len(tests),
        "associated_tests": tests,
        "downstream_consumers_count": len(consumers),
        "downstream_consumers": consumers,
        "dependencies_count": len(dependencies),
        "dependencies": dependencies,
        "dangerous_relationships_count": len(dangers),
        "dangerous_relationships": dangers,
        "data_and_schema_impacts": data_impacts,
        "api_and_contract_impacts": contract_impacts,
        "ui_and_web_vitals_impacts": ui_impacts,
        "summary": (
            f"Entity '{entity}' [{risk_rating} RISK]: {len(tests)} test files, {len(consumers)} consumers, "
            f"{len(dependencies)} dependencies, {len(dangers)} dangerous links, "
            f"{len(data_impacts)} data links, {len(contract_impacts)} contract links."
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
