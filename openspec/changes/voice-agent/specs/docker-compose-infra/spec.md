## MODIFIED Requirements

### Requirement: docker-compose.yml with all services
The repository SHALL include a `docker-compose.yml` at the root that defines five services: `livekit`, `backend`, `frontend`, `agent`. All services SHALL be on a shared Docker network.

#### Scenario: Full stack starts with one command
- **WHEN** a developer runs `docker compose up`
- **THEN** all services (livekit, backend, frontend, agent) SHALL start within 60 seconds
- **THEN** the agent service SHALL connect to the LiveKit server and log a ready message

#### Scenario: Services communicate by name
- **WHEN** the backend makes a connection to LiveKit
- **THEN** it SHALL resolve `livekit` as the hostname (via Docker internal DNS)
- **WHEN** the agent makes HTTP calls to the REST API
- **THEN** it SHALL resolve `backend` as the hostname

## ADDED Requirements

### Requirement: Agent service in docker-compose
The `agent` service SHALL use the same Docker image as the `backend` service (built from `./backend/Dockerfile`) with a different `command` (`uv run python agent.py dev`). It SHALL mount the backend source directory for hot-reload, depend on both `livekit` (healthy) and `backend` (started), and receive the same `env_file` and `LIVEKIT_URL` environment variable.

#### Scenario: Agent service starts after livekit and backend
- **WHEN** `docker compose up` is run
- **THEN** the `agent` container SHALL not start until `livekit` passes its health check and `backend` has started
- **THEN** the agent SHALL log a message indicating it connected to LiveKit

#### Scenario: Agent service shares backend image
- **WHEN** `docker compose build` is run
- **THEN** only one Docker image SHALL be built for both `backend` and `agent`
- **THEN** running `docker compose up` SHALL use that shared image for both services
