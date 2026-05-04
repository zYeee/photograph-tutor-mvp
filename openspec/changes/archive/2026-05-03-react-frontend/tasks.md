## 1. Dependencies & Project Setup

- [x] 1.1 Add `@livekit/components-react`, `@livekit/client`, `@tanstack/react-query` to `frontend/package.json` and run `npm install`
- [x] 1.2 Wrap the React app root in `<QueryClientProvider>` in `frontend/src/main.tsx`
- [x] 1.3 Create `frontend/src/api.ts` with typed fetch helpers for all backend endpoints (`getSessions`, `createSession`, `getMessages`, `closeSession`, `getToken`)
- [x] 1.4 Add `VITE_BACKEND_URL` to `frontend/.env.example` (or verify it exists) and read it in `api.ts`

## 2. App Shell & Layout

- [x] 2.1 Create `frontend/src/App.tsx` two-column grid layout (sidebar 280 px, main fills remainder; collapses to single column below 768 px)
- [x] 2.2 Add CSS Module or global styles for the two-column grid and responsive breakpoint
- [x] 2.3 Hold `activeSessionId` in top-level state; pass setter to sidebar and reader to session pane

## 3. Session Sidebar

- [x] 3.1 Create `frontend/src/components/Sidebar.tsx` that fetches sessions via React Query (`useQuery`) using `getSessions(userId)`
- [x] 3.2 Render each session row with mode badge, equipment_type, and `last_topic` (fallback "New session")
- [x] 3.3 Highlight the active session row; clicking any row calls `setActiveSessionId`
- [x] 3.4 Show loading skeleton while fetching and an error message on failure
- [x] 3.5 Show empty-state message when the session list is empty

## 4. New Session Modal

- [x] 4.1 Create `frontend/src/components/NewSessionModal.tsx` with controlled selects for mode, user_level, and equipment_type
- [x] 4.2 On submit call `createSession(...)` and handle the pending/error states inline
- [x] 4.3 On success: close modal, invalidate the sessions query cache, and set `activeSessionId` to the new session
- [x] 4.4 Close modal on Cancel click or Escape key press without creating a session
- [x] 4.5 Add "New session" button to the sidebar that opens the modal

## 5. Active Session View — Layout & Header

- [x] 5.1 Create `frontend/src/components/SessionView.tsx` that renders nothing (or a prompt) when no session is active
- [x] 5.2 Fetch the active session object and display mode and `last_topic` in the top bar (fallback "No topic yet")
- [x] 5.3 Add mic/connect button area to the top bar (wired up in step 6)

## 6. Voice Room Integration

- [x] 6.1 Add a `useToken` hook in `SessionView.tsx` that calls `getToken(room)` when the user clicks Connect
- [x] 6.2 Render `<LiveKitRoom serverUrl token connect={shouldConnect}>` and `<RoomAudioRenderer>` inside `SessionView`
- [x] 6.3 Show "Listening..." indicator when connected and the agent is not speaking
- [x] 6.4 Detect agent speaking state via `useRemoteParticipants` / track subscription and show "Tutor speaking..." indicator
- [x] 6.5 On Disconnect: call `room.disconnect()`, then `closeSession(sessionId)`, then invalidate the sessions query cache
- [x] 6.6 Handle token fetch error: display error message, keep button in Connect state

## 7. Transcript View

- [x] 7.1 Create `frontend/src/components/Transcript.tsx` that fetches messages with `useQuery` on mount
- [x] 7.2 Render user messages as right-aligned bubbles and assistant messages as left-aligned bubbles
- [x] 7.3 Auto-scroll the transcript container to the bottom whenever a new message is appended
- [x] 7.4 Start a 2-second `refetchInterval` in `useQuery` while the voice room is connected; stop it on disconnect
- [x] 7.5 Show empty-state prompt ("Connect and start speaking") when there are no messages

## 8. Responsive & Polish

- [x] 8.1 Verify sidebar collapses correctly on a 375 px viewport (sidebar becomes full-width or hidden with a toggle)
- [x] 8.2 Check for and fix any React console errors/warnings on initial load
- [x] 8.3 Verify "New session" → connect → speak → disconnect flow end-to-end in the browser
- [x] 8.4 Verify sidebar `last_topic` updates after disconnect triggers a session list refetch
