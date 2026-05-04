## ADDED Requirements

### Requirement: Connect to LiveKit voice room
The system SHALL provide a Connect button in the active session view. Clicking it SHALL fetch a token from `GET /api/token?room=<livekit_room_name>` and join the LiveKit room using `@livekit/components-react`.

#### Scenario: User connects successfully
- **WHEN** the user clicks "Connect" and the token fetch succeeds
- **THEN** the browser joins the LiveKit room
- **THEN** agent audio plays through the browser speakers
- **THEN** a "Listening..." indicator is shown
- **THEN** the Connect button changes to "Disconnect"

#### Scenario: Token fetch fails
- **WHEN** `GET /api/token` returns an error
- **THEN** an error message is displayed
- **THEN** the user remains disconnected

### Requirement: Show agent speaking indicator
While the LiveKit agent is producing audio output, the system SHALL show a "Tutor speaking..." indicator.

#### Scenario: Agent starts speaking
- **WHEN** the agent's audio track becomes active in the room
- **THEN** the UI shows "Tutor speaking..."

#### Scenario: Agent stops speaking
- **WHEN** the agent's audio track goes silent
- **THEN** the "Tutor speaking..." indicator is hidden and "Listening..." is shown instead

### Requirement: Disconnect from voice room
The system SHALL provide a Disconnect button (shown when connected). Clicking it SHALL disconnect from the LiveKit room and close the session via `PATCH /api/sessions/{id}/close`.

#### Scenario: User disconnects
- **WHEN** the user clicks "Disconnect"
- **THEN** the LiveKit room connection is closed
- **THEN** `PATCH /api/sessions/{id}/close` is called
- **THEN** the button reverts to "Connect"
- **THEN** the sidebar session list is refetched
