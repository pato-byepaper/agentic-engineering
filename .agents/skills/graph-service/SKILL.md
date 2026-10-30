---
name: graph-service
description: Tracks dependencies and relationships with predefined dangerous operations, test links, and architectural connections. Checks blast radius before editing files (check-impact) and automatically syncs Mermaid diagrams.
---

# Dependency & Relationship Graph Service

You use this service to record and query architectural dependencies, dangerous/destructive operations, test coverage links, and ticket workflows.

Whenever you discover a relationship, are asked by a user, or are about to modify a high-risk file, you **MUST** record it with `add-relationship` or check it with `check-impact`.

---

## Predefined Relationship Catalog

The graph service supports an extensive predefined catalog with danger flags and visual badges (custom relationships are also accepted):

### 1. Critical & Dangerous Operations (`is_dangerous: true`)
- **`dangerously_destroys`**: Irreversibly deletes data, drops tables, or clears state in target (badge: `⚠️ [DANGER: DESTROYS]`).
- **`dangerously_breaks`**: Modifying source breaks API contracts or downstream consumers (badge: `⚠️ [DANGER: BREAKS]`).
- **`dangerously_overwrites`**: Overwrites configs or files without backup (badge: `⚠️ [DANGER: OVERWRITES]`).
- **`dangerously_exposes`**: Exposes protected data or endpoints to public internet (badge: `⚠️ [DANGER: EXPOSES]`).
- **`dangerously_deprecates`**: Marks target for immediate removal/decommission (badge: `⚠️ [DANGER: DEPRECATES]`).

### 2. Testing & Verification Relations
- **`tests`**: Test file or suite validates target implementation (badge: `🧪 tests`).
- **`unit_tests`**: Unit test suite testing an isolated class/function (badge: `🧪 unit_tests`).
- **`integration_tests`**: Cross-service/DB test suite for target (badge: `🧪 integration_tests`).
- **`e2e_tests`**: End-to-end browser test for target UI flow (badge: `🧪 e2e_tests`).
- **`mocks`**: Mock or fixture simulating target dependency (badge: `🧪 mocks`).
- **`verifies`**: Verifies requirement, ticket, or acceptance criteria (badge: `🧪 verifies`).

### 3. Architecture & Code Dependencies
- **`depends_on`**: Component requires target to operate.
- **`calls`**: Controller, service, or function invokes target endpoint/method.
- **`imports`**: Source file imports symbols from target file.
- **`implements`**: Class or service implements target interface.
- **`extends`**: Class inherits from target base class.
- **`renders`**: UI component renders target subcomponent.
- **`validates`**: DTO or schema validator validates target payload.
- **`queries`**: Reads data from target database table.
- **`mutates`**: Writes/updates/deletes records in target table.
- **`migrates`**: Migration file creates or modifies target schema.
- **`publishes_to`**: Publishes messages to target queue/topic.
- **`subscribes_to`**: Listens for events on target queue/topic.
- **`configures`**: Config file configures target service.

### 4. Coordination & PR Stack
- **`blocks`**: Task blocks target task.
- **`stacked_on`**: Branch or PR is stacked on target base branch.
- **`delegates_to`**: Role hands off task to target role.
- **`hands_off_to`**: Coder hands off diff to Committer upon completion.
- **`verifies_for`**: Tester verifies work for Manager.

---

## Operations & Tool Calls

### 1. Add Relationship (`add-relationship`)
**CLI**:
```bash
# Dangerous operation:
python3 .agents/tools/graph_service.py add-relationship \
  --source "scripts/drop_temp.sql" --rel "dangerously_destroys" --target "db/tables/temp_orders"

# Test relationship:
python3 .agents/tools/graph_service.py add-relationship \
  --source "tests/unit/order.test.ts" --rel "unit_tests" --target "src/services/order.ts"
```
**MCP**: `add_relationship(source="...", relationship="dangerously_destroys", target="...")`

---

### 2. Check Impact Before Editing (`check-impact`)
Run this before editing any file to know its test files, consumers, and dangerous links:

**CLI**:
```bash
python3 .agents/tools/graph_service.py check-impact --entity "src/services/billing.ts"
```
**MCP**: `check_impact(entity="src/services/billing.ts")`

---

### 3. Query Relationships (`get-relationships`)
**CLI**:
```bash
# Query only dangerous connections:
python3 .agents/tools/graph_service.py get-relationships --dangerous

# Query by category:
python3 .agents/tools/graph_service.py get-relationships --category testing
```
**MCP**: `get_relationships(entity="...", only_dangerous=True)`

---

### 4. List Relationship Catalog (`list-relationship-types`)
**CLI**:
```bash
python3 .agents/tools/graph_service.py list-relationship-types [--category danger|testing|architecture]
```
**MCP**: `list_relationship_types(category="danger")`

---

### 5. Export Mermaid Diagram (`export-mermaid`)
Exports live Mermaid with danger alerts (`⚠️ [DANGER: ...]`) and test indicators (`🧪`).

**CLI**:
```bash
python3 .agents/tools/graph_service.py export-mermaid [--orientation TD|LR]
```
**MCP**: `export_graph_mermaid(orientation="TD")`
