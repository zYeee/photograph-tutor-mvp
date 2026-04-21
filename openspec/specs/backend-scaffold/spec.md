## Requirements

### Requirement: FastAPI application skeleton
The backend SHALL be a FastAPI application located in `/backend/` with a health check endpoint, a settings module using `pydantic-settings`, and application startup/shutdown lifecycle hooks.

#### Scenario: Health check endpoint returns 200
- **WHEN** a client sends `GET /health`
- **THEN** the server SHALL respond with HTTP 200 and body `{"status": "ok"}`

#### Scenario: Settings loaded from environment
- **WHEN** the application starts
- **THEN** all settings SHALL be loaded from environment variables (or `.env` file) via `pydantic-settings`, and missing required variables SHALL raise a startup error

### Requirement: SQLite database with SQLAlchemy
The backend SHALL use SQLAlchemy (async) with an aiosqlite driver, storing data in `backend/db/local.db`. The database SHALL be created automatically on first startup.

#### Scenario: Database file created on startup
- **WHEN** the backend starts for the first time with no existing `local.db`
- **THEN** `local.db` SHALL be created at the configured path and all tables SHALL be initialized

#### Scenario: Database persists across container restarts
- **WHEN** the backend container is restarted
- **THEN** the `local.db` file SHALL retain all previously written rows (because it is volume-mounted)

### Requirement: LiveKit Agents SDK integration point
The backend SHALL include a stub LiveKit agent entrypoint (`backend/agent.py`) that connects to the configured LiveKit server URL. If no OpenAI API key is present, it SHALL log a warning and skip AI initialization rather than crashing.

#### Scenario: Agent starts with valid config
- **WHEN** `python agent.py` is run with `LIVEKIT_URL`, `LIVEKIT_API_KEY`, and `LIVEKIT_API_SECRET` set
- **THEN** the agent SHALL connect to the LiveKit server and log "Agent connected"

#### Scenario: Agent starts without OpenAI key
- **WHEN** `python agent.py` is run without `OPENAI_API_KEY`
- **THEN** the agent SHALL log a warning "OPENAI_API_KEY not set — AI features disabled" and SHALL still connect to LiveKit

### Requirement: Python dependency management with uv
The backend SHALL use `uv` for dependency management with a `pyproject.toml` and a committed `uv.lock` file.

#### Scenario: Installing dependencies
- **WHEN** a developer runs `uv sync` in the `/backend` directory
- **THEN** all dependencies SHALL be installed into a `.venv` virtual environment

#### Scenario: Docker build installs deps
- **WHEN** the backend Docker image is built
- **THEN** `uv sync --frozen` SHALL be used to install dependencies from the lockfile without modification
