## Context

The photography tutor already exposes two endpoints suitable for this feature:
- `GET /api/topics` — returns all topics as a parent/child tree (roots are category nodes; children carry a `level` field of `beginner`, `intermediate`, or `advanced`)
- `GET /api/users/{user_id}/progress` — returns all `UserTopicProgress` rows with `slug`, `title`, and `status` (`not_started`, `in_progress`, `completed`)

The sidebar (`Sidebar.tsx`) is the natural home for the trigger button. The modal pattern already exists in the codebase (`NewSessionModal.tsx`), providing a consistent UX precedent.

## Goals / Non-Goals

**Goals:**
- Add a "Study Journey" button to the sidebar header alongside the existing "New session" button
- Open a modal that groups all leaf topics under three labelled sections: Beginner, Intermediate, Advanced
- Mark topics where `status === 'completed'` with a ✅ emoji prefix
- Use React Query to fetch and cache both endpoints; loading and error states handled gracefully

**Non-Goals:**
- Clicking a topic does not navigate or start a session
- No filtering, sorting, or search within the modal
- No backend changes — existing APIs are sufficient
- No per-topic progress percentage or proficiency display (only completed/not-completed distinction)

## Decisions

### Flatten by `level`, not by parent category
The `/api/topics` tree is organised by photographic *category* (Exposure, Composition, etc.), not by level. For the Study Journey view the user cares about progression tiers. Topics will be filtered by `level` field on the child nodes and grouped into three sections regardless of their parent category.

*Alternative considered*: Show categories as sub-headers within each level. Rejected for MVP — adds visual complexity without aiding orientation.

### Single modal component (`StudyJourneyModal`)
Follows the existing `NewSessionModal` pattern: a backdrop overlay + centred card, closed via an × button or backdrop click. Keeps the pattern consistent with zero new dependencies.

### Two parallel React Query fetches
`getTopics()` and `getUserProgress(userId)` are independent and can be fetched concurrently. Progress slugs are stored in a `Set<string>` for O(1) lookup when rendering each topic row.

### Level ordering: Beginner → Intermediate → Advanced
Fixed display order matches the natural learning progression and mirrors the `user_level` enum used elsewhere in the app.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| `/api/topics` returns root categories that have no `level` field | Filter to only nodes where `level` is defined (leaf topics); skip roots |
| Progress data may be stale if another session just completed a topic | React Query default stale-time is 0; data refetches on modal open via `enabled` flag tied to `isOpen` |
| Modal content overflows on small screens | Cap modal height with `overflow-y: auto` and `max-height: 80vh` |
