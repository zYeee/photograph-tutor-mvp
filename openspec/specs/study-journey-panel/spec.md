## ADDED Requirements

### Requirement: Study Journey button in sidebar
The sidebar header SHALL contain a "Study Journey" button that opens the Study Journey modal when clicked. The button SHALL be visible at all times, independent of whether a session is active.

#### Scenario: Button is present in sidebar
- **WHEN** the user loads the application
- **THEN** a "Study Journey" button SHALL be visible in the sidebar header

#### Scenario: Button opens modal
- **WHEN** the user clicks the "Study Journey" button
- **THEN** the Study Journey modal SHALL appear as an overlay

---

### Requirement: Study Journey modal displays all topics grouped by level
The Study Journey modal SHALL display all curriculum leaf topics organised into three sections labelled "Beginner", "Intermediate", and "Advanced", in that order. Root category topics (those without a `level` field) SHALL NOT be shown.

#### Scenario: Three level sections rendered
- **WHEN** the modal opens and topics have loaded
- **THEN** the modal SHALL display exactly three sections: Beginner, Intermediate, and Advanced

#### Scenario: Each section lists its topics
- **WHEN** the modal opens and topics have loaded
- **THEN** each topic whose `level` matches the section label SHALL appear under that section

#### Scenario: Loading state shown while fetching
- **WHEN** the modal opens and topic data has not yet loaded
- **THEN** the modal SHALL display a loading indicator

#### Scenario: Error state shown on fetch failure
- **WHEN** the topic or progress API call fails
- **THEN** the modal SHALL display an error message instead of the topic list

---

### Requirement: Completed topics marked with green check emoji
A topic SHALL be marked with a ✅ emoji prefix when the current user's progress record for that topic has `status === 'completed'`. Topics with any other status or no progress record SHALL appear without the emoji.

#### Scenario: Completed topic shows check
- **WHEN** the user has a progress record with `status = 'completed'` for a topic
- **THEN** that topic's label in the modal SHALL be prefixed with ✅

#### Scenario: Non-completed topic shows no check
- **WHEN** the user has no progress record, or a record with `status = 'not_started'` or `'in_progress'`, for a topic
- **THEN** that topic's label in the modal SHALL NOT show ✅

---

### Requirement: Modal can be dismissed
The Study Journey modal SHALL be dismissible by clicking a close button (×) inside the modal or by clicking the backdrop overlay outside the modal card.

#### Scenario: Close button dismisses modal
- **WHEN** the user clicks the × button inside the modal
- **THEN** the modal SHALL close

#### Scenario: Backdrop click dismisses modal
- **WHEN** the user clicks outside the modal card on the backdrop overlay
- **THEN** the modal SHALL close
