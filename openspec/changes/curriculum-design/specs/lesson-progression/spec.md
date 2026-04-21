## ADDED Requirements

### Requirement: Next-topic endpoint
The system SHALL expose `GET /api/sessions/{id}/next-topic` that returns the next recommended topic for a session. The endpoint SHALL: (1) load the session to obtain `user_level`; (2) query `session_topics` to find topic slugs already covered in this session; (3) filter `curriculum.TOPICS` by `level == user_level`, exclude covered slugs, sort by `sort_order` ascending; (4) return the first remaining entry as a full curriculum dict (including `teaching_points` and `assessment_questions`); (5) return `{"next_topic": null}` when all topics for the level are covered.

#### Scenario: Fresh session returns first beginner topic
- **WHEN** `GET /api/sessions/{id}/next-topic` is called for a session with `user_level=beginner` and no session_topics rows
- **THEN** the response SHALL return the beginner topic with `sort_order=0`

#### Scenario: Covered topics are excluded
- **WHEN** a session has completed 3 beginner topics
- **THEN** `GET /api/sessions/{id}/next-topic` SHALL return the beginner topic with the lowest `sort_order` not yet in `session_topics`

#### Scenario: All level topics complete returns null
- **WHEN** all beginner topics (as defined in `curriculum.TOPICS`) are present in `session_topics`
- **THEN** the response SHALL be `{"next_topic": null}`

#### Scenario: Response includes agent-facing fields
- **WHEN** a next topic is available
- **THEN** the response SHALL include `slug`, `title`, `level`, `sort_order`, `description`, `teaching_points`, and `assessment_questions`

#### Scenario: Unknown session returns 404
- **WHEN** `GET /api/sessions/99999/next-topic` is called with a non-existent session ID
- **THEN** the response SHALL be HTTP 404

### Requirement: Existing topic-completion endpoint unchanged
`POST /api/sessions/{id}/topics/{slug}` (already implemented) SHALL remain the mechanism for recording that a topic was covered. The next-topic endpoint reads from `session_topics`; it does not write to it.

#### Scenario: Mark topic complete then call next-topic
- **WHEN** `POST /api/sessions/{id}/topics/exposure-triangle` succeeds
- **AND** `GET /api/sessions/{id}/next-topic` is called immediately after
- **THEN** `exposure-triangle` SHALL NOT appear in the response
- **THEN** the next topic with a higher `sort_order` SHALL be returned
