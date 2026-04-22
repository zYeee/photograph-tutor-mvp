## 1. API helpers

- [x] 1.1 Add `Topic` and `UserProgress` TypeScript interfaces to `frontend/src/api.ts`
- [x] 1.2 Add `getTopics()` fetch helper calling `GET /api/topics` to `frontend/src/api.ts`
- [x] 1.3 Add `getUserProgress(userId)` fetch helper calling `GET /api/users/{userId}/progress` to `frontend/src/api.ts`

## 2. StudyJourneyModal component

- [x] 2.1 Create `frontend/src/components/StudyJourneyModal.tsx` with modal scaffold (backdrop + card + × close button)
- [x] 2.2 Fetch topics and user progress in parallel using `useQuery` inside the modal
- [x] 2.3 Render loading state while either query is pending
- [x] 2.4 Render error state if either query fails
- [x] 2.5 Flatten topic tree to leaf nodes and group by `level` (beginner / intermediate / advanced)
- [x] 2.6 Build a `Set<string>` of completed topic slugs from progress data (`status === 'completed'`)
- [x] 2.7 Render three labelled sections (Beginner, Intermediate, Advanced) with topic rows
- [x] 2.8 Prefix completed topic titles with ✅ emoji
- [x] 2.9 Close modal on backdrop click

## 3. Styling

- [x] 3.1 Create `frontend/src/components/StudyJourneyModal.css` with backdrop overlay, modal card, section headers, topic rows, and scrollable content area (`max-height: 80vh`, `overflow-y: auto`)

## 4. Sidebar integration

- [x] 4.1 Add `studyJourneyOpen` state to `Sidebar.tsx`
- [x] 4.2 Add "Study Journey" button to sidebar header in `Sidebar.tsx`
- [x] 4.3 Render `<StudyJourneyModal>` conditionally when `studyJourneyOpen` is true, passing `userId` and `onClose`

## 5. Verification

- [x] 5.1 Open the app, click "Study Journey", confirm all three level sections appear with topics
- [x] 5.2 Confirm topics completed in a prior session show ✅ prefix
- [x] 5.3 Confirm modal closes on × button click and on backdrop click
- [x] 5.4 Confirm no console errors and loading/error states display correctly
