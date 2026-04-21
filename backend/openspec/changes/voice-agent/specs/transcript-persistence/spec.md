## ADDED Requirements

### Requirement: User turns saved to messages API
After each user speech turn is committed (transcription finalised by STT), the agent SHALL call `POST /api/sessions/{id}/messages` with `{"role": "user", "content": "<transcription>"}`.

#### Scenario: User speech turn saved
- **WHEN** a user finishes speaking and Whisper STT produces a final transcription
- **THEN** the agent SHALL call `POST /api/sessions/{id}/messages` with `role="user"` and the transcription text
- **THEN** the call SHALL succeed before the next user turn begins (best-effort; not blocking the audio pipeline)

#### Scenario: Message saved with correct session ID
- **WHEN** messages are posted during a session
- **THEN** `GET /api/sessions/{id}/messages` SHALL return all posted messages associated with that session's ID

### Requirement: Agent turns saved to messages API
After each agent response is fully synthesised and played, the agent SHALL call `POST /api/sessions/{id}/messages` with `{"role": "assistant", "content": "<agent text response>"}`.

#### Scenario: Agent response saved
- **WHEN** the agent completes a response turn
- **THEN** `POST /api/sessions/{id}/messages` SHALL be called with `role="assistant"` and the full agent response text
- **THEN** `GET /api/sessions/{id}/messages` after the session SHALL show both the user and assistant turns in chronological order

### Requirement: Prior transcript injected into system context
At room join, the prior message history loaded from `GET /api/sessions/{id}/messages` SHALL be injected into the GPT-4o `ChatContext` as alternating `user`/`assistant` messages, prepended before the first live user turn. History SHALL be capped at the most recent 50 messages.

#### Scenario: Session reopened with prior transcript
- **WHEN** a user rejoins a session that had 8 prior message turns
- **THEN** the agent's first response SHALL be coherent with and reference the prior conversation context
- **THEN** `GET /api/sessions/{id}/messages` SHALL eventually show more than 8 messages (new turns appended)

#### Scenario: History cap applied
- **WHEN** a session has 80 prior messages
- **THEN** the agent SHALL inject only the 50 most recent messages into the GPT-4o context
- **THEN** the oldest 30 SHALL be silently dropped from the injection (not from the database)
