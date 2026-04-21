## ADDED Requirements

### Requirement: Mode detection at session start
The agent SHALL read `session.mode` from the session API response immediately after joining a room. Based on the mode, it SHALL route to one of two conversational flows: `structured_learning` or `scene_advice`. This routing SHALL happen before the first user turn (the agent initiates the opening message).

#### Scenario: Structured learning mode detected
- **WHEN** the loaded session has `mode = "structured_learning"` and `user_level` is set
- **THEN** the agent SHALL call `GET /api/sessions/{id}/next-topic` to get the recommended topic
- **THEN** the agent SHALL open the session by introducing that topic by name and asking if the user is ready to begin

#### Scenario: Structured learning mode, no user_level
- **WHEN** the loaded session has `mode = "structured_learning"` and `user_level` is null or empty
- **THEN** the agent SHALL begin the assessment flow: ask the user their current photography experience level and what equipment they use
- **THEN** after receiving the user's answers, the agent SHALL determine the appropriate level (beginner/intermediate/advanced), call `PATCH /api/sessions/{id}` to store `user_level` and `equipment_type`, then proceed to introduce the first topic for that level

#### Scenario: Scene advice mode detected
- **WHEN** the loaded session has `mode = "scene_advice"`
- **THEN** the agent SHALL open by prompting the user to describe the scene or subject they want to photograph

### Requirement: Assessment flow produces a stored user_level
When the agent runs the assessment flow, the determined `user_level` and `equipment_type` SHALL be persisted to the session record so that future sessions can skip the assessment.

#### Scenario: Assessment updates session record
- **WHEN** the agent completes the 2–3 assessment questions and determines `user_level = "intermediate"`
- **THEN** `PATCH /api/sessions/{id}` SHALL be called with `{"user_level": "intermediate", "equipment_type": "<user's answer>"}`
- **THEN** a subsequent `GET /api/sessions/{id}` SHALL return the updated `user_level`

### Requirement: System prompt is mode-specific
The GPT-4o system prompt SHALL include a persona section that differs by mode.

#### Scenario: Structured learning persona
- **WHEN** `session.mode = "structured_learning"`
- **THEN** the system prompt SHALL include a persona such as: "You are a patient, encouraging photography tutor. Guide the student through the current topic step by step, using clear explanations and practical examples."
- **THEN** the prompt SHALL also include the user's level, equipment type, and the current topic's `teaching_points`

#### Scenario: Scene advice persona
- **WHEN** `session.mode = "scene_advice"`
- **THEN** the system prompt SHALL include a persona such as: "You are an expert on-location photography advisor. When the user describes a scene, give practical, actionable advice covering lighting, composition, exposure settings, and tips specific to their equipment."
- **THEN** the prompt SHALL include the user's level and equipment type but NOT a specific topic
