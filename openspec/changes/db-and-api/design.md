## Context

The backend scaffold (`backend/app/`) has a working FastAPI app, a `database.py` stub, and a `GET /health` endpoint. The schema is fully specified in `openspec/specs/database/schema.md`. This change wires SQLAlchemy async ORM models to that schema, sets up the connection lifecycle, seeds the curriculum, and adds REST endpoints consumed by the frontend and the LiveKit agent.

## Goals / Non-Goals

**Goals:**
- SQLAlchemy async models for all 8 tables, matching the approved schema exactly
- `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` applied on every connection
- Idempotent curriculum seed on app startup (insert-if-not-exists by slug)
- REST endpoints: sessions (CRUD + sidebar list), messages (append + list), topics (curriculum tree + session topics + mark complete), user progress (read)
- All tables auto-created via `create_all` on first boot — no migration tooling for MVP

**Non-Goals:**
- Authentication / user creation API (users are created externally for MVP)
- Alembic migrations (deferred until schema stabilises post-MVP)
- Photo submission upload / feedback endpoints (separate change)
- Full-text search on messages

## Decisions

### Async SQLAlchemy with `aiosqlite`

FastAPI runs on an async event loop; blocking SQLite I/O on the same thread would stall request handling. `AsyncSession` + `aiosqlite` keeps everything non-blocking. Both are already in `pyproject.toml`.

### Single `AsyncSession` factory via dependency injection

A `get_db()` FastAPI dependency yields an `AsyncSession` per request and closes it on exit. All route handlers receive the session via `Depends(get_db)`. This makes handlers easy to test by overriding the dependency.

### `create_all` on startup, no Alembic yet

Schema changes during MVP are frequent enough that migration files would create more churn than value. `create_all` is idempotent for existing tables. When the schema stabilises post-MVP, a single Alembic baseline migration captures the final state.

### Curriculum seed in `lifespan`, not a CLI command

Seeding runs in the FastAPI `lifespan` async context manager, after `create_all`. It uses `INSERT OR IGNORE` (by slug) so restarts are safe. Keeping it in lifespan means `docker compose up` is the only command needed — no separate `seed` step.

### Flat router layout under `backend/app/api/`

One file per resource (`sessions.py`, `messages.py`, `topics.py`, `progress.py`). Each file exports a `router` that `main.py` includes with a prefix. No nested routers for MVP — the API surface is small enough that flat is clearer.

### `last_topic_id` updated in the mark-complete endpoint

`POST /api/sessions/{id}/topics/{slug}` inserts into `session_topics` and also updates `sessions.last_topic_id` in the same transaction. This keeps the sidebar query cheap (no subquery) and avoids a separate "update last topic" endpoint.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| `create_all` won't apply column additions to existing tables | Acceptable for MVP; document that schema changes require `docker compose down -v` to reset the volume during development |
| WAL pragma must be set per-connection, not per-session | Set via SQLAlchemy `@event.listens_for(engine.sync_engine, "connect")` — fires on every new connection |
| `INSERT OR IGNORE` in curriculum seed silently skips updates to existing topics | Intentional; slug is the stable key. To update topic metadata, delete rows and restart |
| No pagination on `GET /api/sessions/{id}/messages` | Acceptable for MVP sessions; add `limit`/`offset` if context windows grow large |

## Migration Plan

1. `docker compose up` — `create_all` creates all tables, lifespan seed populates `topics`
2. Verify with `GET /health` (existing), `GET /api/topics` (new)
3. No rollback needed — tables are additive and the SQLite file is in a Docker volume that can be reset with `docker compose down -v`
