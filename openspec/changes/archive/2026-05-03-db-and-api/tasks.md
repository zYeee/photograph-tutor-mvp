## 1. Models and Database Layer

- [x] 1.1 Create `backend/app/models.py` with SQLAlchemy `DeclarativeBase` and async-mapped models for all 8 tables: `User`, `Session`, `Message`, `Topic`, `SessionTopic`, `UserTopicProgress`, `PhotoSubmission`, `PhotoFeedback` — columns, types, and constraints matching `openspec/specs/database/schema.md`
- [x] 1.2 Update `backend/app/database.py`: create async engine from `DATABASE_URL`, register a `@event.listens_for(engine.sync_engine, "connect")` handler that sets `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON`, define `AsyncSessionLocal` factory, and expose `get_db()` dependency
- [x] 1.3 Add `async_setup_db()` function to `database.py` that runs `create_all` on all models
- [x] 1.4 Create `backend/app/curriculum.py` with a hardcoded `TOPICS` list covering at least three root categories (e.g., Exposure, Composition, Lighting) with leaf topics under each — each entry has `slug`, `title`, `description`, `parent_slug` (or `None`), `difficulty`, `sort_order`
- [x] 1.5 Update the FastAPI `lifespan` in `main.py` to call `async_setup_db()` then seed `topics` from `TOPICS` using `INSERT OR IGNORE` by slug

## 2. Session Endpoints

- [x] 2.1 Create `backend/app/api/sessions.py` with `POST /api/sessions` — validate body, insert `Session` row, return HTTP 201 with session JSON
- [x] 2.2 Add `GET /api/sessions?user_id=<id>` to `sessions.py` — query sessions for user ordered by `started_at DESC`, LEFT JOIN topics for `last_topic` title, return list
- [x] 2.3 Add `GET /api/sessions/{id}` to `sessions.py` — return single session with `last_topic` title or HTTP 404
- [x] 2.4 Add `PATCH /api/sessions/{id}/close` to `sessions.py` — set `ended_at = now()`, optionally store `summary` from body, return HTTP 200
- [x] 2.5 Register sessions router in `main.py` with prefix `/api`

## 3. Message Endpoints

- [x] 3.1 Create `backend/app/api/messages.py` with `POST /api/sessions/{id}/messages` — validate `role` enum, insert `Message` row, return HTTP 201
- [x] 3.2 Add `GET /api/sessions/{id}/messages` to `messages.py` — return all messages for session ordered by `created_at ASC`
- [x] 3.3 Register messages router in `main.py` with prefix `/api`

## 4. Topics Endpoints

- [x] 4.1 Create `backend/app/api/topics.py` with `GET /api/topics` — load all topics, build nested tree (root categories with `children` list sorted by `sort_order`), return JSON
- [x] 4.2 Add `POST /api/sessions/{id}/topics/{slug}` to `topics.py` — look up topic by slug (404 if missing), insert into `session_topics` if not present, update `sessions.last_topic_id`, return HTTP 201 or 200 (already complete)
- [x] 4.3 Add `GET /api/sessions/{id}/topics` to `topics.py` — return `session_topics` rows joined with topic details ordered by `completed_at ASC`
- [x] 4.4 Register topics router in `main.py` with prefix `/api`

## 5. Progress Endpoints

- [x] 5.1 Create `backend/app/api/progress.py` with `GET /api/users/{id}/progress` — return all `user_topic_progress` rows for user joined with topic slug and title
- [x] 5.2 Add `PUT /api/users/{id}/progress/{slug}` to `progress.py` — upsert `user_topic_progress` row (insert or update `status`, `proficiency`, `last_visited_at`, `updated_at`)
- [x] 5.3 Register progress router in `main.py` with prefix `/api`

## 6. Verification

- [x] 6.1 Run `docker compose up --build` and confirm all services start cleanly with no DB errors in backend logs
- [x] 6.2 Verify `GET /health` still returns `{"status":"ok"}`
- [x] 6.3 Verify `GET /api/topics` returns the seeded curriculum tree with nested children
- [x] 6.4 Verify `POST /api/sessions` creates a session and `GET /api/sessions?user_id=<id>` lists it with `last_topic: null`
- [x] 6.5 Verify `POST /api/sessions/{id}/messages` and `GET /api/sessions/{id}/messages` round-trip correctly
- [x] 6.6 Verify `POST /api/sessions/{id}/topics/{slug}` updates `last_topic_id` and `GET /api/sessions?user_id=<id>` shows the topic title in `last_topic`
- [x] 6.7 Verify `PUT /api/users/{id}/progress/{slug}` and `GET /api/users/{id}/progress` round-trip correctly
- [x] 6.8 Run `docker compose down && docker compose up` and confirm the seeded topics and any test rows persist (SQLite volume survives restart)
