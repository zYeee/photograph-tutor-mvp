## Why

The MVP backend and LiveKit voice agent are in place, but there is no browser UI — users cannot start a session, talk to the tutor, or review past transcripts. This change delivers the complete React SPA that ties every backend endpoint and the LiveKit voice room into a usable product.

## What Changes

- Add a full React + Vite frontend under `frontend/src/`
- Two-column layout: session sidebar (left) + active session view (right)
- Session sidebar lists all sessions for the hardcoded MVP user (user_id=1), ordered newest-first, with mode badge, equipment type, and last-topic label
- "New session" modal lets the user pick mode (Structured Learning / Scene Advice), user_level, and equipment_type, then calls `POST /api/sessions`
- Active session view shows the current topic, a Connect/Disconnect voice button, a real-time transcript (message bubbles), and speaking/listening indicators
- LiveKit token fetched from `GET /api/token?room=<room_name>`; audio handled by `@livekit/components-react`
- Transcript polled or streamed via LiveKit data channel; session closed via `PATCH /api/sessions/{id}/close` on disconnect
- Responsive layout that works on mobile viewports

## Capabilities

### New Capabilities

- `session-list`: Display and navigate the list of past sessions for the current user, with metadata (mode, equipment, last topic)
- `session-create`: Modal form to create a new session (mode, user_level, equipment_type) and navigate to it
- `voice-room`: Connect/disconnect from the LiveKit room, stream agent audio to browser speakers, and show speaking/listening indicators
- `transcript-view`: Real-time display of conversation turns (user + assistant bubbles), loaded from REST and updated after each voice turn

### Modified Capabilities

*(none — no existing specs require delta changes)*

## Impact

- `frontend/src/` — new React component tree, hooks, and pages
- `frontend/package.json` — adds `@livekit/components-react`, `@livekit/client` (if not already present)
- Backend API surface used: `GET /api/sessions`, `POST /api/sessions`, `GET /api/sessions/{id}/messages`, `PATCH /api/sessions/{id}/close`, `GET /api/token`
- No backend schema changes required
