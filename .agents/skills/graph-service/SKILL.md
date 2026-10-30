---
name: graph-service
description: Tracks dependencies and relationships across components, services, database models, and tasks. Automatically updates Mermaid diagrams. Use whenever recording (add-relationship) or querying (get-relationships) relationships.
---

# Dependency & Relationship Graph Service

You use this service to record and query architectural dependencies, service boundaries, database relationships, and ticket interactions.

Whenever a user asks or you discover a new dependency, entity link, or component relationship, you **MUST** record it using `add-relationship`.

---

## Capabilities & Architecture

- **Directed Relationship Graph**: Stores entities (nodes) and directed relationships (edges) in `.agents/graph/dependencies.json`.
- **Automatic Mermaid Synchronization**: Every relationship added automatically re-generates `.agents/graph/dependencies.mmd` for easy inclusion in PR descriptions and documentation.

---

## Operations & Tool Calls

### 1. Add Relationship (`add-relationship`)
Records a relationship between two entities.

**CLI Execution**:
```bash
python3 .agents/tools/graph_service.py add-relationship \
  --source "BillingService" \
  --rel "depends_on" \
  --target "StripeGateway" \
  --meta '{"layer": "backend", "criticality": "high"}'
```

**MCP Tool Call**:
`add_relationship(source="BillingService", relationship="depends_on", target="StripeGateway", metadata={"layer": "backend"})`

**Common Relationship Types**:
- `depends_on`: Component A requires Component B to function.
- `calls`: Service A invokes API/RPC of Service B.
- `implements`: Module A implements Interface B.
- `migrates_to`: Legacy model A is replaced by new model B.
- `blocks`: Task A must complete before Task B can start.
- `queries`: Service A queries Database Table B.

### 2. Query Relationships (`get-relationships`)
Inspects relationships for a specific entity or filters by relation type.

**CLI Execution**:
```bash
# Get all incoming and outgoing connections for an entity:
python3 .agents/tools/graph_service.py get-relationships --entity "BillingService"

# Get only outgoing connections:
python3 .agents/tools/graph_service.py get-relationships --entity "BillingService" --direction outgoing

# Filter by relation type:
python3 .agents/tools/graph_service.py get-relationships --rel "depends_on"
```

**MCP Tool Call**:
`get_relationships(entity="BillingService", direction="all")`

### 3. List All Entities (`list-entities`)
Lists all nodes in the graph with incoming and outgoing connection counts.

**CLI Execution**:
```bash
python3 .agents/tools/graph_service.py list-entities
```

### 4. Export Mermaid Diagram (`export-mermaid`)
Exports the live Mermaid diagram for use in PR descriptions or architecture documents.

**CLI Execution**:
```bash
python3 .agents/tools/graph_service.py export-mermaid [--orientation TD|LR]
```

**MCP Tool Call**:
`export_graph_mermaid(orientation="TD")`

---

## Storage Locations
- Graph Store: `.agents/graph/dependencies.json`
- Live Mermaid File: `.agents/graph/dependencies.mmd`
