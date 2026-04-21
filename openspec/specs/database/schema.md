# Database Schema — Photography Tutor

SQLite database at `db/local.db` (Docker named volume `db-data`). Designed to be forward-compatible with PostgreSQL — no SQLite-exclusive types are used.

---

## Entity-Relationship Overview

```
users ──< sessions ──< messages          (conversation history / LLM memory)
               │
               ├── last_topic_id ──> topics
               └──< session_topics >── topics ──< topics (self, parent_id)

users ──< user_topic_progress >── topics (cross-session aggregate progress)

sessions ──< photo_submissions ──< photo_feedback
users    ──< photo_submissions
```

---

## Tables

### `users`

Identity record. No auth credentials are stored here — auth is out of scope for MVP.

| Column         | Type     | Constraints                             |
|----------------|----------|-----------------------------------------|
| `id`           | INTEGER  | PRIMARY KEY AUTOINCREMENT               |
| `email`        | TEXT     | UNIQUE NOT NULL                         |
| `display_name` | TEXT     | NOT NULL                                |
| `created_at`   | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP      |
| `updated_at`   | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP      |

---

### `sessions`

One row per voice session. Carries the learner's context: level, equipment, interaction mode, and a pointer to the last topic studied (used by the sidebar).

| Column              | Type     | Constraints                                                                       |
|---------------------|----------|-----------------------------------------------------------------------------------|
| `id`                | INTEGER  | PRIMARY KEY AUTOINCREMENT                                                         |
| `user_id`           | INTEGER  | NOT NULL REFERENCES users(id)                                                     |
| `livekit_room_name` | TEXT     | UNIQUE NOT NULL                                                                   |
| `mode`              | TEXT     | NOT NULL CHECK(mode IN ('structured_learning', 'scene_advice'))                   |
| `user_level`        | TEXT     | NOT NULL CHECK(user_level IN ('beginner', 'intermediate', 'advanced'))            |
| `equipment_type`    | TEXT     | NOT NULL CHECK(equipment_type IN ('smartphone', 'mirrorless', 'dslr', 'point-and-shoot', 'film')) |
| `last_topic_id`     | INTEGER  | NULL REFERENCES topics(id)                                                        |
| `started_at`        | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP                                                |
| `ended_at`          | DATETIME | NULL                                                                              |
| `summary`           | TEXT     | NULL                                                                              |

**`user_level`** — set at session start (user self-reports or carries over from prior sessions). Guides the agent's vocabulary and depth of explanation.

**`equipment_type`** — determines which camera controls and concepts are relevant during the session.

**`last_topic_id`** — updated in-place whenever the session moves to a new topic. Drives the "last topic" column in the session sidebar list without a JOIN to `session_topics`. NULL until the first topic is covered.

**`ended_at IS NULL`** — session is active. Populated when the LiveKit room closes.

**`summary`** — AI-generated session summary written at session close.

**Interaction modes:**
- `structured_learning` — agent follows curriculum, tracks topic progress, advances through the topic tree
- `scene_advice` — agent gives ad-hoc feedback on a submitted photo; topic tracking is optional

---

### `messages`

Full conversation history for a session. The entire table (filtered by `session_id`, ordered by `created_at`) is injected into the LLM context window at session resume to restore conversational memory.

| Column        | Type     | Constraints                                             |
|---------------|----------|---------------------------------------------------------|
| `id`          | INTEGER  | PRIMARY KEY AUTOINCREMENT                               |
| `session_id`  | INTEGER  | NOT NULL REFERENCES sessions(id)                        |
| `role`        | TEXT     | NOT NULL CHECK(role IN ('user', 'assistant', 'system')) |
| `content`     | TEXT     | NOT NULL                                               |
| `token_count` | INTEGER  | NULL                                                    |
| `created_at`  | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP                      |

**`token_count`** — stored at insert time (cheap to compute, expensive to reconstruct). Used for session cost tracking and context-window budget enforcement.

**LLM memory injection pattern:**
```
SELECT role, content FROM messages
WHERE session_id = :sid
ORDER BY created_at ASC
```
Result is prepended to the next LLM call as the conversation history array.

---

### `topics`

Seeded reference table. The curriculum is defined as a hardcoded Python constant in `backend/app/curriculum.py` and inserted into this table at application startup (idempotent — skips rows whose `slug` already exists). Updates to the curriculum require changing the Python constant and restarting the container.

| Column        | Type    | Constraints                                  |
|---------------|---------|----------------------------------------------|
| `id`          | INTEGER | PRIMARY KEY AUTOINCREMENT                    |
| `slug`        | TEXT    | UNIQUE NOT NULL                              |
| `title`       | TEXT    | NOT NULL                                     |
| `description` | TEXT    | NULL                                         |
| `parent_id`   | INTEGER | NULL REFERENCES topics(id)                   |
| `difficulty`  | INTEGER | NOT NULL CHECK(difficulty BETWEEN 1 AND 5)   |
| `sort_order`  | INTEGER | NOT NULL DEFAULT 0                           |

**`parent_id IS NULL`** — root category (e.g., `exposure`, `composition`, `lighting`).
**`parent_id IS NOT NULL`** — leaf topic under a category (e.g., `aperture`, `shutter-speed`, `rule-of-thirds`).

Example slugs: `exposure`, `aperture`, `shutter-speed`, `iso`, `depth-of-field`, `composition`, `rule-of-thirds`, `golden-hour`, `lighting`, `catch-light`.

---

### `session_topics`

Records which topics were covered (and completed) within a specific session. Supports the "completed topics" requirement at session scope. Also feeds `user_topic_progress` aggregate.

| Column         | Type     | Constraints                                |
|----------------|----------|--------------------------------------------|
| `id`           | INTEGER  | PRIMARY KEY AUTOINCREMENT                  |
| `session_id`   | INTEGER  | NOT NULL REFERENCES sessions(id)           |
| `topic_id`     | INTEGER  | NOT NULL REFERENCES topics(id)             |
| `completed_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP         |

**Unique constraint:** `UNIQUE(session_id, topic_id)` — a topic is recorded once per session regardless of how many times it was mentioned.

**Query — completed topics for a session:**
```
SELECT t.slug, t.title, st.completed_at
FROM session_topics st
JOIN topics t ON t.id = st.topic_id
WHERE st.session_id = :sid
ORDER BY st.completed_at ASC
```

---

### `user_topic_progress`

Cross-session aggregate of per-user topic mastery. Updated each time a topic is completed in any session.

| Column            | Type     | Constraints                                                                               |
|-------------------|----------|-------------------------------------------------------------------------------------------|
| `id`              | INTEGER  | PRIMARY KEY AUTOINCREMENT                                                                 |
| `user_id`         | INTEGER  | NOT NULL REFERENCES users(id)                                                             |
| `topic_id`        | INTEGER  | NOT NULL REFERENCES topics(id)                                                            |
| `status`          | TEXT     | NOT NULL DEFAULT 'not_started' CHECK(status IN ('not_started', 'in_progress', 'completed')) |
| `proficiency`     | REAL     | NULL CHECK(proficiency BETWEEN 0.0 AND 1.0)                                               |
| `last_visited_at` | DATETIME | NULL                                                                                      |
| `updated_at`      | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP                                                        |

**Unique constraint:** `UNIQUE(user_id, topic_id)`

---

### `photo_submissions`

Photos submitted by a user within a session for AI critique.

| Column         | Type     | Constraints                             |
|----------------|----------|-----------------------------------------|
| `id`           | INTEGER  | PRIMARY KEY AUTOINCREMENT               |
| `user_id`      | INTEGER  | NOT NULL REFERENCES users(id)           |
| `session_id`   | INTEGER  | NOT NULL REFERENCES sessions(id)        |
| `storage_path` | TEXT     | NOT NULL                               |
| `caption`      | TEXT     | NULL                                    |
| `submitted_at` | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP      |

**`storage_path`** — relative container path, e.g., `uploads/<user_id>/<uuid>.jpg`. No file deduplication at the DB level.

---

### `photo_feedback`

AI-generated critique for a submitted photo. One record per submission (1:1).

| Column              | Type     | Constraints                                                     |
|---------------------|----------|-----------------------------------------------------------------|
| `id`                | INTEGER  | PRIMARY KEY AUTOINCREMENT                                       |
| `submission_id`     | INTEGER  | NOT NULL REFERENCES photo_submissions(id) UNIQUE               |
| `message_id`        | INTEGER  | NULL REFERENCES messages(id)                                    |
| `composition_score` | REAL     | NULL CHECK(composition_score BETWEEN 0.0 AND 1.0)              |
| `exposure_score`    | REAL     | NULL CHECK(exposure_score BETWEEN 0.0 AND 1.0)                 |
| `focus_score`       | REAL     | NULL CHECK(focus_score BETWEEN 0.0 AND 1.0)                    |
| `lighting_score`    | REAL     | NULL CHECK(lighting_score BETWEEN 0.0 AND 1.0)                 |
| `overall_score`     | REAL     | NULL CHECK(overall_score BETWEEN 0.0 AND 1.0)                  |
| `notes`             | TEXT     | NULL                                                            |
| `created_at`        | DATETIME | NOT NULL DEFAULT CURRENT_TIMESTAMP                              |

**`UNIQUE` on `submission_id`** — one feedback row per photo. Re-analysis updates the existing row.
**`message_id`** — links back to the conversation turn that produced the critique. NULL for offline/batch feedback.

---

## Indexing Strategy

| Index                           | Table                  | Columns                     | Query it serves                        |
|---------------------------------|------------------------|-----------------------------|----------------------------------------|
| `idx_sessions_user_id`          | `sessions`             | `user_id`                   | Session list for sidebar               |
| `idx_sessions_livekit_room`     | `sessions`             | `livekit_room_name`         | Agent room → session lookup            |
| `idx_messages_session_created`  | `messages`             | `session_id, created_at`    | LLM memory injection (ordered load)    |
| `idx_session_topics_session`    | `session_topics`       | `session_id`                | Completed topics per session           |
| `idx_session_topics_topic`      | `session_topics`       | `topic_id`                  | Sessions that covered a topic          |
| `idx_user_topic_progress_user`  | `user_topic_progress`  | `user_id`                   | Full user progress load                |
| `idx_photo_submissions_session` | `photo_submissions`    | `session_id`                | Photos in a session                    |
| `idx_photo_submissions_user`    | `photo_submissions`    | `user_id`                   | User gallery view                      |

Primary keys and columns with `UNIQUE` constraints are automatically indexed by SQLite.

---

## Key Query Patterns

### Sidebar session list (last topic per session)

```sql
SELECT
    s.id,
    s.mode,
    s.user_level,
    s.equipment_type,
    s.started_at,
    s.ended_at,
    t.title  AS last_topic
FROM sessions s
LEFT JOIN topics t ON t.id = s.last_topic_id
WHERE s.user_id = :uid
ORDER BY s.started_at DESC
```

`last_topic_id` on `sessions` makes this a single LEFT JOIN with no subquery.

### LLM memory injection

```sql
SELECT role, content
FROM messages
WHERE session_id = :sid
ORDER BY created_at ASC
```

### Completed topics in a session

```sql
SELECT t.slug, t.title, st.completed_at
FROM session_topics st
JOIN topics t ON t.id = st.topic_id
WHERE st.session_id = :sid
ORDER BY st.completed_at ASC
```

---

## Connection Pragmas

Both must be set on every new connection before any query:

```
PRAGMA journal_mode = WAL;     -- concurrent reads from multiple processes
PRAGMA foreign_keys = ON;      -- enforce referential integrity
```

---

## Design Decisions

### `last_topic_id` on `sessions` vs. derived from `session_topics`

Storing `last_topic_id` directly on `sessions` avoids a `MAX(completed_at)` subquery in every sidebar load. The cost is one extra UPDATE per topic transition during a session — acceptable given the low write frequency.

### `session_topics` separate from `user_topic_progress`

Session-scoped completion (`session_topics`) and lifetime progress (`user_topic_progress`) serve different read patterns. The sidebar needs session-scoped data; the curriculum overview needs lifetime data. Merging them into one table would require grouping on every sidebar query.

### `user_level` and `equipment_type` on `sessions`, not `users`

A learner's level and equipment can change across sessions (upgrade from smartphone to mirrorless, or self-assess as intermediate after more practice). Storing on `sessions` preserves history and allows the agent to observe progression over time.

### Hard-coded curriculum seeded into `topics` table

The curriculum lives in `backend/app/curriculum.py` as a Python list of dicts. At startup, the app performs an upsert-or-skip over every entry — existing rows are left unchanged, new slugs are inserted. This keeps the schema relational (FK integrity, joins, indexes) while avoiding a separate migration step for curriculum changes during the MVP phase. Moving to a DB-managed curriculum later is a straightforward additive change: remove the seed call and manage rows directly.

### No CASCADE deletes

Deleting a user or session is blocked if dependent rows exist. Deletions must be explicit and ordered (messages → session_topics → sessions → users). This prevents accidental data loss from a stale FK reference.

---

## Open Questions

1. **Anonymous users** — `email` is NOT NULL for MVP. Every session requires a user record. Revisit if guest/anonymous access is needed.
2. **Photo storage** — using container volume (`uploads/`) for MVP. `storage_path` stores a relative path. Migrate to object storage (S3/R2) by changing the path to a URL — no schema change required.
3. **Topic hierarchy depth** — two levels (category → topic) is sufficient for MVP.
4. **`equipment_type` extensibility** — CHECK constraint with five known types for MVP. Add `'other'` to the CHECK list if free-form equipment is needed before a schema migration is warranted.
