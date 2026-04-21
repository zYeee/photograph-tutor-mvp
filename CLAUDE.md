# photograph-tutor-mvp

Real-time voice AI photography tutor — monorepo with Python backend, React frontend, and LiveKit for voice sessions.

## Directory Layout

```
/
├── backend/          # Python FastAPI app (uv, SQLAlchemy, LiveKit Agents SDK)
│   ├── app/          # Application package
│   │   ├── api/      # Route handlers
│   │   ├── main.py   # FastAPI entry point
│   │   ├── settings.py
│   │   └── database.py
│   ├── agent.py      # LiveKit agent entry point
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/         # React + Vite app (LiveKit JS SDK)
│   ├── src/
│   │   ├── components/
│   │   └── App.tsx
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── livekit.yaml      # LiveKit dev server config
├── .env.example      # Copy to .env and fill in values
├── Makefile
└── CLAUDE.md         # This file
```

## Quick Start

```bash
cp .env.example .env
# Edit .env — at minimum set OPENAI_API_KEY for AI features
make up
```

## Service URLs

| Service  | URL                          | Notes                     |
|----------|------------------------------|---------------------------|
| Frontend | http://localhost:5173        | React dev server (Vite)   |
| Backend  | http://localhost:8000        | FastAPI                   |
| Backend health | http://localhost:8000/health | Should return `{"status":"ok"}` |
| LiveKit  | ws://localhost:7880          | WebSocket endpoint        |

## Common Commands

```bash
make up       # Start all services (detached)
make down     # Stop all services
make logs     # Tail logs from all services
make build    # Rebuild Docker images

# Backend only
cd backend && uv sync          # Install Python deps locally
cd backend && uv run uvicorn app.main:app --reload  # Run without Docker

# Frontend only
cd frontend && npm install     # Install Node deps
cd frontend && npm run dev     # Run without Docker
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LIVEKIT_URL` | Yes | `ws://localhost:7880` | LiveKit server WebSocket URL |
| `LIVEKIT_API_KEY` | Yes | `devkey` | LiveKit API key (matches `livekit.yaml`) |
| `LIVEKIT_API_SECRET` | Yes | `devsecret` | LiveKit API secret |
| `OPENAI_API_KEY` | No | — | Required for AI voice features; scaffold runs without it |
| `DATABASE_URL` | Yes | `sqlite+aiosqlite:///./db/local.db` | SQLAlchemy connection string |
| `VITE_BACKEND_URL` | No | `http://localhost:8000` | Backend URL used by browser |

## Adding a New Environment Variable

1. Add it to `.env.example` with a placeholder and comment
2. Add it to `backend/app/settings.py` as a `pydantic-settings` field
3. Document it in the table above

## Switching to PostgreSQL

1. Add a `postgres` service to `docker-compose.yml`
2. Set `DATABASE_URL=postgresql+asyncpg://user:pass@postgres/db` in `.env`
3. Remove the `db-data` SQLite volume from `backend` service
