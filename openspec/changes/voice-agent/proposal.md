## Why

`backend/agent.py` exists only as a stub: it logs a startup message and exits. Without a real LiveKit Agents worker, the app has no voice capability — users can't speak to the tutor, no STT/LLM/TTS pipeline runs, and the structured-learning and scene-advice modes are completely inert. Wiring up the agent is the core missing piece that makes the product functional.

## What Changes

- Implement `backend/agent.py` as a full LiveKit Agents SDK worker: Whisper STT → GPT-4o → OpenAI TTS round-trip
- Session lifecycle: on room join, agent loads session context and message history from the REST API and injects the prior transcript into the system prompt
- Intent routing on first turn (or explicit trigger): structured-learning mode either runs the assessment flow (if no `user_level` set) or introduces the next curriculum topic; scene-advice mode prompts the user to describe the scene and responds with lighting, composition, exposure, and equipment-specific guidance
- Transcript persistence after every agent turn: user transcription and assistant text POSTed to `/api/sessions/{id}/messages`
- Topic-coverage tracking: when the agent covers a curriculum topic it fires `POST /api/sessions/{id}/topics/{slug}` and `PUT /api/users/{id}/progress/{slug}`
- Add an `agent` service to `docker-compose.yml` (separate container from the FastAPI backend, sharing the same image but with a different `CMD`) so the worker starts with `docker compose up`
- Graceful degradation: if `OPENAI_API_KEY` is absent, agent logs a warning and waits rather than crashing

## Capabilities

### New Capabilities

- `voice-session`: LiveKit Agents SDK worker setup — room join, STT/LLM/TTS pipeline, graceful degradation without API key
- `intent-routing`: First-turn detection of `session.mode` and `user_level`; branches to assessment flow or topic introduction (structured learning) vs scene-description prompt (scene advice)
- `transcript-persistence`: Loads prior messages at session start and injects them into the system prompt; POSTs new user and assistant turns to the messages API after each exchange
- `scene-advice`: Scene advice mode conversational flow — prompts for scene description, responds covering lighting, composition, exposure, and equipment-specific tips in a single coherent turn
- `topic-coverage-tracking`: Detects which curriculum topic was covered in a turn and fires the topic-complete and user-progress REST calls

### Modified Capabilities

- `docker-compose-infra`: New `agent` service added (separate CMD within the backend image, depends on `livekit` and `backend`)

## Impact

- **`backend/agent.py`**: complete rewrite from stub to production worker
- **`docker-compose.yml`**: new `agent` service entry
- **`backend/pyproject.toml`**: ensure `livekit-agents`, `openai`, `httpx` are declared
- **No REST API changes** — agent is a pure consumer of existing endpoints
- **`.env.example`**: confirm `OPENAI_API_KEY` is documented (already present)
