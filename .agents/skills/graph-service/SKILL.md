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
- **`dangerously_drops_table`**: Drops or truncates an entire database table (badge: `⚠️ [DANGER: DROPS TABLE]`).
- **`dangerously_drops_column`**: Drops or renames an active production database column (badge: `⚠️ [DANGER: DROPS COLUMN]`).
- **`dangerously_bypasses_rls`**: Bypasses or disables Row Level Security policies (badge: `⚠️ [DANGER: BYPASSES RLS]`).
- **`dangerously_bypasses_auth`**: Skips authentication or authorization guards (badge: `⚠️ [DANGER: BYPASSES AUTH]`).
- **`dangerously_leaks_pii`**: Emits personal data, passwords, or tokens into logs/payloads (badge: `⚠️ [DANGER: LEAKS PII]`).
- **`dangerously_locks_table`**: Issues exclusive table locks causing pool exhaustion (badge: `⚠️ [DANGER: LOCKS TABLE]`).
- **`dangerously_unbounded_query`**: Queries large datasets without pagination/stream (badge: `⚠️ [DANGER: UNBOUNDED QUERY]`).
- **`dangerously_blocks_event_loop`**: Runs CPU-heavy sync code on main thread (badge: `⚠️ [DANGER: BLOCKS EVENT LOOP]`).
- **`dangerously_invalidates_cache`**: Triggers global cache flush causing stampede (badge: `⚠️ [DANGER: CACHE STAMPEDE]`).
- **`dangerously_disables_cors`**: Disables CORS or permits wildcard origins (badge: `⚠️ [DANGER: DISABLES CORS]`).
- **`dangerously_downgrades_security`**: Weakens ciphers or security requirements (badge: `⚠️ [DANGER: DOWNGRADES SECURITY]`).

### 2. Testing & Verification Relations
- **`tests`**: Test suite validates target implementation (badge: `🧪 tests`).
- **`unit_tests`**: Unit test suite testing an isolated class/function (badge: `🧪 unit_tests`).
- **`integration_tests`**: Cross-service/DB test suite for target (badge: `🧪 integration_tests`).
- **`e2e_tests`**: End-to-end browser test for target UI flow (badge: `🧪 e2e_tests`).
- **`regression_tests`**: Regression test guarding against past defects (badge: `🧪 regression_tests`).
- **`smoke_tests`**: Fast health check / sanity test for deployment verification (badge: `🧪 smoke_tests`).
- **`contract_tests`**: Consumer-driven contract test validating API payloads (badge: `🧪 contract_tests`).
- **`benchmarks`**: Performance benchmark measuring latency/throughput (badge: `🧪 benchmarks`).
- **`snapshots`**: Snapshot test capturing DOM or data structures (badge: `🧪 snapshots`).
- **`fuzzes`**: Fuzz testing generating random input permutations (badge: `🧪 fuzzes`).
- **`mocks`**: Mock or fixture simulating target dependency (badge: `🧪 mocks`).
- **`seeds`**: Provides seed records or mock DB state for tests (badge: `🧪 seeds`).
- **`verifies`**: Tester verifies requirement, ticket, or acceptance criteria (badge: `🧪 verifies`).

### 3. Database, Storage & Persistence Relations
- **`migrates`**: Migration file creates or modifies target schema.
- **`enforces_rls_on`**: Row Level Security policy defines tenant/role isolation.
- **`indexes`**: Database index accelerates lookup queries on target table/columns.
- **`foreign_keys_to`**: Foreign key constraint links to target table.
- **`queries`**: Reads data from target database table.
- **`mutates`**: Writes/updates/deletes records in target table.
- **`partitions`**: Database partitioning strategy distributes target table data.
- **`triggers`**: Database trigger fires automated logic on table event.
- **`materializes`**: Materializes query results into view or cache table.
- **`stores_blob`**: Persists binary files or images in target storage bucket.

### 4. API, Protocols, Schemas & Contracts
- **`exposes_endpoint`**: Controller or route handler exposes target HTTP/RPC endpoint.
- **`consumes_endpoint`**: Client or service calls target remote HTTP/RPC endpoint.
- **`validates_schema`**: Schema validator (Zod, Pydantic) asserts payload structure.
- **`implements_spec`**: Implements OpenAPI, GraphQL, or Protobuf specification.
- **`serializes`**: Serializes domain entity into target DTO/transport format.
- **`deserializes`**: Deserializes transport payload into domain entity.
- **`transforms`**: Transforms data between domain representations.
- **`authenticates`**: Verifies caller identity (JWT, OAuth, API key).
- **`authorizes`**: Enforces role/permission check on caller for target action.

### 5. UI, DOM, State Management & Web Vitals
- **`renders`**: UI component renders target subcomponent or page view.
- **`manages_state_of`**: State store (Zustand, Redux, Context) manages state for target.
- **`subscribes_to_store`**: Component subscribes to state slice in target store.
- **`dispatches_action`**: UI event handler dispatches action/command to store.
- **`lazy_loads`**: Dynamically imports target module on demand to optimize LCP.
- **`styles`**: Applies CSS rules, Tailwind tokens, or themes to target.
- **`affects_web_vitals`**: Component directly impacts LCP, INP, or CLS budgets.

### 6. Infrastructure, Runtime, Caching & Messaging
- **`caches`**: Stores computed results in target cache (Redis, CDN).
- **`invalidates_cache`**: Evicts target cache entry when underlying entity changes.
- **`publishes_to`**: Publishes messages to target message broker/queue.
- **`subscribes_to`**: Consumes messages from target broker/queue.
- **`rate_limits`**: Enforces rate limiting or concurrency throttling.
- **`encrypts`**: Applies cryptographic encryption to target payload/field.
- **`decrypts`**: Decrypts ciphertext from secure storage/payload.
- **`reads_env`**: Reads environment variable or secret configuration.
- **`cron_triggers`**: Scheduled cron job periodically executes target handler.
- **`provisions`**: Infrastructure-as-Code provisions target resource.
- **`deploys_to`**: CI/CD pipeline deploys artifact to target environment.

### 7. Architecture & Code Dependencies
- **`depends_on`**: Component requires target to operate.
- **`calls`**: Controller, service, or function invokes target endpoint/method.
- **`imports`**: Source file imports symbols from target file.
- **`implements`**: Class or service implements target interface.
- **`extends`**: Class inherits from target base class.
- **`configures`**: Config file configures target service.
- **`injects`**: Dependency injection container supplies target instance.

### 8. Governance, Policies & Documentation
- **`documents`**: Documentation or API specification documents target implementation.
- **`adheres_to_adr`**: Implementation strictly complies with target ADR.
- **`governed_by_policy`**: Module is bound by security/privacy/engineering policy.
- **`replaces`**: Modern implementation replaces or supersedes legacy component.
- **`deprecated_by`**: Target component is marked deprecated and replaced by source.

### 9. Coordination & PR Stack
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
