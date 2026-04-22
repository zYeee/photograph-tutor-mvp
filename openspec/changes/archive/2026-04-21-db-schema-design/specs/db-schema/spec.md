## ADDED Requirements

### Requirement: Users table
The database SHALL contain a `users` table with `id`, `email` (UNIQUE NOT NULL), `display_name` (NOT NULL), `created_at`, and `updated_at` columns. No authentication credentials SHALL be stored in this table.

#### Scenario: User record created on first join
- **WHEN** a new user accesses the tutor for the first time
- **THEN** a row is inserted into `users` with a unique email and current timestamp in `created_at`

#### Scenario: Duplicate email rejected
- **WHEN** an insert is attempted with an email that already exists in `users`
- **THEN** the database SHALL reject the insert with a UNIQUE constraint violation

---

### Requirement: Sessions table
The database SHALL contain a `sessions` table linking each voice session to a user and a LiveKit room. Each session SHALL record its interaction `mode` ('structured_learning' or 'scene_advice'), `user_level` ('beginner', 'intermediate', 'advanced'), `equipment_type` ('smartphone', 'mirrorless', 'dslr', 'point-and-shoot', 'film'), nullable `last_topic_id` (FK → topics), `started_at`, nullable `ended_at`, and nullable `summary`.

#### Scenario: Active session has null ended_at
- **WHEN** a session is created at voice-join time
- **THEN** `ended_at` is NULL and `started_at` is set to the current timestamp

#### Scenario: Session closed on voice-leave
- **WHEN** the LiveKit room closes or the user disconnects
- **THEN** `ended_at` is updated to the current timestamp

#### Scenario: Room name is unique per session
- **WHEN** two concurrent sessions attempt to use the same LiveKit room name
- **THEN** the database SHALL reject the second insert with a UNIQUE constraint violation on `livekit_room_name`

#### Scenario: Invalid mode rejected
- **WHEN** a session is inserted with a mode value outside ('structured_learning', 'scene_advice')
- **THEN** the database SHALL reject the insert with a CHECK constraint violation

#### Scenario: Invalid user_level rejected
- **WHEN** a session is inserted with a user_level outside ('beginner', 'intermediate', 'advanced')
- **THEN** the database SHALL reject the insert with a CHECK constraint violation

#### Scenario: Invalid equipment_type rejected
- **WHEN** a session is inserted with an equipment_type outside ('smartphone', 'mirrorless', 'dslr', 'point-and-shoot', 'film')
- **THEN** the database SHALL reject the insert with a CHECK constraint violation

#### Scenario: last_topic_id updated during session
- **WHEN** the agent advances to a new topic during a session
- **THEN** `sessions.last_topic_id` is updated to the new topic's id

---

### Requirement: Session topics table
The database SHALL contain a `session_topics` table recording which topics were completed within a specific session, with a `UNIQUE(session_id, topic_id)` constraint and a `completed_at` timestamp.

#### Scenario: Topic completion recorded once per session
- **WHEN** the agent marks a topic as covered in a session
- **THEN** a row is inserted into `session_topics`; a second insert for the same session/topic pair SHALL be rejected by the UNIQUE constraint

#### Scenario: Completed topics retrievable in order
- **WHEN** the frontend requests completed topics for a session
- **THEN** all `session_topics` rows for that session SHALL be retrievable ordered by `completed_at` ascending

---

### Requirement: Messages table
The database SHALL contain a `messages` table storing each conversation turn with `session_id`, `role` ('user', 'assistant', or 'system'), `content`, optional `token_count`, and `created_at`.

#### Scenario: Messages loaded in chronological order
- **WHEN** the agent loads conversation history for a session
- **THEN** messages SHALL be retrievable ordered by `created_at` ascending

#### Scenario: Invalid role rejected
- **WHEN** a message is inserted with a role outside ('user', 'assistant', 'system')
- **THEN** the database SHALL reject the insert with a CHECK constraint violation

---

### Requirement: Topics reference table
The database SHALL contain a `topics` table as a seeded reference table with `slug` (UNIQUE), `title`, `description`, nullable `parent_id` (self-reference for category → topic hierarchy), `difficulty` (1–5), and `sort_order`.

#### Scenario: Root category has no parent
- **WHEN** a root category topic is queried
- **THEN** its `parent_id` SHALL be NULL

#### Scenario: Sub-topic references parent category
- **WHEN** a sub-topic is queried
- **THEN** its `parent_id` SHALL reference a valid `topics.id` with `parent_id IS NULL`

#### Scenario: Difficulty out of range rejected
- **WHEN** a topic is inserted with a difficulty outside 1–5
- **THEN** the database SHALL reject the insert with a CHECK constraint violation

---

### Requirement: User topic progress table
The database SHALL contain a `user_topic_progress` table with a UNIQUE constraint on `(user_id, topic_id)` tracking each learner's `status` ('not_started', 'in_progress', 'completed'), nullable `proficiency` (0.0–1.0), and `last_visited_at`.

#### Scenario: Progress upserted on topic interaction
- **WHEN** a user discusses a topic during a session
- **THEN** the corresponding `user_topic_progress` row is inserted (if new) or updated with the latest `status` and `last_visited_at`

#### Scenario: Duplicate user-topic pair rejected
- **WHEN** an insert is attempted for a (user_id, topic_id) pair that already exists
- **THEN** the database SHALL reject the insert with a UNIQUE constraint violation (use upsert instead)

#### Scenario: Proficiency out of range rejected
- **WHEN** a progress update sets `proficiency` outside 0.0–1.0
- **THEN** the database SHALL reject the update with a CHECK constraint violation

---

### Requirement: Photo submissions table
The database SHALL contain a `photo_submissions` table linking a submitted photo to a `user_id`, `session_id`, a `storage_path` (NOT NULL), optional `caption`, and `submitted_at`.

#### Scenario: Submission recorded on photo upload
- **WHEN** a user submits a photo during a session
- **THEN** a row is inserted into `photo_submissions` with the resolved `storage_path` and current `submitted_at`

#### Scenario: Photos queryable by session
- **WHEN** the agent loads photos for the current session
- **THEN** all submissions with the matching `session_id` SHALL be retrievable

---

### Requirement: Photo feedback table
The database SHALL contain a `photo_feedback` table with a UNIQUE constraint on `submission_id` (one feedback record per photo), optional score columns (`composition_score`, `exposure_score`, `focus_score`, `lighting_score`, `overall_score` — each REAL 0.0–1.0), optional `notes`, and optional `message_id` linking to the conversation turn that produced the feedback.

#### Scenario: Feedback stored after AI critique
- **WHEN** the AI agent completes a photo critique
- **THEN** a `photo_feedback` row is inserted with score columns and `notes` populated

#### Scenario: Second feedback for same photo rejected
- **WHEN** an insert is attempted for a `submission_id` that already has a feedback record
- **THEN** the database SHALL reject the insert with a UNIQUE constraint violation (use update instead)

#### Scenario: Score out of range rejected
- **WHEN** any score column is set outside 0.0–1.0
- **THEN** the database SHALL reject the write with a CHECK constraint violation

---

### Requirement: Foreign key enforcement
The database SHALL enforce all foreign key constraints. SQLite foreign key enforcement SHALL be enabled at connection time (`PRAGMA foreign_keys = ON`).

#### Scenario: Orphaned message rejected
- **WHEN** a message is inserted with a `session_id` that does not exist in `sessions`
- **THEN** the database SHALL reject the insert with a FOREIGN KEY constraint violation

#### Scenario: Cascade delete not applied
- **WHEN** a user or session is deleted
- **THEN** the database SHALL reject the delete if dependent rows exist (no CASCADE — deletions must be explicit)

---

### Requirement: WAL journal mode
The database SHALL be opened with `PRAGMA journal_mode=WAL` to support concurrent read access from multiple backend processes.

#### Scenario: WAL mode active after connection
- **WHEN** the backend initialises a new SQLite connection
- **THEN** executing `PRAGMA journal_mode` SHALL return `'wal'`
