## 1. Extend curriculum.py

- [x] 1.1 Add a `level` field (`"beginner"` | `"intermediate"` | `"advanced"`) and a per-level `sort_order` (int) to every entry in `backend/app/curriculum.py`
- [x] 1.2 Add `teaching_points: list[str]` to every entry — 3–5 bullet sentences describing what the agent should cover
- [x] 1.3 Add `assessment_questions: list[str]` to every entry — 2–3 questions the agent can ask to gauge understanding
- [x] 1.4 Assign levels per the curriculum plan: beginner topics = exposure triangle, aperture, shutter speed, ISO, rule of thirds, leading lines, focal length, basic focus; intermediate = depth of field, histogram, framing, negative space, fill flash, catchlight, white balance, exposure correction; advanced = hyperfocal distance, bokeh, color grading, golden ratio, Rembrandt lighting, blue hour, and at least 2 more creative/advanced technique topics
- [x] 1.5 Verify final count: `len([t for t in TOPICS if t["level"]=="beginner"]) >= 6`, same check for intermediate (≥8) and advanced (≥8), total ≥20

## 2. Add next-topic endpoint

- [x] 2.1 In `backend/app/api/topics.py`, add `GET /sessions/{session_id}/next-topic` route
- [x] 2.2 Load session by ID; return HTTP 404 if not found
- [x] 2.3 Query `session_topics JOIN topics` to collect the set of covered slugs for this session
- [x] 2.4 Import `TOPICS` from `app.curriculum`; filter by `entry["level"] == session.user_level`; exclude covered slugs; sort by `entry["sort_order"]`
- [x] 2.5 If filtered list is empty, return `{"next_topic": null}`; otherwise return the first entry dict (all keys including `teaching_points` and `assessment_questions`)

## 3. Acceptance criteria smoke tests

- [x] 3.1 Start the backend (`make up` or `uv run uvicorn app.main:app --reload`) and confirm no import errors
- [x] 3.2 Verify `GET /api/topics` response contains no `teaching_points` or `assessment_questions` fields
- [x] 3.3 Create a test session with `user_level=beginner` via `POST /api/sessions`; call `GET /api/sessions/{id}/next-topic` and confirm the response contains `slug`, `teaching_points`, and `assessment_questions`
- [x] 3.4 Mark that topic complete via `POST /api/sessions/{id}/topics/{slug}`; re-call next-topic and confirm the completed topic is no longer returned
- [x] 3.5 Mark all beginner topics complete via the mark-complete endpoint; confirm `GET /api/sessions/{id}/next-topic` returns `{"next_topic": null}`
- [x] 3.6 Confirm total topic count in `curriculum.py` is ≥20 across all levels with a quick Python one-liner: `python -c "from app.curriculum import TOPICS; print(len(TOPICS))"`
