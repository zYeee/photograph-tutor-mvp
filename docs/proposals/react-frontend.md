react-frontend React SPA: session sidebar with last-topic label, create/open session, LiveKit voice room, real-time transcript display, two interaction modes.

Supplementary details to feed after initial artifacts:
Layout: two-column. Left: session sidebar. Right: active session view.

Sidebar:
- List of sessions from GET /api/sessions?user_id=<id>, ordered by started_at DESC.
- Each row shows: mode badge, equipment_type, last_topic (or "New session").
- "New session" button opens a modal: pick mode (Structured Learning / Scene Advice),
  user_level, equipment_type → calls POST /api/sessions.

Active session view:
- Top bar: session mode, current topic (from last_topic), mic button.
- Transcript area: scrolling list of message bubbles (user/assistant),
  populated from GET /api/sessions/{id}/messages and updated in real-time
  as the agent speaks (subscribe to LiveKit data channel or poll).
- Voice UI: single Connect/Disconnect button.
  When connected: show animated waveform or "Listening..." indicator.
  When agent speaks: show "Tutor speaking..." indicator.
- On disconnect: session auto-closes via PATCH /api/sessions/{id}/close.

No login screen for MVP — hardcode user_id=1 (or read from localStorage).
Use @livekit/components-react for the room/audio; build custom transcript UI.
LiveKit token from GET /api/token?room=<livekit_room_name>.

Acceptance criteria:
- Sidebar lists sessions; clicking one opens it and loads transcript
- "New session" creates a session and navigates to it
- Connecting to voice room plays agent audio through browser speakers
- Transcript updates after each voice turn (user speech + agent response)
- After marking a topic, sidebar last_topic label updates on next visit
- Works on mobile viewport (responsive layout)
- No console errors on initial load

