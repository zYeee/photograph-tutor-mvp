## 1. Root Monorepo Setup

- [x] 1.1 Create `.gitignore` covering Python (`__pycache__`, `.venv`, `*.pyc`, `db/local.db`), Node (`node_modules`, `dist`), and env files (`.env`)
- [x] 1.2 Create `.env.example` with all required variables: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `OPENAI_API_KEY`, `DATABASE_URL`, `VITE_BACKEND_URL`
- [x] 1.3 Create root `Makefile` with `up`, `down`, `logs`, and `build` targets delegating to `docker compose`
- [x] 1.4 Create `CLAUDE.md` documenting directory layout, service ports, env variable reference, and common dev commands

## 2. Backend Scaffold

- [x] 2.1 Create `/backend/pyproject.toml` with `uv` project config and dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]`, `aiosqlite`, `pydantic-settings`, `livekit-agents`
- [x] 2.2 Run `uv lock` inside `/backend` to generate `uv.lock` and commit it
- [x] 2.3 Create `/backend/app/__init__.py` and `/backend/app/main.py` with FastAPI app, lifespan hook for DB init, and `GET /health` endpoint returning `{"status": "ok"}`
- [x] 2.4 Create `/backend/app/settings.py` using `pydantic-settings` to load and validate all env variables on startup
- [x] 2.5 Create `/backend/app/database.py` with async SQLAlchemy engine pointed at `DATABASE_URL` (defaulting to `sqlite+aiosqlite:///./db/local.db`) and `create_all` on startup
- [x] 2.6 Create `/backend/app/api/token.py` with `GET /api/token?room=<name>` endpoint that generates a LiveKit access token and returns it as JSON
- [x] 2.7 Create `/backend/agent.py` stub that connects to LiveKit server, logs a warning if `OPENAI_API_KEY` is absent, and does not crash
- [x] 2.8 Create `/backend/Dockerfile` using `ghcr.io/astral-sh/uv` base, copying `pyproject.toml` + `uv.lock`, running `uv sync --frozen`, and starting `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

## 3. Frontend Scaffold

- [x] 3.1 Scaffold `/frontend` with `npm create vite@latest . -- --template react-ts`
- [x] 3.2 Install LiveKit dependencies: `npm install livekit-client @livekit/components-react`
- [x] 3.3 Create `/frontend/vite.config.ts` with proxy rule: `/api` → `http://backend:8000` and `server.host: '0.0.0.0'`
- [x] 3.4 Create `/frontend/src/components/RoomJoin.tsx` with a room name input, "Join" button, token fetch from `/api/token`, and error display
- [x] 3.5 Wire `RoomJoin` into `/frontend/src/App.tsx` as the default view
- [x] 3.6 Create `/frontend/Dockerfile` using `node:20-alpine`, installing deps with `npm ci`, and starting `npm run dev` (Vite on port 5173)

## 4. Docker Compose Infrastructure

- [x] 4.1 Create `/livekit.yaml` dev config with `port: 7880`, `rtc.port_range_start: 50000`, `rtc.port_range_end: 60000`, and `keys:` map with dev key/secret (matching `.env.example`); set `development: true` to disable token verification
- [x] 4.2 Create `docker-compose.yml` with `livekit` service using `livekit/livekit-server:latest`, mounting `livekit.yaml`, exposing ports 7880 and 7881/udp, with a health check on `http://localhost:7880`
- [x] 4.3 Add `backend` service to `docker-compose.yml`: build from `./backend`, `depends_on: livekit: condition: service_healthy`, volume mount `./backend:/app`, named volume `db-data:/app/db`, env from `.env`
- [x] 4.4 Add `frontend` service to `docker-compose.yml`: build from `./frontend`, `depends_on: [backend]`, volume mounts `./frontend:/app` and anonymous `node_modules` volume, expose port 5173
- [x] 4.5 Add `volumes: db-data:` top-level volume declaration to `docker-compose.yml`
- [x] 4.6 Add `networks: default:` shared network so all services resolve each other by service name

## 5. Verification

- [x] 5.1 Run `docker compose up` from scratch and confirm all four services reach a running state
- [x] 5.2 Verify `GET http://localhost:8000/health` returns `{"status": "ok"}`
- [x] 5.3 Verify `http://localhost:5173` loads the React app in a browser
- [x] 5.4 Verify `GET http://localhost:8000/api/token?room=test` returns a LiveKit token JSON
- [x] 5.5 Verify SQLite `local.db` persists after `docker compose down && docker compose up`
- [x] 5.6 Edit a `.py` file and confirm uvicorn reloads; edit a `.tsx` file and confirm Vite HMR triggers
