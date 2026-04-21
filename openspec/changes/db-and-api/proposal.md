## Why

The schema is fully designed and approved (`openspec/specs/database/schema.md`), but the backend has no models or API endpoints. Without them, no feature — voice sessions, learning progress, conversation memory — can persist data.

**Depends on:** `db-schema-design` (schema approved and finalized).

## What Changes

- Add SQLAlchemy async models for all 8 tables: `users`, `sessions`, `messages`, `topics`, `session_topics`, `user_topic_progress`, `photo_submissions`, `photo_feedback`
- Wire async SQLite engine with `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` at connection time
- Seed curriculum from `backend/app/curriculum.py` into `topics` table on startup (idempotent)
- Add REST API endpoints for sessions, messages, topics, and user progress
- Wire all new routers into the existing FastAPI app

**Acceptance criteria:**
- `GET /health` still returns `{"status":"ok"}`
- `POST /api/sessions` creates a session row and returns it
- `GET /api/sessions?user_id=<id>` returns session list with `last_topic` title from JOIN
- `GET /api/sessions/{id}/messages` returns full transcript ordered by `created_at`
- `POST /api/sessions/{id}/messages` appends a message row
- `GET /api/topics` returns the seeded curriculum tree
- `POST /api/sessions/{id}/topics/{slug}` marks a topic complete in `session_topics` and updates `sessions.last_topic_id`
- `GET /api/users/{id}/progress` returns `user_topic_progress` rows for a user
- All tables created on first `docker compose up` with no manual migration step

## Capabilities

### New Capabilities

- `db-models`: SQLAlchemy async ORM models for all 8 tables, engine/session factory, WAL+FK pragma setup, and curriculum seed on startup
- `rest-api`: FastAPI route handlers for sessions, messages, topics, and user progress

### Modified Capabilities

<!-- None — existing backend-scaffold requirements (health, LiveKit token) are unchanged -->

## Impact

- `backend/app/database.py` — extend with pragma setup and `create_all`
- `backend/app/models.py` — new file with all ORM models
- `backend/app/curriculum.py` — new file with hardcoded topic list
- `backend/app/api/` — new route modules: `sessions.py`, `messages.py`, `topics.py`, `progress.py`
- `backend/app/main.py` — register new routers, run curriculum seed in lifespan
- `backend/pyproject.toml` — no new dependencies (aiosqlite + sqlalchemy already present)
