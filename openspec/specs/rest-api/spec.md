## ADDED Requirements

### Requirement: Create session
The backend SHALL expose `POST /api/sessions` accepting `user_id`, `livekit_room_name`, `mode`, `user_level`, and `equipment_type`. It SHALL insert a row into `sessions` and return the created session as JSON.

#### Scenario: Session created successfully
- **WHEN** a valid POST body is sent to `/api/sessions`
- **THEN** the response SHALL be HTTP 201 with the new session row as JSON including `id`, `started_at`, and `last_topic_id: null`

#### Scenario: Duplicate room name rejected
- **WHEN** a POST is made with a `livekit_room_name` that already exists
- **THEN** the response SHALL be HTTP 409

#### Scenario: Invalid mode rejected
- **WHEN** a POST is made with a `mode` value outside the allowed set
- **THEN** the response SHALL be HTTP 422

---

### Requirement: List sessions for user
The backend SHALL expose `GET /api/sessions?user_id=<id>` returning all sessions for that user ordered by `started_at DESC`, with a `last_topic` field containing the topic title from a LEFT JOIN on `topics`.

#### Scenario: Sessions returned with last topic
- **WHEN** `GET /api/sessions?user_id=1` is called and a session has `last_topic_id` set
- **THEN** the response SHALL include `last_topic: "<topic title>"` for that session

#### Scenario: Active session has null ended_at
- **WHEN** a session has not been closed
- **THEN** its `ended_at` field in the response SHALL be `null`

---

### Requirement: Get single session
The backend SHALL expose `GET /api/sessions/{id}` returning the session row with `last_topic` title included.

#### Scenario: Existing session returned
- **WHEN** `GET /api/sessions/1` is called for a session that exists
- **THEN** the response SHALL be HTTP 200 with the full session object

#### Scenario: Missing session returns 404
- **WHEN** `GET /api/sessions/9999` is called for a session that does not exist
- **THEN** the response SHALL be HTTP 404

---

### Requirement: Close session
The backend SHALL expose `PATCH /api/sessions/{id}/close` that sets `ended_at` to the current timestamp and optionally stores a `summary` from the request body.

#### Scenario: Session closed
- **WHEN** `PATCH /api/sessions/1/close` is called
- **THEN** `sessions.ended_at` SHALL be set to the current timestamp and the response SHALL be HTTP 200

---

### Requirement: Append message
The backend SHALL expose `POST /api/sessions/{id}/messages` accepting `role`, `content`, and optional `token_count`, inserting a row into `messages`.

#### Scenario: Message appended
- **WHEN** a valid POST body is sent to `/api/sessions/1/messages`
- **THEN** the response SHALL be HTTP 201 with the new message row including `id` and `created_at`

#### Scenario: Invalid role rejected
- **WHEN** a POST is made with a `role` outside ('user', 'assistant', 'system')
- **THEN** the response SHALL be HTTP 422

---

### Requirement: List messages for session
The backend SHALL expose `GET /api/sessions/{id}/messages` returning all messages for that session ordered by `created_at ASC`.

#### Scenario: Full transcript returned in order
- **WHEN** `GET /api/sessions/1/messages` is called
- **THEN** the response SHALL be a JSON array of message objects ordered by `created_at` ascending

#### Scenario: Empty session returns empty array
- **WHEN** a session has no messages
- **THEN** the response SHALL be HTTP 200 with an empty array

---

### Requirement: List topics (curriculum tree)
The backend SHALL expose `GET /api/topics` returning all topics from the seeded curriculum, structured as a nested list: root categories with their child topics.

#### Scenario: Curriculum tree returned
- **WHEN** `GET /api/topics` is called
- **THEN** the response SHALL include all root categories, each with a `children` array of leaf topics sorted by `sort_order`

---

### Requirement: Mark topic complete in session
The backend SHALL expose `POST /api/sessions/{id}/topics/{slug}` that inserts a row into `session_topics` (if not already present) and updates `sessions.last_topic_id` to the matching topic's `id`, both in a single transaction.

#### Scenario: Topic marked complete
- **WHEN** `POST /api/sessions/1/topics/aperture` is called
- **THEN** a row is inserted into `session_topics` and `sessions.last_topic_id` is updated; response SHALL be HTTP 201

#### Scenario: Idempotent on repeated call
- **WHEN** the same topic is posted for the same session twice
- **THEN** the second call SHALL return HTTP 200 (already complete) without inserting a duplicate

#### Scenario: Unknown slug returns 404
- **WHEN** a slug that does not exist in `topics` is posted
- **THEN** the response SHALL be HTTP 404

---

### Requirement: List completed topics for session
The backend SHALL expose `GET /api/sessions/{id}/topics` returning all `session_topics` rows for that session joined with topic details, ordered by `completed_at ASC`.

#### Scenario: Completed topics returned in order
- **WHEN** `GET /api/sessions/1/topics` is called after two topics have been marked complete
- **THEN** the response SHALL list both topics ordered by `completed_at` ascending

---

### Requirement: Get user progress
The backend SHALL expose `GET /api/users/{id}/progress` returning all `user_topic_progress` rows for that user joined with topic slug and title.

#### Scenario: Progress returned
- **WHEN** `GET /api/users/1/progress` is called
- **THEN** the response SHALL include one entry per topic the user has interacted with, including `status` and `proficiency`

#### Scenario: User with no progress returns empty array
- **WHEN** a user has no rows in `user_topic_progress`
- **THEN** the response SHALL be HTTP 200 with an empty array

---

### Requirement: Upsert user topic progress
The backend SHALL expose `PUT /api/users/{id}/progress/{slug}` accepting `status` and optional `proficiency`, performing an insert-or-update on `user_topic_progress`.

#### Scenario: Progress created on first interaction
- **WHEN** `PUT /api/users/1/progress/aperture` is called for a (user, topic) pair that has no existing row
- **THEN** a new row is inserted and the response SHALL be HTTP 200 with the upserted row

#### Scenario: Progress updated on subsequent call
- **WHEN** `PUT /api/users/1/progress/aperture` is called for a pair that already has a row
- **THEN** the existing row's `status`, `proficiency`, and `last_visited_at` are updated
