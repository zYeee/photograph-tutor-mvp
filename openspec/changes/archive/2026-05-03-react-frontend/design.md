## Context

The backend exposes a REST API (FastAPI) and a LiveKit voice agent. The frontend directory exists but contains only a Vite scaffold — no real UI. This design delivers the full React SPA using the existing backend surface without changing it.

MVP constraint: no auth. `user_id=1` is hardcoded (or read from `localStorage` for easy override).

## Goals / Non-Goals

**Goals:**
- Two-column layout: session sidebar + active session pane
- CRUD sessions via REST; voice via `@livekit/components-react`
- Real-time transcript updates after each voice turn
- Responsive (works on mobile)
- No console errors on initial load

**Non-Goals:**
- User authentication / multi-user support
- Offline support or PWA
- Backend changes
- Custom WebRTC implementation (use LiveKit SDK)
- Image upload or camera features

## Decisions

### 1. State management: React Query + local component state

**Decision**: Use TanStack Query (React Query) for all REST fetching and cache invalidation. No global state library (no Redux/Zustand).

**Why**: Sessions and messages are server-state. React Query handles loading/error states, background refetch, and cache invalidation with minimal boilerplate. Component-local state covers UI concerns (modal open, active session ID).

**Alternatives considered**:
- Zustand global store — adds complexity for what is essentially server-cache synchronization.
- SWR — similar to React Query but less ergonomic for mutations.

### 2. Transcript updates: polling (not LiveKit data channel)

**Decision**: Poll `GET /api/sessions/{id}/messages` every 2 s while a session is connected, rather than subscribing to the LiveKit data channel.

**Why**: The agent backend does not currently publish transcript events over the data channel. Polling avoids agent-side changes and is reliable enough for an MVP with low concurrency. The 2 s interval is imperceptible to users given typical voice-turn latency.

**Alternatives considered**:
- LiveKit data channel subscription — ideal long-term; deferred until agent emits transcript events.
- WebSocket endpoint on the FastAPI backend — extra backend work outside this change's scope.

### 3. Voice UI: `@livekit/components-react` for room/audio, custom transcript

**Decision**: Use `<LiveKitRoom>` and `<RoomAudioRenderer>` from `@livekit/components-react` to handle WebRTC negotiation and audio playback. Build transcript and indicator UI manually.

**Why**: The SDK components handle all the hard WebRTC plumbing (ICE, codec negotiation, speaker permissions). Custom UI is needed because the SDK's pre-built components don't match our transcript bubble design.

### 4. Sequence: connect → token fetch → room join

```
User clicks "Connect"
  → Frontend: GET /api/token?room=<livekit_room_name>
  → Backend: returns { token: "<jwt>" }
  → Frontend: passes token to <LiveKitRoom serverUrl connect>
  → LiveKit SDK: joins room, agent joins automatically
  → RoomAudioRenderer: streams agent audio to speakers
  → Polling starts: GET /api/sessions/{id}/messages every 2s

User clicks "Disconnect"
  → LiveKit SDK: disconnect()
  → Frontend: PATCH /api/sessions/{id}/close
  → Polling stops
  → Sidebar refetches session list (last_topic updates)
```

### 5. Layout: CSS Grid, no UI framework

**Decision**: Use plain CSS Grid / Flexbox with CSS Modules. No component library (no MUI/Chakra).

**Why**: Keeps the bundle lean. The layout is simple enough that a library adds more overhead than value for MVP.

## Risks / Trade-offs

- **Polling latency** → Users see transcript updates up to 2 s after each turn. Acceptable for MVP; mitigated by snappy voice feedback from audio playback.
- **Token leakage** → LiveKit JWT is fetched client-side with no user auth. Risk is low for local dev; acceptable for MVP. Mitigation: short token TTL (set in backend).
- **Single user hardcode** → `user_id=1` means all browser sessions share state. Acceptable for MVP demo; mitigated by a `localStorage` override hook so testers can vary it.
- **Mobile layout** → Two-column grid collapses to single column below 768 px. Sidebar becomes a slide-in drawer on small screens.

## Migration Plan

1. `npm install` in `frontend/` — adds `@livekit/components-react`, `@livekit/client`, `@tanstack/react-query`
2. Replace Vite scaffold `src/` with new component tree
3. `make up` — Vite dev server serves new UI at `http://localhost:5173`
4. No database migrations or backend deployments needed

## Open Questions

- Should the token endpoint accept an existing `session_id` and derive the room name, or should the frontend pass the `livekit_room_name` directly? (Current plan: frontend passes `room` param derived from session object.)
- Long-term: should transcript events be pushed via LiveKit data channel to eliminate polling?
