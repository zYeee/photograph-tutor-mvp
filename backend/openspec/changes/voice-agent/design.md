## Context

`backend/agent.py` is a 30-line stub that reads env vars and exits. It cannot connect to a LiveKit room, receive audio, or produce speech. The LiveKit Agents SDK, OpenAI Whisper STT, GPT-4o, and OpenAI TTS are already listed as dependencies in `pyproject.toml` and are present in the virtual environment. The REST API (`/api/sessions`, `/api/sessions/{id}/messages`, `/api/sessions/{id}/topics`, `/api/sessions/{id}/next-topic`, `/api/users/{id}/progress`) already exists and is the sole state store — the agent is a pure consumer of it.

## Goals / Non-Goals

**Goals:**
- Implement a functional LiveKit Agents SDK worker in `agent.py`
- STT (Whisper) → GPT-4o → TTS (OpenAI) voice round-trip per user turn
- Load session context + prior transcript at room join; inject into GPT-4o system prompt
- Route first turn to structured-learning or scene-advice flow based on `session.mode`
- Persist each user transcription and agent response to the messages API
- Fire topic-complete + user-progress API calls when a curriculum topic is covered
- Survive missing `OPENAI_API_KEY` with a logged warning rather than a crash

**Non-Goals:**
- Web frontend or LiveKit JS SDK changes
- Image/photo analysis (not in voice pipeline scope)
- Agent-side message storage (REST API is the store; agent writes, never reads back mid-session)
- Multi-user rooms

## Decisions

### 1. Separate Docker service vs shared backend CMD

**Decision**: Add an `agent` service to `docker-compose.yml` that reuses the backend image with a different command: `uv run python agent.py dev`.

**Rationale**: One process per container is idiomatic Docker. Sharing the image avoids a second Dockerfile. The agent and FastAPI share nothing at runtime beyond env vars — there's no in-process coupling needed.

**Trade-off**: Two containers from the same image means the image is built once but instantiated twice, so memory usage is doubled versus a `CMD` switch in one container. For dev this is acceptable; for production a single image re-use is still more efficient than a second Dockerfile.

**Alternative considered**: Run both uvicorn and the agent in one container via a supervisor process (e.g., `supervisord`). Rejected: complicates the image, hides process failures, and violates the single-responsibility principle for containers.

---

### 2. Session context loading via HTTP at room join

**Decision**: At `entrypoint` start, the agent calls `GET /api/sessions/{id}` and `GET /api/sessions/{id}/messages` over HTTP using `httpx.AsyncClient` to load session metadata and prior transcript before the first user turn.

**Rationale**: The agent runs in asyncio (LiveKit Agents uses async throughout), so `httpx.AsyncClient` is the correct non-blocking choice. The FastAPI backend is the single source of truth for session state; the agent should not maintain its own state store.

**Session ID resolution**: The LiveKit room name is `livekit_room_name` from the `sessions` table. When the agent joins a room, the room name is available from `JobContext.room.name`. The agent calls `GET /api/sessions?livekit_room_name={name}` (or derives the session ID from the room name per the naming convention used at session creation) to resolve the session.

```
Room join sequence:

  LiveKit Server ──► agent entrypoint(ctx: JobContext)
                          │
                          ├─ ctx.connect(auto_subscribe=AUDIO_ONLY)
                          │
                          ├─ GET /api/sessions?livekit_room_name={ctx.room.name}
                          │       └─► session: {id, user_id, user_level, equipment_type, mode}
                          │
                          ├─ GET /api/sessions/{id}/messages
                          │       └─► prior_messages: [{role, content}, ...]
                          │
                          ├─ GET /api/sessions/{id}/next-topic  (if mode=structured_learning)
                          │       └─► next_topic: {slug, title, teaching_points, ...}
                          │
                          └─ build ChatContext → start VoiceAssistant
```

---

### 3. System prompt construction

**Decision**: The system prompt is assembled at session start from four components and set as the initial `llm.ChatMessage(role="system", ...)` in the `ChatContext`:

1. **Persona**: mode-dependent — "You are a patient, encouraging photography tutor..." (structured learning) or "You are an on-location photography advisor..." (scene advice)
2. **User context**: level + equipment type
3. **Current topic** (structured learning only): topic title, description, and `teaching_points` from `curriculum.TOPICS`
4. **Prior transcript**: each prior message injected as `role=user`/`role=assistant` turns in the `ChatContext`

**Rationale**: Injecting history into the context (rather than summarising it) gives GPT-4o the full conversation and enables "on session reopen, reference prior conversation" without any summarisation pipeline. At typical session lengths (<50 turns) this stays well within the GPT-4o context window.

---

### 4. Intent detection and assessment flow

**Decision**: Intent is determined at room join (not mid-conversation) by reading `session.mode` and `session.user_level` from the API response. No LLM inference is used to detect intent.

- `structured_learning` + `user_level` already set → load `next-topic`, introduce it in the first agent turn
- `structured_learning` + `user_level` is empty/null → run assessment: agent asks 2–3 questions, then calls `PATCH /api/sessions/{id}` (or a future assessment endpoint) to store the result
- `scene_advice` → agent's first turn prompts the user to describe their scene

**Rationale**: Rule-based intent detection is deterministic, testable, and has zero latency compared to an LLM-based classifier. The mode is an explicit session-creation choice, not something that needs to be inferred.

---

### 5. Topic-coverage detection

**Decision**: In structured-learning mode, the agent marks the current topic as covered after the agent has produced its first substantive response about the topic (i.e., after the first `assistant` turn that follows the topic introduction). This fires `POST /api/sessions/{id}/topics/{slug}` and `PUT /api/users/{id}/progress/{slug}`.

**Rationale**: The agent controls the conversation flow; it knows which topic it is teaching. A time-or-turn threshold is simpler and more reliable than LLM self-assessment of "did I cover this topic?". MVP heuristic: fire after the first full assistant turn in structured-learning mode.

**Simplification**: For the first implementation, mark the topic covered when the session ends (`on_disconnected` callback) rather than mid-session. This avoids premature marking during early turns.

---

### 6. Graceful degradation without OPENAI_API_KEY

**Decision**: At startup, check for `OPENAI_API_KEY`. If absent, log a warning and enter a wait loop (agent stays connected but does not process audio). Do not crash or exit.

**Rationale**: The acceptance criteria explicitly requires the agent to connect without crashing when the key is missing. This lets the agent service run in CI/dev environments without OpenAI credentials.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| Prior transcript grows large (many sessions), exceeding GPT-4o context | Cap injected history at last 50 messages; oldest are truncated |
| Session ID not resolvable from room name (naming mismatch) | Use `GET /api/sessions?livekit_room_name=...` and handle 404 gracefully with a logged error |
| Agent fires topic-complete too early (first turn heuristic) | Acceptable for MVP; a more sophisticated turn-count threshold can be added later |
| LiveKit Agents SDK API changes between versions | Pin SDK version in `pyproject.toml`; check release notes before upgrading |
| TTS latency adds perceived delay | Use streaming TTS (OpenAI TTS supports chunked streaming); LiveKit Agents handles this natively |

## Migration Plan

1. `docker compose build && docker compose up` — new `agent` service starts automatically
2. Rollback: remove `agent` service from `docker-compose.yml`; no DB changes required

## Open Questions

- Should assessment results be written to `sessions.user_level` via `PATCH /api/sessions/{id}` or via a dedicated assessment endpoint? — **Assumption**: `PATCH /api/sessions/{id}` with `{user_level, equipment_type}` fields; if that route doesn't exist, add it as part of this change.
- Should the agent listen for a "skip topic" voice command to advance to the next topic mid-session? — **Out of scope for MVP.**
