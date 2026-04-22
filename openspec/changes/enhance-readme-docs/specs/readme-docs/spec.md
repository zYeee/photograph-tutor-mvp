## ADDED Requirements

### Requirement: System requirements section
README.md SHALL contain a "System Requirements" section listing the minimum host dependencies needed to run the project locally: Docker ≥ 24.0 and Docker Compose ≥ 2.20 (plugin form, `docker compose`).

#### Scenario: Reader can verify prerequisites before setup
- **WHEN** a developer reads the README before cloning the repo
- **THEN** they SHALL find a clearly labelled section listing Docker and Docker Compose version minimums

#### Scenario: Correct compose command shown
- **WHEN** the system requirements section references Docker Compose
- **THEN** it SHALL use the plugin syntax `docker compose` (not the legacy `docker-compose` binary)

---

### Requirement: Environment setup guide
README.md SHALL contain a step-by-step "Environment Setup" section that walks the reader through creating `.env` from `.env.example` and setting each required variable. Each variable SHALL include its name, whether it is required or optional, its default value (if any), and a one-line description of what it controls.

#### Scenario: Required variables are clearly marked
- **WHEN** a developer reads the environment setup section
- **THEN** variables with no safe default (e.g. `OPENAI_API_KEY`) SHALL be marked as required, and variables with working defaults SHALL be marked as optional

#### Scenario: Copy command is shown
- **WHEN** a developer follows the setup guide
- **THEN** the first step SHALL show the shell command `cp .env.example .env`

#### Scenario: All five variables are documented
- **WHEN** the section is rendered
- **THEN** it SHALL document exactly these variables: `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, `OPENAI_API_KEY`, `DATABASE_URL`, `VITE_BACKEND_URL`

---

### Requirement: Architecture overview with Mermaid diagram
README.md SHALL contain an "Architecture Overview" section with a Mermaid `graph TD` diagram showing the five runtime components (Browser, Frontend, Backend, Agent, LiveKit Server) and SQLite as a data store, with labelled directed edges representing the primary communication path between each pair.

#### Scenario: Diagram is rendered by GitHub
- **WHEN** the README is viewed on GitHub
- **THEN** the Mermaid fenced code block SHALL render as a visual diagram (not raw text)

#### Scenario: All five services are nodes
- **WHEN** the diagram is inspected
- **THEN** it SHALL contain nodes for: Browser, Frontend (Vite/React), Backend (FastAPI), Agent (LiveKit Agents SDK), and LiveKit Server

#### Scenario: Communication relationships are labelled
- **WHEN** the diagram is inspected
- **THEN** edges SHALL carry labels identifying the protocol or purpose (e.g. "HTTP REST", "WebSocket / RTC", "LiveKit SDK", "LiveKit Agents SDK")

---

### Requirement: Database schema with Mermaid ER diagram
README.md SHALL contain a "Database Schema" section with a Mermaid `erDiagram` diagram covering the six critical tables: `users`, `sessions`, `messages`, `topics`, `session_topics`, and `user_topic_progress`. Each table SHALL show its primary key and the most important non-nullable columns. Foreign-key relationships SHALL be shown with crow's-foot notation.

#### Scenario: Six tables are present in diagram
- **WHEN** the ER diagram is inspected
- **THEN** it SHALL contain exactly these six entities: USERS, SESSIONS, MESSAGES, TOPICS, SESSION_TOPICS, USER_TOPIC_PROGRESS

#### Scenario: Relationships use crow's-foot notation
- **WHEN** the Mermaid erDiagram source is inspected
- **THEN** relationship lines SHALL use standard ERD cardinality markers (e.g. `||--o{`)

#### Scenario: Diagram is rendered by GitHub
- **WHEN** the README is viewed on GitHub
- **THEN** the Mermaid fenced code block SHALL render as a visual ER diagram
