## MODIFIED Requirements

### Requirement: Curriculum content file structure
`backend/app/curriculum.py` SHALL export a `TOPICS` list where each entry is a dict with the following keys: `slug` (str, matches a row in the `topics` DB table), `title` (str), `level` (str: one of `beginner`, `intermediate`, `advanced`), `sort_order` (int, unique within a level), `description` (str), `teaching_points` (list[str], what the agent SHALL cover in this topic), `assessment_questions` (list[str], questions the agent SHALL use to gauge understanding).

#### Scenario: All required keys present
- **WHEN** `curriculum.TOPICS` is imported
- **THEN** every entry SHALL contain the keys: `slug`, `title`, `level`, `sort_order`, `description`, `teaching_points`, `assessment_questions`
- **THEN** `teaching_points` and `assessment_questions` SHALL each be a non-empty list

#### Scenario: Sort order is unique within a level
- **WHEN** filtering `TOPICS` by a given level
- **THEN** no two entries SHALL share the same `sort_order` value within that level

## ADDED Requirements

### Requirement: Minimum topic coverage per level
`curriculum.py` SHALL contain at least 20 topics in total, distributed across the three levels as follows: Beginner 6–8 topics covering exposure triangle, basic composition, and focus fundamentals; Intermediate 8–10 topics covering depth of field, lighting patterns, and advanced composition; Advanced 8–10 topics covering hyperfocal distance, color grading, and creative techniques.

#### Scenario: Minimum count per level
- **WHEN** `curriculum.TOPICS` is imported and filtered by level
- **THEN** `beginner` level SHALL have at least 6 entries
- **THEN** `intermediate` level SHALL have at least 8 entries
- **THEN** `advanced` level SHALL have at least 8 entries

#### Scenario: Teaching points are agent-actionable
- **WHEN** the agent reads `teaching_points` for any topic
- **THEN** each point SHALL be a sentence describing a concrete concept or skill the agent should explain or demonstrate

#### Scenario: Assessment questions are evaluative
- **WHEN** the agent reads `assessment_questions` for any topic
- **THEN** each question SHALL be phrased so that the learner's answer reveals whether they understood the topic

### Requirement: Curriculum slugs are consistent with the DB topics table
Every `slug` value in `curriculum.TOPICS` SHALL exist as a row in the `topics` DB table. The DB table remains the FK reference source; `curriculum.py` is the content source. The `topics` table SHALL NOT have `teaching_points` or `assessment_questions` columns.

#### Scenario: GET /api/topics has no curriculum-only fields
- **WHEN** `GET /api/topics` is called
- **THEN** each topic object in the response SHALL NOT contain `teaching_points` or `assessment_questions` keys
- **THEN** the response shape SHALL remain unchanged from its current form

#### Scenario: Every curriculum slug resolves in DB
- **WHEN** the backend starts
- **THEN** every slug in `curriculum.TOPICS` SHALL have a matching row in the `topics` table (verified by startup assertion or test)
