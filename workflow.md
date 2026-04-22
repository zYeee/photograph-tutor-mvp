# Development Workflow

---

## AI Tools Used

| Tool | Model | Role |
|------|-------|------|
| Claude Code (CLI) | Claude Sonnet 4.6 | Primary Model |
| Claude Code (CLI) | Claude Opus 4.7 | Secondary Model, for complex planing and debugging |

---

## Workflow: How Claude Code Was Used

### 1. Project Planning with OpenSpec (`/opsx:propose`)

Before writing any code, each feature was designed using the **OpenSpec** harness built into
Claude Code. Running `/opsx:propose` with a feature description triggers a structured planning
workflow that produces three artifacts:

- **`proposal.md`** — the why: problem statement, scope, and list of capabilities
- **`design.md`** — the how: technical decisions, sequence diagrams, risks and trade-offs
- **`specs/*.md`** — testable requirements in WHEN/THEN scenario format

sample structure: [react-frontend](https://github.com/zYeee/photograph-tutor-mvp/tree/main/openspec/changes/react-frontend)


### 2. Implementation with `/opsx:apply`

Once artifacts were approved, `/opsx:apply` parsed the `tasks.md` checklist and walked through
each task sequentially — reading relevant source files, writing or editing code, and checking
off tasks as they completed. This kept implementation scoped to what the spec required and
avoided over-engineering.

the finished tasks can be archived manually: [archived](https://github.com/zYeee/photograph-tutor-mvp/tree/main/openspec/changes/archive)

### 3. Iterative Debugging in Conversation

Bugs were fixed by describing the symptom directly in the Claude Code chat. Claude would:
1. Read the relevant files
2. Identify the root cause
3. Make a targeted edit

Examples from this project:
- **Blank page crash**: `useDataChannel` hook used outside `<LiveKitRoom>` context; Claude
  refactored it into a `DataChannelReceiver` component rendered inside the LiveKit tree
- **Duplicate agent dispatch**: agent joining rooms twice on session creation; fixed by
  scoping the dispatch call correctly
- **Transcript flicker**: streaming previews and polled messages overlapping; fixed with
  a deduplication filter in `Transcript.tsx`
- **Topic Status**: the topic status in study journey are not managed correctly

