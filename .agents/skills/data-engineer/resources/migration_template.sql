-- Migration Template: <migration_name>
-- Description: Creates <table_name> with indices, constraints, and Row Level Security (RLS)

--------------------------------------------------------------------------------
-- UP MIGRATION
--------------------------------------------------------------------------------

-- 1. Create Table
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Foreign Keys & Performance Indexes
-- Always index foreign key and tenant isolation columns
CREATE INDEX IF NOT EXISTS idx_items_tenant_status 
ON items (tenant_id, status);

CREATE INDEX IF NOT EXISTS idx_items_tenant_created 
ON items (tenant_id, created_at DESC);

-- 3. Row Level Security (RLS)
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE items FORCE ROW LEVEL SECURITY;

CREATE POLICY items_tenant_isolation_select ON items
    FOR SELECT
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

CREATE POLICY items_tenant_isolation_insert ON items
    FOR INSERT
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

CREATE POLICY items_tenant_isolation_update ON items
    FOR UPDATE
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID)
    WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

CREATE POLICY items_tenant_isolation_delete ON items
    FOR DELETE
    USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::UUID);

--------------------------------------------------------------------------------
-- DOWN MIGRATION (ROLLBACK)
--------------------------------------------------------------------------------

/*
DROP POLICY IF EXISTS items_tenant_isolation_delete ON items;
DROP POLICY IF EXISTS items_tenant_isolation_update ON items;
DROP POLICY IF EXISTS items_tenant_isolation_insert ON items;
DROP POLICY IF EXISTS items_tenant_isolation_select ON items;
ALTER TABLE items DISABLE ROW LEVEL SECURITY;
DROP INDEX IF EXISTS idx_items_tenant_created;
DROP INDEX IF EXISTS idx_items_tenant_status;
DROP TABLE IF EXISTS items;
*/
