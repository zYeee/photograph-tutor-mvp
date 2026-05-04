## ADDED Requirements

### Requirement: SQLAlchemy async models
The backend SHALL define SQLAlchemy async ORM models in `backend/app/models.py` for all 8 tables defined in the approved schema: `users`, `sessions`, `messages`, `topics`, `session_topics`, `user_topic_progress`, `photo_submissions`, `photo_feedback`. Column names, types, nullability, and constraints SHALL match `openspec/specs/database/schema.md` exactly.

#### Scenario: All tables created on first boot
- **WHEN** the FastAPI app starts for the first time against an empty database
- **THEN** all 8 tables SHALL exist in the SQLite file after startup completes

#### Scenario: Repeated startup does not error
- **WHEN** the app starts against a database that already has all tables
- **THEN** `create_all` SHALL complete without error or data loss

---

### Requirement: Connection pragmas applied on every connection
The backend SHALL apply `PRAGMA journal_mode=WAL` and `PRAGMA foreign_keys=ON` on every new SQLite connection via a SQLAlchemy engine event listener.

#### Scenario: WAL mode active
- **WHEN** a new database connection is established
- **THEN** `PRAGMA journal_mode` SHALL return `'wal'`

#### Scenario: Foreign keys enforced
- **WHEN** a new database connection is established
- **THEN** inserting a row with an invalid FK SHALL raise a constraint error

---

### Requirement: AsyncSession dependency
The backend SHALL expose a `get_db()` FastAPI dependency that yields an `AsyncSession` per request and closes it on completion or error.

#### Scenario: Session provided to route handlers
- **WHEN** a route handler declares `db: AsyncSession = Depends(get_db)`
- **THEN** it SHALL receive a valid open session for the duration of the request

#### Scenario: Session closed after request
- **WHEN** a request completes (success or exception)
- **THEN** the session SHALL be closed and returned to the connection pool

---

### Requirement: Curriculum seed on startup
The backend SHALL seed the `topics` table from the hardcoded curriculum defined in `backend/app/curriculum.py` during the FastAPI lifespan startup hook. The seed SHALL be idempotent — rows with an existing `slug` SHALL be skipped.

#### Scenario: Topics populated after first boot
- **WHEN** the app starts against an empty database
- **THEN** `SELECT COUNT(*) FROM topics` SHALL return the number of topics defined in `curriculum.py`

#### Scenario: Seed is safe on restart
- **WHEN** the app restarts against a database that already contains all topic slugs
- **THEN** no duplicate rows SHALL be inserted and startup SHALL complete without error
