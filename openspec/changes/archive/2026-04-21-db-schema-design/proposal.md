## Why

The photography tutor backend needs a well-defined SQLite data model before any feature work begins. Without an explicit schema design, tables will accumulate ad-hoc columns and relationships will be ambiguous.

## What Changes

- Define the full SQLite relational schema covering users, sessions, messages, learning progress, and photo submissions
- Establish foreign key relationships, indexing strategy, and nullability constraints
- Produce a schema design document (no migration code or ORM models) as the authoritative reference

## Capabilities

### New Capabilities

- `db-schema`: Entity definitions, relationships, and constraints for the SQLite database backing the photography tutor

### Modified Capabilities

<!-- None — this is a greenfield schema; no existing requirement specs change -->

## Impact

- Informs all future backend feature work (API endpoints, agent state, progress tracking)
- SQLite file lives at `db/local.db` (mounted as a named Docker volume `db-data`)
- Schema design is forward-compatible with a future PostgreSQL migration (no SQLite-specific types that lack Postgres equivalents)
