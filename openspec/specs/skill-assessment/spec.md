## Context

Assessment (determining a user's level and equipment type at session start) is handled in `agent.py` and is **out of scope for this change**. The agent asks 2–3 diagnostic questions, then calls `POST /api/sessions` with the determined `user_level` and `equipment_type`. Both fields already exist as CHECK-constrained columns on the `sessions` table.

This spec file exists only to document the boundary: curriculum-design does not implement assessment logic. A future `agent-assessment` change will own the conversation flow and question set.

## ADDED Requirements

### Requirement: Assessment questions available on curriculum topics
Each topic in `curriculum.py` SHALL include an `assessment_questions` field (list of strings) so that the agent, during a session, can test learner understanding without needing a separate question bank service. These questions are accessed by the agent directly from the Python module — there is no REST endpoint for assessment questions.

#### Scenario: Agent reads assessment questions from curriculum
- **WHEN** the agent is teaching a topic and wants to check understanding
- **THEN** it SHALL access `curriculum.TOPICS` filtered by slug to retrieve `assessment_questions`
- **THEN** no HTTP call is needed — the curriculum module is imported directly in `agent.py`

#### Scenario: Assessment questions are not exposed via REST
- **WHEN** any public REST endpoint is called
- **THEN** `assessment_questions` SHALL NOT appear in responses from `GET /api/topics` or `GET /api/topics/{slug}`
- **THEN** `assessment_questions` are only available to server-side code that imports `curriculum.py`
