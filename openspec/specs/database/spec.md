## Context

No new database tables are required for this change. The existing schema already covers all needs:

| Table | How it's used |
|-------|---------------|
| `topics` | Stores slugs as FK references; `slug` is the join key between DB and `curriculum.py` |
| `session_topics` | Records which topics have been covered in a session (already has `session_id`, `topic_id`, `completed_at`) |
| `sessions` | `user_level` column (CHECK: beginner/intermediate/advanced) drives topic filtering in the next-topic endpoint |

This spec file documents the no-change boundary: curriculum-design deliberately keeps teaching content out of the DB.

## ADDED Requirements

### Requirement: topics table contains only structural data
The `topics` table SHALL NOT have `teaching_points`, `assessment_questions`, or any other agent-guidance columns added. It remains a lightweight FK reference table with `slug`, `title`, `description`, `difficulty`, `sort_order`, and `parent_id`.

#### Scenario: Topics table schema unchanged
- **WHEN** the schema is inspected after this change is applied
- **THEN** the `topics` table SHALL have exactly the same columns as before: `id`, `slug`, `title`, `description`, `parent_id`, `difficulty`, `sort_order`
- **THEN** no new columns SHALL be present on `topics`, `session_topics`, or `sessions`

#### Scenario: GET /api/topics response shape unchanged
- **WHEN** `GET /api/topics` is called after deploying this change
- **THEN** the JSON response structure SHALL be identical to its pre-change shape
- **THEN** no new fields SHALL appear in topic objects
