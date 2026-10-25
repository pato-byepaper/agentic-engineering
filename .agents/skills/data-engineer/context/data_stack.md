# Data Layer & Database Stack: agy-workshop

## Database Configuration
- **Database Engine**: unknown
- **ORM / Query Builder / Migrations**: unknown
- **Migration Directory / Tooling**: [Check schema files in repo]

## Mandatory Invariants
- **Always review schema first** before code is written.
- Check indexing on foreign keys and high-frequency filter columns.
- Ensure Row Level Security (RLS) policies exist if multi-tenant isolation is required.
- Write reversible, zero-downtime migrations.
