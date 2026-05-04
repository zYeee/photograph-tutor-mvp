## ADDED Requirements

### Requirement: Display session list in sidebar
The system SHALL fetch all sessions for the current user from `GET /api/sessions?user_id=<id>` and display them in a scrollable sidebar ordered by `started_at` descending.

Each row SHALL show:
- A mode badge (`Structured Learning` or `Scene Advice`)
- The `equipment_type` label
- The `last_topic` value, or the text "New session" when `last_topic` is null

#### Scenario: Sessions exist
- **WHEN** the sidebar loads and the API returns one or more sessions
- **THEN** each session appears as a row with mode badge, equipment_type, and last_topic (or "New session")
- **THEN** rows are ordered newest-first

#### Scenario: No sessions yet
- **WHEN** the sidebar loads and the API returns an empty list
- **THEN** the sidebar shows an empty state message (e.g., "No sessions yet")

#### Scenario: API error
- **WHEN** the API call fails
- **THEN** the sidebar shows an error message without crashing

### Requirement: Navigate to a session by clicking its row
The system SHALL make each session row clickable; clicking one SHALL load that session in the active session pane.

#### Scenario: User clicks a session row
- **WHEN** the user clicks a session row in the sidebar
- **THEN** the active session pane updates to show that session's details and transcript

### Requirement: Sidebar last_topic updates on revisit
After a session ends and a topic has been marked, the sidebar last_topic label SHALL reflect the updated value on the next sidebar load or refetch.

#### Scenario: Topic updated after session ends
- **WHEN** the user disconnects from a session that set a new last_topic
- **THEN** the sidebar refetches the session list
- **THEN** the row for that session shows the updated last_topic label
