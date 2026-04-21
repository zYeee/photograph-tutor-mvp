## ADDED Requirements

### Requirement: LiveKit Agents worker entry point
`backend/agent.py` SHALL implement a LiveKit Agents SDK worker using the `cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))` pattern. The worker SHALL connect to the LiveKit server specified by `LIVEKIT_URL` using the key and secret from `LIVEKIT_API_KEY` / `LIVEKIT_API_SECRET`.

#### Scenario: Worker starts and waits for room assignments
- **WHEN** `python agent.py dev` is run with valid `LIVEKIT_*` env vars
- **THEN** the worker SHALL connect to the LiveKit server and log a ready message
- **THEN** it SHALL wait for room job assignments without exiting

#### Scenario: Worker starts without OPENAI_API_KEY
- **WHEN** `OPENAI_API_KEY` is not set in the environment
- **THEN** the worker SHALL log a warning ("OPENAI_API_KEY not set — AI features disabled")
- **THEN** the worker SHALL still connect to LiveKit and NOT crash or exit

### Requirement: STT → LLM → TTS voice pipeline
The agent SHALL use a `VoiceAssistant` (or equivalent LiveKit Agents pipeline) composed of: OpenAI Whisper for STT, GPT-4o (`gpt-4o`) for LLM, and OpenAI TTS for speech synthesis. The pipeline SHALL be fully streaming — audio output SHALL begin playing before the LLM response is complete.

#### Scenario: Full voice round-trip
- **WHEN** a user speaks into the LiveKit room
- **THEN** the speech SHALL be transcribed by Whisper STT
- **THEN** the transcription SHALL be sent to GPT-4o with the session's system prompt and history
- **THEN** the LLM response SHALL be synthesised to speech by OpenAI TTS and played back in the room

#### Scenario: No audio response when OPENAI_API_KEY absent
- **WHEN** `OPENAI_API_KEY` is not set and a user speaks
- **THEN** the agent SHALL NOT attempt to call OpenAI APIs
- **THEN** the room SHALL remain connected; no error crash SHALL occur

### Requirement: Session context loaded at room join
When the agent's `entrypoint` is called for a room, the agent SHALL resolve the corresponding session by calling `GET /api/sessions` filtered by `livekit_room_name`, load session metadata (user_level, equipment_type, mode), and load prior message history from `GET /api/sessions/{id}/messages` before handling the first user turn.

#### Scenario: Agent loads prior transcript on room join
- **WHEN** the agent joins a room for a session that already has 10 prior messages
- **THEN** those 10 messages SHALL be injected into the GPT-4o context before the first user turn
- **THEN** the agent's first response SHALL be able to reference content from those prior messages

#### Scenario: Room with no matching session
- **WHEN** the agent joins a room whose name has no matching session in the API
- **THEN** the agent SHALL log an error and gracefully leave the room without crashing
