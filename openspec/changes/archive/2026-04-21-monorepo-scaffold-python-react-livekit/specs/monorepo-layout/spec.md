## ADDED Requirements

### Requirement: Root directory structure
The repository SHALL follow a monorepo layout with `/backend`, `/frontend`, and infrastructure files at the root.

#### Scenario: Developer clones the repo
- **WHEN** a developer clones the repository and lists the root directory
- **THEN** they SHALL see: `backend/`, `frontend/`, `docker-compose.yml`, `.env.example`, `Makefile`, `CLAUDE.md`, and `.gitignore`

### Requirement: Environment variable template
The repository SHALL include a `.env.example` file that documents every required environment variable with placeholder values and inline comments.

#### Scenario: Developer sets up environment
- **WHEN** a developer copies `.env.example` to `.env`
- **THEN** the application SHALL start without errors (given valid API key values are filled in)

#### Scenario: Missing required variable
- **WHEN** the backend starts without a required environment variable (e.g., `LIVEKIT_URL`)
- **THEN** the application SHALL exit with a descriptive error message identifying the missing variable

### Requirement: Root Makefile shortcuts
The repository SHALL include a `Makefile` at the root providing at minimum: `up`, `down`, `logs`, and `build` targets that delegate to `docker compose`.

#### Scenario: Developer starts the stack
- **WHEN** a developer runs `make up`
- **THEN** `docker compose up -d` SHALL be executed and all services SHALL start

#### Scenario: Developer stops the stack
- **WHEN** a developer runs `make down`
- **THEN** `docker compose down` SHALL be executed and all containers SHALL stop

### Requirement: CLAUDE.md project documentation
The repository SHALL include a `CLAUDE.md` file documenting the monorepo structure, service ports, environment variable reference, and common dev commands.

#### Scenario: New contributor reads CLAUDE.md
- **WHEN** a developer reads `CLAUDE.md`
- **THEN** they SHALL find: directory layout, how to start the stack, service URLs, and how to add a new environment variable
