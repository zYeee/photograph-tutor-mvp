## ADDED Requirements

### Requirement: Open new-session modal
The system SHALL display a "New session" button in the sidebar. Clicking it SHALL open a modal form.

#### Scenario: User opens modal
- **WHEN** the user clicks the "New session" button
- **THEN** a modal opens containing fields for mode, user_level, and equipment_type

### Requirement: Create session via modal form
The modal form SHALL allow the user to select:
- **mode**: `structured_learning` or `scene_advice`
- **user_level**: beginner, intermediate, or advanced
- **equipment_type**: free-text or preset options (e.g., DSLR, mirrorless, smartphone)

On submit the system SHALL call `POST /api/sessions` with the selected values. On success it SHALL close the modal, add the new session to the sidebar, and navigate to the new session in the active pane.

#### Scenario: Successful session creation
- **WHEN** the user fills in all fields and clicks "Create"
- **THEN** `POST /api/sessions` is called with the correct payload
- **THEN** the modal closes
- **THEN** the new session appears at the top of the sidebar list
- **THEN** the active session pane shows the new session

#### Scenario: API error on creation
- **WHEN** `POST /api/sessions` returns an error
- **THEN** the modal shows an inline error message
- **THEN** the modal remains open so the user can retry

#### Scenario: User cancels modal
- **WHEN** the user clicks Cancel or presses Escape
- **THEN** the modal closes without creating a session
