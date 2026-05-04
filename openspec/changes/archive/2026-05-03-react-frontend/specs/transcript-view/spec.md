## ADDED Requirements

### Requirement: Load existing transcript on session open
When a session is opened in the active pane, the system SHALL fetch all messages from `GET /api/sessions/{id}/messages` and display them as a scrollable list of chat bubbles, with user messages right-aligned and assistant messages left-aligned.

#### Scenario: Session has prior messages
- **WHEN** the user opens a session that has existing messages
- **THEN** all messages are shown as bubbles in chronological order
- **THEN** the view scrolls to the most recent message

#### Scenario: Session has no messages yet
- **WHEN** the user opens a new session with no messages
- **THEN** an empty-state prompt is shown (e.g., "Connect and start speaking")

### Requirement: Real-time transcript updates during voice session
While the voice session is connected, the system SHALL poll `GET /api/sessions/{id}/messages` every 2 seconds and append any new messages to the transcript without duplicating existing ones.

#### Scenario: New message arrives during polling
- **WHEN** a new user or assistant message is added on the server between polls
- **THEN** the new bubble appears in the transcript within 2 seconds
- **THEN** the transcript auto-scrolls to the new message

#### Scenario: Polling stops on disconnect
- **WHEN** the user disconnects from the voice room
- **THEN** polling stops and no further fetches occur

### Requirement: Transcript header shows current topic
The active session view top bar SHALL display the session mode and the current `last_topic` (refreshed after each poll cycle).

#### Scenario: Session has a current topic
- **WHEN** the session's `last_topic` is non-null
- **THEN** the top bar shows the topic name

#### Scenario: Session has no topic yet
- **WHEN** `last_topic` is null
- **THEN** the top bar shows "No topic yet" or similar placeholder
