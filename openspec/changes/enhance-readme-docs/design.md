## Context

The project already has a CLAUDE.md with developer-facing notes, but the public README.md lacks onboarding content. New contributors face three friction points: (1) unclear minimum host requirements, (2) no guided `.env` setup walkthrough, and (3) no visual reference for the overall architecture or data model. This is a documentation-only change — no code, API, or schema is modified.

## Goals / Non-Goals

**Goals:**
- Add system requirements (Docker ≥ 24, Docker Compose ≥ 2.20)
- Add a step-by-step environment setup guide covering all `.env` variables
- Add a Mermaid architecture diagram showing all five services and their connections
- Add a Mermaid ER diagram covering the six critical tables (users, sessions, messages, topics, session_topics, user_topic_progress)

**Non-Goals:**
- Changing CLAUDE.md, Makefile, or any code file
- Full API reference documentation
- Deployment / production infrastructure documentation
- Documenting every table column (only critical tables, abbreviated)

## Decisions

**Decision 1: Use Mermaid for all diagrams**
GitHub renders Mermaid natively in Markdown. No external image assets, no stale screenshots. Mermaid `graph TD` for the architecture diagram and `erDiagram` for the schema.

*Alternative considered*: ASCII art — rejected because it cannot express relationship types clearly.

**Decision 2: Architecture diagram scope — five service nodes**
Include: Browser, Frontend (Vite), Backend (FastAPI), Agent (LiveKit Agents SDK), LiveKit Server. Show the SQLite/DB as a data store attached to Backend.
Omit provider-level cloud boxes (OpenAI, etc.) to keep the diagram focused on locally-running infrastructure.

**Decision 3: ER diagram scope — six critical tables only**
Include: `users`, `sessions`, `messages`, `topics`, `session_topics`, `user_topic_progress`.
Omit: `photo_submissions`, `photo_feedback` — these are secondary features not required for core session flows.

**Decision 4: README section order**
1. System Requirements
2. Quick Start (already present — keep, de-duplicate with Setup section)
3. Environment Setup (step-by-step `.env` guide)
4. Architecture Overview (Mermaid diagram)
5. Database Schema (Mermaid ER diagram)

Existing content (Service URLs, Common Commands, env var table) is preserved unchanged.

## Risks / Trade-offs

- **Mermaid version drift** → GitHub renders Mermaid server-side; syntax that works today should remain stable. Mitigation: use only stable `graph TD` and `erDiagram` syntax.
- **README length** → Adding four new sections increases README length. Mitigation: keep each section concise; use collapsible `<details>` blocks if sections grow too large in future.
- **Diagram accuracy drift** → Diagrams can become stale as the codebase evolves. Mitigation: diagrams show component relationships (stable), not implementation details (volatile). Schema diagram is manually updated if models.py changes.
