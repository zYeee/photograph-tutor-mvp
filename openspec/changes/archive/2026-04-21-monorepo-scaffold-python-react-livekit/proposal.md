## Why

The project currently lacks a structured monorepo scaffold, making it difficult to develop, test, and deploy the Python backend and React frontend together. Establishing a clean monorepo layout with Docker Compose integration (including LiveKit and SQLite) creates a reproducible local development environment and a clear foundation for all future feature work.

## What Changes

- Introduce a `/backend` directory with a Python/FastAPI application skeleton using `uv` for dependency management
- Introduce a `/frontend` directory with a React (Vite) application skeleton using the LiveKit JS SDK
- Replace PostgreSQL with SQLite for local development simplicity (file-based, zero-config)
- Add a `docker-compose.yml` that orchestrates: backend, frontend (dev server), LiveKit server, and LiveKit egress
- Add a `.env.example` with all required environment variables
- Add a root `Makefile` / `justfile` for common dev commands (`up`, `down`, `logs`, `migrate`)
- Add `CLAUDE.md` documenting the monorepo structure and dev workflow

## Capabilities

### New Capabilities

- `monorepo-layout`: Directory structure, root-level tooling, and conventions for the Python/React monorepo
- `backend-scaffold`: FastAPI app skeleton with LiveKit Agents SDK integration, SQLite via SQLAlchemy, health endpoint
- `frontend-scaffold`: React + Vite app skeleton with LiveKit JS SDK wired up, basic room join flow
- `docker-compose-infra`: `docker-compose.yml` defining backend, frontend, livekit-server, and livekit-egress services with networking and volume mounts

### Modified Capabilities

<!-- none — this is a greenfield scaffold -->

## Impact

- **Code**: Creates `/backend`, `/frontend`, `docker-compose.yml`, `.env.example`, `Makefile` at repo root
- **Dependencies**: Python (`fastapi`, `uvicorn`, `livekit-agents`, `sqlalchemy`, `alembic`), Node (`react`, `vite`, `@livekit/components-react`, `livekit-client`)
- **Infrastructure**: LiveKit server runs locally via Docker; SQLite replaces PostgreSQL for zero-setup local dev
- **Developer workflow**: `docker compose up` starts the full stack; no manual service installation required
