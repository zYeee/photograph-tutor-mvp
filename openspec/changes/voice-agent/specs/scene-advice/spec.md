## ADDED Requirements

### Requirement: Scene advice opening prompt
When `session.mode = "scene_advice"`, the agent's opening message SHALL invite the user to describe the scene or subject they want to photograph, and mention that it will give advice on lighting, composition, and exposure.

#### Scenario: Scene advice opening message
- **WHEN** the agent joins a room with `mode = "scene_advice"`
- **THEN** the agent SHALL produce an opening message such as: "Hi! I'm your on-location photography advisor. Tell me about the scene or subject you're planning to shoot, and I'll give you advice on lighting, composition, and exposure for your setup."

### Requirement: Scene advice response covers four areas
When the user describes a scene, the agent's response SHALL address all four of: lighting conditions and recommendations, composition suggestions, exposure settings, and equipment-specific tips based on `session.equipment_type`.

#### Scenario: Full scene advice turn
- **WHEN** a user says "I want to photograph a street market at midday with my mirrorless camera"
- **THEN** the agent's response SHALL include at least one concrete recommendation on: (1) how to handle harsh midday lighting, (2) a composition approach for a busy market scene, (3) exposure settings appropriate for bright daylight, (4) a tip specific to mirrorless cameras

#### Scenario: Equipment-specific tip included
- **WHEN** `session.equipment_type = "smartphone"`
- **THEN** the agent's scene advice SHALL include a tip specific to smartphone photography (e.g., using portrait mode, gridlines, or HDR)
- **WHEN** `session.equipment_type = "dslr"`
- **THEN** the tip SHALL be relevant to DSLR-specific features or workflow

### Requirement: Scene advice is conversational across turns
After the initial scene description, the agent SHALL remain in scene-advice mode and accept follow-up questions or scene refinements across multiple turns.

#### Scenario: Follow-up question handled
- **WHEN** after receiving scene advice the user asks "What about if the clouds come in?"
- **THEN** the agent SHALL respond with advice adapted to overcast conditions
- **THEN** it SHALL NOT restart the opening prompt or ask the user to describe the scene again
