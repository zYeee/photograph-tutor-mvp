## Context

The existing backend scaffold already has the right DB shape:
- `topics` table: `id`, `slug`, `title`, `description`, `difficulty`, `sort_order`, `parent_id` — seeded from `curriculum.py`
- `session_topics` table: `session_id`, `topic_id`, `completed_at` — tracks which topics were covered in a session
- `sessions` table: `user_level` (CHECK IN beginner/intermediate/advanced), `equipment_type` — set at session creation
- `curriculum.py`: currently a flat `TOPICS` list with slugs, titles, descriptions — no level or agent-guidance fields

The current `topics.py` router already has `POST /sessions/{id}/topics/{slug}` (mark complete) and `GET /sessions/{id}/topics` (list covered). What's missing is the forward-looking endpoint — "what next?" — and the rich agent-facing content in `curriculum.py`.

Assessment (determining user_level) happens in `agent.py` at session creation time and is out of scope for this change. `user_level` is already stored in the `sessions` row.

## Goals / Non-Goals

**Goals:**
- Restructure `curriculum.py` with ≥20 topics across 3 levels; each topic has `teaching_points` and `assessment_questions`
- Implement `GET /api/sessions/{id}/next-topic` using Python curriculum as content source, DB as state
- Guarantee `GET /api/topics` never exposes `teaching_points` or `assessment_questions`

**Non-Goals:**
- Assessment flow (which level a user is at) — that is `agent.py` scope
- Storing `teaching_points` or `assessment_questions` in the DB
- Cross-session topic progression (within a single session only for MVP)
- Frontend UI for curriculum progress

## Decisions

### 1. Curriculum content stays in Python, not the DB

**Decision**: `curriculum.py` is the single source of truth for `teaching_points`, `assessment_questions`, `level`, and per-level `sort_order`. The DB `topics` table holds only what the DB needs: `slug`, `title`, `description`, `difficulty`, and a global `sort_order` for seeding.

**Rationale**: Teaching content is authored, reviewed in code, and changes with curriculum iterations — not ad-hoc admin edits. Putting it in the DB would require a CMS or migration for every content update. A Python file is diffable, testable, and deployable without a schema change.

**Alternative considered**: Store `teaching_points` as a JSON column on `topics` — rejected because it blurs the content/FK boundary and breaks the acceptance criterion ("no teaching_points in DB").

---

### 2. Two `sort_order` values: global DB sort vs. per-level curriculum sort

**Decision**: `topics.sort_order` in the DB is for global ordering (used by `GET /api/topics`). `curriculum.py` entries have a separate `sort_order` field scoped within a level. The next-topic endpoint uses only the curriculum `sort_order` — it never reads `topics.sort_order`.

**Rationale**: A beginner's "sort_order=0" topic is not the same as the globally first topic. Separating them avoids coupling content sequencing to DB ordering.

---

### 3. next-topic endpoint placement

**Decision**: Add `GET /api/sessions/{id}/next-topic` to `backend/app/api/topics.py` (alongside the existing session-topics routes).

**Rationale**: It's logically a topic-selection operation scoped to a session. The `topics.py` router already imports `Session`, `SessionTopic`, and `Topic` — no new imports needed.

**Alternative considered**: Add to `sessions.py` router — rejected to keep the sessions router focused on lifecycle (create, list, close).

---

### 4. next-topic algorithm

```
GET /api/sessions/{id}/next-topic

1. Load session → get user_level. If session not found → 404.
2. Query session_topics JOIN topics WHERE session_id={id} → set of covered slugs.
3. From curriculum.TOPICS, filter: entry["level"] == user_level.
4. Exclude entries whose slug is in covered slugs.
5. Sort remaining by entry["sort_order"] ascending.
6. If list is empty → return {"next_topic": null}.
7. Else → return the first entry (full curriculum dict: slug, title, level,
   sort_order, description, teaching_points, assessment_questions).
```

```
Request flow:

┌──────────────────┐   GET /api/sessions/{id}/next-topic   ┌──────────────────┐
│  agent.py /      │ ─────────────────────────────────────► │  topics.py       │
│  frontend        │                                         │  router          │
└──────────────────┘                                         └────────┬─────────┘
                                                                      │
                                              ┌───────────────────────┼────────────────────────┐
                                              │ DB reads              │                        │
                                              ▼                       ▼                        │
                                    ┌──────────────────┐   ┌──────────────────┐               │
                                    │ sessions         │   │ session_topics   │               │
                                    │ → user_level     │   │ JOIN topics      │               │
                                    └──────────────────┘   │ → covered slugs  │               │
                                                            └──────────────────┘               │
                                                                      │                        │
                                                                      ▼                        │
                                                            ┌──────────────────┐               │
                                                            │ curriculum.py    │               │
                                                            │ TOPICS list      │               │
                                                            │ filter by level  │               │
                                                            │ exclude covered  │               │
                                                            │ sort by order    │               │
                                                            └──────────────────┘               │
                                                                      │                        │
                                                                      ▼                        │
                                                            ┌──────────────────┐               │
                                                            │ return next      │               │
                                                            │ topic dict or    │◄──────────────┘
                                                            │ {next_topic:null}│
                                                            └──────────────────┘
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Slug mismatch: curriculum.py slug not in topics table | Curriculum seed must ensure every curriculum slug exists in the DB; add a startup assertion or unit test |
| `curriculum.py` sort_order gaps/duplicates per level | Treat sort_order as advisory (stable sort); document that gaps are OK |
| Level boundary: user finishes all beginner topics | Return `{"next_topic": null}` for MVP; tier promotion (auto-advance to intermediate) is a follow-up |
| Teaching content grows large in one file | File stays manageable at 20–30 entries; split into `curriculum/beginner.py` etc. if it exceeds ~500 lines |

## Migration Plan

1. Update `curriculum.py` in place — no DB migration needed
2. New endpoint is additive — no existing routes change
3. Rollback: revert `curriculum.py` and remove the new route

## Open Questions

- Should `next-topic` consider cross-session progress (`user_topic_progress` table) or only the current session's `session_topics`? — **Assumption for MVP**: current session only; cross-session progress is `user_topic_progress` scope (separate change)
- Should the endpoint auto-promote to the next level when all topics are done? — **Assumption for MVP**: return `null`; the agent handles the conversation about what comes next
