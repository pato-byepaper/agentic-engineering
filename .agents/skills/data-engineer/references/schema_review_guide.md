# Data Engineer: Schema Review & Performance Guide

As a Data Engineer, you **always review schemas first** before any query or application code is written. This guide outlines the review procedure, indexing principles, and Row Level Security (RLS) standards.

---

## 1. Schema Review Checklist

Before approving or writing database definitions, check:

- [ ] **Primary Key Selection**:
  - Prefer sequential UUIDs (`UUIDv7`) or `BIGINT IDENTITY/SERIAL` over random `UUIDv4` to prevent B-tree fragmentation and write degradation.
- [ ] **Foreign Keys & Referential Integrity**:
  - Every foreign key constraint must specify an explicit `ON DELETE` behavior (`CASCADE`, `RESTRICT`, `SET NULL`).
  - **Every foreign key column must be indexed**. (Postgres and MySQL do not automatically create indexes on foreign keys).
- [ ] **Data Types & Sizing**:
  - Use appropriate sized integers (`SMALLINT`, `INTEGER`, `BIGINT`).
  - Avoid arbitrary `TEXT` without length constraints where bounded data is expected.
  - Store timestamps as `TIMESTAMPTZ` (UTC) with `DEFAULT CURRENT_TIMESTAMP`.
- [ ] **Audit Columns**:
  - Every stateful table should have `created_at` and `updated_at`.

---

## 2. Row Level Security (RLS) Standards

For multi-tenant or user-isolated systems:

1. **Always Enable RLS**:
   ```sql
   ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;
   ALTER TABLE table_name FORCE ROW LEVEL SECURITY;
   ```
2. **Define Separate Policies for Read and Write**:
   - `SELECT` uses `USING (tenant_id = current_setting('app.current_tenant_id')::uuid)`.
   - `INSERT` / `UPDATE` uses both `USING` and `WITH CHECK` to prevent data escaping the tenant boundary.
3. **Index Policy Columns**:
   - The columns evaluated in RLS policies (e.g., `tenant_id`, `user_id`) MUST have indexes, otherwise every single row scan will incur heavy overhead.

---

## 3. Indexing Strategy & Query Optimization

- **B-Tree Index Order (Equality First, Range Second)**:
  - Example: `WHERE tenant_id = '...' AND created_at > '...' ORDER BY created_at DESC`
  - Optimal index: `CREATE INDEX idx_table_tenant_created ON table (tenant_id, created_at DESC)`.
- **Partial Indexes**:
  - For filtered states: `CREATE INDEX idx_orders_unprocessed ON orders (created_at) WHERE status = 'PENDING';`
- **Covering Indexes**:
  - Use `INCLUDE (colA, colB)` to satisfy queries directly from the index without heap lookups.
- **Query Plan Verification**:
  - Always run `EXPLAIN (ANALYZE, BUFFERS)` to verify index utilization and ensure no sequential scans on large tables.

---

## 4. Zero-Downtime Migration Rules

- **Non-blocking Indexes**: Always create indexes concurrently in production:
  ```sql
  CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_name ON table (column);
  ```
- **Column Additions**:
  - Adding a `NOT NULL` column must include a default or be broken into a backfill step.
- **Reversibility**:
  - Every migration must have an exact, tested rollback/down migration.
