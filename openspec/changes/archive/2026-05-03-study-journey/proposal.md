## Why

Users have no visibility into the curriculum structure or their learning progress across sessions. A Study Journey panel gives learners a birds-eye view of all topics grouped by difficulty level, with instant feedback on what they have already covered.

## What Changes

- Add a **Study Journey** button to the sidebar header
- Clicking the button opens a modal popup that displays all topics organised into three difficulty sections (Beginner, Intermediate, Advanced)
- Topics the user has previously completed are marked with a ✅ green check emoji
- The modal fetches data from two existing endpoints: `GET /api/topics` (topic tree) and `GET /api/users/{user_id}/progress` (completion status)
- No backend changes required — all necessary data is already exposed

## Capabilities

### New Capabilities

- `study-journey-panel`: Frontend modal component that lists the full curriculum by level and marks completed topics for the current user

### Modified Capabilities

<!-- None — existing API endpoints are sufficient; no spec-level behaviour changes -->

## Impact

- `frontend/src/components/Sidebar.tsx` — add Study Journey button
- New files: `StudyJourneyModal.tsx`, `StudyJourneyModal.css`
- `frontend/src/api.ts` — add `getTopics` and `getUserProgress` fetch helpers
- No backend or database changes required
