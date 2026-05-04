## 1. Prerequisites and Dependencies

- [x] 1.1 Verify `livekit-agents`, `livekit-plugins-openai`, `livekit-plugins-silero`, `httpx` are in `backend/pyproject.toml`; add any that are missing and run `uv sync`
- [x] 1.2 Add `PATCH /api/sessions/{id}` route to `backend/app/api/sessions.py` accepting `{"user_level": str, "equipment_type": str}` — needed by the assessment flow to store determined level

## 2. Session PATCH Endpoint

- [x] 2.1 In `backend/app/api/sessions.py`, add a `SessionPatch` Pydantic model with optional `user_level` and `equipment_type` fields
- [x] 2.2 Add `PATCH /sessions/{session_id}` route that updates only the provided fields and returns the updated session row

## 3. Core Agent Scaffold

- [x] 3.1 Rewrite `backend/agent.py` with the LiveKit Agents SDK entry point: `async def entrypoint(ctx: JobContext)` and `cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))` in `if __name__ == "__main__"`
- [x] 3.2 At startup, check for `OPENAI_API_KEY`; if absent log a warning and skip OpenAI plugin initialisation (agent stays connected in no-op mode)
- [x] 3.3 In `entrypoint`, call `ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)` then resolve the session: `GET /api/sessions?livekit_room_name={ctx.room.name}` via `httpx.AsyncClient`; if no session found, log error and return
- [x] 3.4 Call `GET /api/sessions/{id}/messages` and load the prior message list (cap at 50 most recent)

## 4. System Prompt Construction

- [x] 4.1 Write a `build_system_prompt(session, next_topic)` function that returns a prompt string including: mode-specific persona, user level + equipment type, and (structured learning only) the current topic title + teaching_points joined as bullet points
- [x] 4.2 Build the initial `llm.ChatContext`: system prompt as first message, then prior messages injected as alternating user/assistant turns

## 5. VoiceAssistant Pipeline

- [x] 5.1 Instantiate `VoiceAssistant` with Silero VAD, OpenAI Whisper STT (`openai.STT()`), GPT-4o LLM (`openai.LLM(model="gpt-4o")`), OpenAI TTS (`openai.TTS()`), and the initial `ChatContext`
- [x] 5.2 Call `assistant.start(ctx.room)` and keep the entrypoint alive with `await asyncio.sleep(float("inf"))`

## 6. Intent Routing

- [x] 6.1 After connecting, read `session["mode"]` and `session["user_level"]`
- [x] 6.2 For `structured_learning` with `user_level` set: call `GET /api/sessions/{id}/next-topic`; if a topic is returned, have the assistant say an opening message introducing it
- [x] 6.3 For `structured_learning` with no `user_level`: have the assistant open with the 2-question assessment (experience level + equipment); on receiving answers, call `PATCH /api/sessions/{id}` with the determined values, then introduce the first topic
- [x] 6.4 For `scene_advice`: have the assistant open with the scene-description invitation

## 7. Transcript Persistence

- [x] 7.1 Subscribe to the `on_user_speech_committed` (or equivalent) event; in the handler POST `{"role": "user", "content": transcript}` to `/api/sessions/{id}/messages` via httpx
- [x] 7.2 Subscribe to the `on_agent_speech_committed` (or equivalent) event; POST `{"role": "assistant", "content": agent_text}` to `/api/sessions/{id}/messages`

## 8. Topic Coverage Tracking

- [x] 8.1 Track `current_topic_slug` in a closure or session-local variable set during intent routing
- [x] 8.2 On room disconnect (participant left / `ctx.room.on("disconnected")`), if in structured-learning mode and `current_topic_slug` is set: call `POST /api/sessions/{id}/topics/{slug}` and `PUT /api/users/{user_id}/progress/{slug}` with `{"status": "completed"}`

## 9. Docker Compose

- [x] 9.1 Add an `agent` service to `docker-compose.yml`: image built from `./backend`, command `uv run python agent.py dev`, same `volumes` + `env_file` as `backend`, `environment: LIVEKIT_URL=ws://livekit:7880`, `depends_on: livekit (healthy) + backend (started)`

## 10. Smoke Tests

- [x] 10.1 Run `docker compose up --build`; confirm the `agent` container starts without errors and logs a LiveKit connection message
- [x] 10.2 With `OPENAI_API_KEY` unset, confirm `agent` logs a warning but stays running (does not exit)
- [x] 10.3 Create a session via `POST /api/sessions` with `mode=structured_learning` and `user_level=beginner`; connect a LiveKit client to the room and confirm the agent joins and speaks an opening message
- [ ] 10.4 Speak a test phrase; confirm `GET /api/sessions/{id}/messages` shows at least one user turn and one assistant turn after the exchange
- [ ] 10.5 Disconnect from the room; confirm `GET /api/sessions/{id}/topics` shows at least one topic marked complete and `GET /api/users/{id}/progress` shows the corresponding slug as `completed`
- [ ] 10.6 Create a second session reusing the same `user_id`; reconnect and confirm the agent's first response references the prior session content
