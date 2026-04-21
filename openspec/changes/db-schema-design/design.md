## Context

The photography tutor needs persistent storage for users, voice sessions, conversation history, learning progress across photography topics, and photo submissions with AI-generated feedback. The database runs as SQLite in development (file at `db/local.db`, mounted in Docker as the `db-data` named volume). The schema is designed to be forward-compatible with PostgreSQL for future production migration.

The two interaction modes—**structured learning** (curriculum-driven) and **scene advice** (ad-hoc photo critique)—drive distinct data access patterns that the schema must support efficiently.

**Canonical schema:** [`openspec/specs/database/schema.md`](../../specs/database/schema.md)

## Goals / Non-Goals

**Goals:**
- Define all entities, columns, types, nullability, and constraints
- Establish foreign key relationships and cardinalities
- Document indexing strategy for anticipated query patterns
- Remain forward-compatible with PostgreSQL (no SQLite-exclusive types)
- Support both interaction modes without schema branching

**Non-Goals:**
- SQLAlchemy model code or Alembic migrations (implementation phase)
- Full-text search indexing on conversation content
- Multi-tenancy or organization-level data isolation
- File storage (photos are stored on disk; the DB holds only paths/metadata)

## Decisions

### Curriculum: hard-coded Python constant seeded into `topics` table

The curriculum is defined in `backend/app/curriculum.py` and inserted idempotently at startup. Keeps schema relational (FK integrity, joins) without a manual seed step. See schema doc for details.

### `last_topic_slug` on `sessions` for sidebar

`sessions.last_topic_id` FK → `topics.id` is updated in-place per topic transition. Sidebar query is a single `LEFT JOIN topics` — no subquery needed.

### `session_topics` separate from `user_topic_progress`

Session-scoped completion and lifetime progress serve different read patterns. Merging them would require grouping on every sidebar load.

### `user_level` and `equipment_type` on `sessions`, not `users`

Equipment and self-assessed level can change across sessions. Storing on `sessions` preserves history and lets the agent observe progression over time.

### No CASCADE deletes

Deletions must be explicit and ordered. Prevents accidental data loss from stale FK references.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| SQLite WAL mode required under concurrent Docker processes | Set `PRAGMA journal_mode=WAL` at connection time |
| `updated_at` auto-update has no `ON UPDATE` trigger in SQLite | Use SQLAlchemy `onupdate=func.now()` on mapped columns |
| `storage_path` breaks if container mount point changes | Document convention in CLAUDE.md |
| Curriculum changes require container restart | Acceptable for MVP; document in CLAUDE.md |
