## ADDED Requirements

### Requirement: docker-compose.yml with all services
The repository SHALL include a `docker-compose.yml` at the root that defines four services: `backend`, `frontend`, `livekit`, and optionally `livekit-egress`. All services SHALL be on a shared Docker network.

#### Scenario: Full stack starts with one command
- **WHEN** a developer runs `docker compose up`
- **THEN** all four services SHALL start and become healthy within 60 seconds

#### Scenario: Services communicate by name
- **WHEN** the backend makes a connection to LiveKit
- **THEN** it SHALL resolve `livekit` as the hostname (via Docker internal DNS)

### Requirement: Service startup ordering
Services SHALL start in dependency order: `livekit` first, then `backend` (depends_on livekit healthy), then `frontend` (depends_on backend started).

#### Scenario: Backend waits for LiveKit
- **WHEN** `docker compose up` is run on a cold system
- **THEN** the backend container SHALL not start until the livekit container passes its health check

### Requirement: Hot-reload via volume mounts
The `backend` and `frontend` services SHALL mount their source directories into the container so that code changes trigger hot-reload without rebuilding the image.

#### Scenario: Backend code change reloads
- **WHEN** a developer edits a `.py` file in `/backend`
- **THEN** `uvicorn` SHALL detect the change (via `--reload`) and restart within 2 seconds

#### Scenario: Frontend code change reloads
- **WHEN** a developer edits a `.tsx` file in `/frontend/src`
- **THEN** Vite HMR SHALL update the browser without a full page reload

### Requirement: SQLite data persistence
The backend service SHALL mount a named Docker volume for the SQLite database file so that data persists across `docker compose down` / `up` cycles.

#### Scenario: Data survives container restart
- **WHEN** `docker compose down` followed by `docker compose up` is run
- **THEN** rows written to SQLite before the stop SHALL still be present after restart

### Requirement: Service port exposure
Each service SHALL expose a stable port on localhost:
- `livekit`: 7880 (WebSocket/HTTP), 7881 (RTC/UDP)
- `backend`: 8000
- `frontend`: 5173

#### Scenario: Developer accesses services from host
- **WHEN** the stack is running
- **THEN** `http://localhost:8000/health` SHALL return 200 and `http://localhost:5173` SHALL serve the React app

### Requirement: LiveKit dev config
The `livekit` service SHALL start with a dev configuration (`livekit.yaml`) that disables authentication token verification for local development convenience.

#### Scenario: Connect without token validation
- **WHEN** a client connects to the local LiveKit server without a valid JWT
- **THEN** the server SHALL accept the connection (dev mode only)
