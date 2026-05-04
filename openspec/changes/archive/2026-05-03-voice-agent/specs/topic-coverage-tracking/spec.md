## ADDED Requirements

### Requirement: Topic marked complete when session ends
In `structured_learning` mode, when the agent session ends (user disconnects from the room), the agent SHALL call `POST /api/sessions/{id}/topics/{slug}` with the slug of the topic that was being taught during the session.

#### Scenario: Topic marked on session end
- **WHEN** the agent was teaching the `aperture` topic in a structured-learning session
- **AND** the user disconnects from the LiveKit room
- **THEN** the agent SHALL call `POST /api/sessions/{id}/topics/aperture`
- **THEN** a subsequent `GET /api/sessions/{id}/next-topic` SHALL NOT return `aperture` for a new session at the same level

#### Scenario: No topic to mark in scene-advice mode
- **WHEN** `session.mode = "scene_advice"`
- **THEN** the agent SHALL NOT call the topic-complete endpoint at session end

#### Scenario: No next-topic available
- **WHEN** `GET /api/sessions/{id}/next-topic` returns `{"next_topic": null}` (all topics complete)
- **THEN** the agent SHALL NOT attempt to mark a topic complete
- **THEN** the agent SHALL congratulate the user on completing the level and suggest they could try the next level

### Requirement: User progress updated after topic coverage
After firing the topic-complete endpoint, the agent SHALL also call `PUT /api/users/{id}/progress/{slug}` with `{"status": "completed"}` to update the per-user cross-session progress record.

#### Scenario: User progress updated
- **WHEN** the agent marks `aperture` complete for session with `user_id=5`
- **THEN** `PUT /api/users/5/progress/aperture` SHALL be called with `{"status": "completed"}`
- **THEN** `GET /api/users/5/progress` SHALL show `aperture` with `status = "completed"`
