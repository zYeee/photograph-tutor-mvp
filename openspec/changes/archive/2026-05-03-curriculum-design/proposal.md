## Why

`backend/app/curriculum.py` already exists as a flat topic list with slugs, titles, and descriptions, but it has no concept of skill level, teaching agenda, or assessment questions. Without those fields, the agent has no structured guidance for what to teach or how to sequence topics for a learner's level, and the backend has no way to answer "what should this user tackle next?" The existing `sessions.user_level`, `topics`, and `session_topics` tables are already the right shape — they just lack the rich curriculum content to power a progression endpoint.

## What Changes

- Extend `backend/app/curriculum.py` to a fully structured curriculum: each topic entry gains `level` (beginner/intermediate/advanced), per-level `sort_order`, `teaching_points` (list of what the agent should cover), and `assessment_questions` (list of questions to gauge understanding). Target ≥20 topics spread across all three levels.
- Add `GET /api/sessions/{id}/next-topic` to the sessions API: reads the session's `user_level` from the DB, cross-references `session_topics` (topics already covered in this session), and returns the lowest `sort_order` remaining topic for that level from `curriculum.py`. Returns `null` when all level topics are complete.
- The `topics` DB table remains slug-only FK references; no rich content (`teaching_points`, `assessment_questions`) goes into the DB.

## Capabilities

### New Capabilities

- `next-topic-suggestion`: `GET /api/sessions/{id}/next-topic` endpoint that computes the next recommended topic for a session using the Python curriculum as the content source and `session_topics` as the completion log.

### Modified Capabilities

- `curriculum`: `backend/app/curriculum.py` is restructured — each entry gains `level`, `sort_order` (within level), `teaching_points`, and `assessment_questions`. The file becomes the authoritative content source; the DB retains only slugs.

## Impact

- **`backend/app/curriculum.py`**: significant content addition; existing slug list becomes a richer levelled structure
- **`backend/app/api/topics.py`** or **`sessions.py`**: one new route added (`GET /api/sessions/{id}/next-topic`)
- **Database**: no schema changes — `topics`, `session_topics`, and `sessions.user_level` already exist
- **Agent**: can now call `GET /api/sessions/{id}/next-topic` to know what to teach next; assessment flow (determining `user_level` at session creation) is a separate `agent.py` concern
- **`GET /api/topics`**: no change — returns DB fields only, never `teaching_points` or `assessment_questions` (acceptance criterion)
