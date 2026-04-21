## Context

The photograph-tutor-mvp is a real-time voice AI photography tutor. Before any feature work can begin, the project needs a reproducible monorepo structure that developers can clone and run with a single command. The current repo has no backend, no frontend, and no infrastructure configuration. This design covers the scaffold only — no AI/voice logic is implemented here.

The project context specifies PostgreSQL, but for a local development scaffold we choose SQLite to eliminate an additional dependency and simplify first-run experience. PostgreSQL can be layered back in when production deployment is scoped.

## Goals / Non-Goals

**Goals:**
- Define a `/backend` (FastAPI + SQLite via SQLAlchemy) and `/frontend` (React + Vite) directory structure
- Provide a `docker-compose.yml` that starts all services with `docker compose up`
- Include a LiveKit server container for local voice session testing
- Provide `.env.example` documenting every required environment variable
- Enable hot-reload for both backend and frontend in development

**Non-Goals:**
- AI/voice pipeline implementation (OpenAI Whisper, GPT-4o, TTS) — out of scope for scaffold
- Production deployment, CI/CD, or cloud infrastructure
- Authentication or user management
- Database migrations beyond initial schema bootstrap

## Decisions

### D1: SQLite over PostgreSQL for local dev

**Decision**: Use SQLite (via SQLAlchemy + aiosqlite) for the scaffold.

**Rationale**: SQLite requires no Docker container, no credentials, and no volume management. The file lives at `backend/db/local.db`. Switching to PostgreSQL later requires only a connection string change; SQLAlchemy abstracts the difference.

**Alternative considered**: Keep PostgreSQL (matches production). Rejected because it adds container startup ordering complexity and slows first-run setup for new contributors.

### D2: Vite over CRA for React frontend

**Decision**: Use Vite as the React build tool.

**Rationale**: Vite is the current ecosystem standard, provides fast HMR, and has first-class Docker support via `--host 0.0.0.0`.

**Alternative considered**: Create React App — deprecated and significantly slower.

### D3: LiveKit server via official Docker image

**Decision**: Use `livekit/livekit-server` in docker-compose with a dev config that disables auth for local use.

**Rationale**: Allows real LiveKit room and track behavior locally without a cloud account. The LiveKit Agents SDK connects to this local server via `ws://livekit:7880`.

**Alternative considered**: Use LiveKit Cloud for local dev. Rejected because it requires network access and credentials on every `docker compose up`.

### D4: uv for Python dependency management

**Decision**: Use `uv` instead of `pip`/`poetry` for the backend.

**Rationale**: `uv` is dramatically faster, produces a lockfile (`uv.lock`), and the official Docker image (`ghcr.io/astral-sh/uv`) makes container builds clean. `uv sync` installs dependencies in the Dockerfile.

**Alternative considered**: `poetry` — heavier and slower; `pip` + `requirements.txt` — no lockfile.

### D5: Sequence of service startup

```
docker compose up
    │
    ├── livekit-server (port 7880/7881)
    │       └── health check → healthy
    │
    ├── backend (port 8000)
    │       depends_on: livekit-server (healthy)
    │       └── uvicorn, hot-reload via volume mount
    │
    └── frontend (port 5173)
            depends_on: backend (started)
            └── vite dev server, hot-reload via volume mount
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| SQLite concurrency limits if multiple backend workers | Scaffold uses single worker; document the PostgreSQL migration path in CLAUDE.md |
| LiveKit dev image version drift | Pin `livekit/livekit-server` to a specific tag in docker-compose |
| `node_modules` inside the container conflicts with host mount | Use an anonymous volume for `node_modules` to shadow the bind mount |
| LiveKit Agents SDK requires a running OpenAI key even in scaffold | Provide a stub agent entrypoint that logs "no API key" gracefully; document in .env.example |

## Migration Plan

1. Run `docker compose up` — services start in dependency order
2. Backend auto-creates SQLite tables on first startup via SQLAlchemy `create_all`
3. To switch to PostgreSQL: replace `DATABASE_URL` in `.env`, add postgres service to docker-compose, remove SQLite volume

## Open Questions

- Should the frontend scaffold include a basic LiveKit room join UI, or just the SDK installed? (Current proposal: minimal join UI to prove the integration works end-to-end)
- Pin LiveKit server version to match the Agents SDK version being used?
