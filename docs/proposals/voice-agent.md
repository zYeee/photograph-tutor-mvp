voice-agent LiveKit Agents SDK worker: Whisper STT, GPT-4o LLM, OpenAI TTS, memory injection, intent detection for structured-learning vs scene-advice modes.

Supplementary details to feed after initial artifacts:
Entry point: backend/agent.py (already exists as stub).
Agent runs as a separate LiveKit worker process, NOT inside FastAPI.
Add to docker-compose as a 4th service (or keep in backend container
with a separate CMD — your call, note tradeoff).

Session lifecycle:
1. Agent joins LiveKit room when user connects.
2. Agent calls GET /api/sessions/{id} to load session context.
3. Agent calls GET /api/sessions/{id}/messages to load transcript.
4. Transcript injected into GPT-4o system prompt as prior conversation.

Intent detection (first turn or explicit trigger):
- If session.mode == 'structured_learning':
    * If no user_level set: run assessment flow (ask level + equipment questions).
    * Otherwise: call GET /api/sessions/{id}/next-topic and introduce it.
- If session.mode == 'scene_advice':
    * Prompt user to describe the scene.
    * Give advice covering lighting, composition, exposure, equipment-specific tips.

After each agent turn:
- POST /api/sessions/{id}/messages with role='user' (transcription)
- POST /api/sessions/{id}/messages with role='assistant' (agent text)
- If a topic was covered: POST /api/sessions/{id}/topics/{slug}
- PUT /api/users/{id}/progress/{slug} with updated status

System prompt must include:
- User level, equipment type
- Full prior transcript
- Current topic being taught (structured learning only)
- Mode-specific persona: "patient photography tutor" vs "on-location advisor"

No crash if OPENAI_API_KEY is missing — log warning and wait.

Acceptance criteria:
- Agent connects to LiveKit room without crashing (with or without OPENAI_API_KEY)
- Speaking triggers STT → LLM → TTS round-trip
- After session, GET /api/sessions/{id}/messages shows full transcript
- On session reopen, agent's first response references prior conversation
- POST /api/sessions/{id}/topics/aperture fired automatically when agent covers aperture
- Scene advice turn covers lighting + composition + equipment-specific tip

