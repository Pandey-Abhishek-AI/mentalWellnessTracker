# Task List

> **Project:** Mental Wellness Tracker  
> **Last updated:** 2026-06-13

## Milestone: MVP

### TASK-001: Project scaffold

- **Status:** Todo
- **Priority:** High
- **Objective:** Create Python project structure, dependencies, lint/test config, `.env.example`, `.gitignore`.
- **Depends on:** None
- **Files likely to change:**
  - `pyproject.toml`, `requirements.txt`, `.env.example`, `.gitignore`
  - `app/`, `src/`, `tests/`, `data/` directories
- **Acceptance criteria:**
  - [ ] `pip install -r requirements.txt` succeeds
  - [ ] `pytest` runs (even if zero tests initially)
  - [ ] `ruff check` passes on scaffold files
  - [ ] `.env.example` lists all env var names from technical design
- **Test requirement:** Smoke import of `app.config`
- **PRD reference:** NFR code quality

---

### TASK-002: Data models and repository

- **Status:** Todo
- **Priority:** High
- **Objective:** SQLAlchemy models with `user_id` scoping and `WellnessRepository` CRUD/upsert.
- **Depends on:** TASK-001
- **Files likely to change:**
  - `src/models/*.py`, `src/repositories/wellness_repository.py`
  - `tests/integration/test_repository.py`, `tests/conftest.py`
- **Acceptance criteria:**
  - [ ] User, MoodEntry, JournalEntry, Insight, ChatMessage models created
  - [ ] Default user seeded on first run
  - [ ] Mood/journal upsert by `entry_date` works
  - [ ] `clear_user_data` removes all user records
- **Test requirement:** Integration tests for all repository methods
- **PRD reference:** FR-004

---

### TASK-003: Safety module

- **Status:** Todo
- **Priority:** High
- **Objective:** Crisis detector, disclaimers, helpline data, output post-filter, `SafetyService`.
- **Depends on:** TASK-001
- **Files likely to change:**
  - `src/safety/crisis_detector.py`, `disclaimers.py`, `helplines.py`
  - `app/components/crisis_panel.py`
  - `tests/unit/test_crisis_detector.py`, `tests/unit/test_safety_output_filter.py`
- **Acceptance criteria:**
  - [ ] Crisis keywords detected in journal/chat text
  - [ ] India helplines returned with correct numbers
  - [ ] Disclaimer text available for onboarding
  - [ ] Banned advice phrases filtered from LLM output
  - [ ] Crisis detection runs before any LLM call (verified in tests)
- **Test requirement:** Unit tests with positive/negative crisis cases
- **PRD reference:** FR-005, FR-006, SEC-010

---

### TASK-004: Mood check-in page

- **Status:** Todo
- **Priority:** High
- **Objective:** Streamlit check-in page with validation and persistence.
- **Depends on:** TASK-002, TASK-003
- **Files likely to change:**
  - `app/pages/1_checkin.py`, `app/components/mood_form.py`
  - `src/services/mood_service.py`, `src/utils/validation.py`
  - `tests/unit/test_validation.py`
- **Acceptance criteria:**
  - [ ] Mood, energy, sleep inputs (1–5) with validation
  - [ ] Optional tags (mock test, family pressure, burnout, etc.)
  - [ ] Daily upsert: updating same day overwrites entry
  - [ ] Success/error feedback shown
- **Test requirement:** Unit tests for mood validation and service
- **PRD reference:** FR-002, FR-012

---

### TASK-005: Journal entry page

- **Status:** Todo
- **Priority:** High
- **Objective:** Journal page with length validation, crisis detection, persistence.
- **Depends on:** TASK-002, TASK-003
- **Files likely to change:**
  - `app/pages/2_journal.py`
  - `src/services/journal_service.py`
  - `tests/integration/test_journal_service.py`
- **Acceptance criteria:**
  - [ ] Journal enforces min/max character limits
  - [ ] Crisis language shows helpline panel
  - [ ] Entry saved with `crisis_flagged` flag
  - [ ] Empty state guidance for first-time users
- **Test requirement:** Integration test for crisis flag on save
- **PRD reference:** FR-003, FR-005, FR-012

---

### TASK-006: Grok client adapter

- **Status:** Todo
- **Priority:** High
- **Objective:** `GrokClient` protocol, OpenAI-compatible implementation, `MockGrokClient`, prompts, schemas.
- **Depends on:** TASK-001, TASK-003
- **Files likely to change:**
  - `src/llm/client.py`, `prompts.py`, `schemas.py`
  - `tests/unit/test_schemas.py`, `tests/unit/test_prompts.py`
- **Acceptance criteria:**
  - [ ] `GrokClient` interface with insight, chat, coping methods
  - [ ] Real client uses `XAI_API_KEY` and configurable models
  - [ ] Retry with backoff on transient errors
  - [ ] `MockGrokClient` for tests
  - [ ] Insight JSON parsed via Pydantic `InsightPayload`
- **Test requirement:** Unit tests for schema parsing and mock client
- **PRD reference:** FR-013, SEC-001

---

### TASK-007: Insight generation and dashboard

- **Status:** Todo
- **Priority:** High
- **Objective:** `InsightService`, insights page with trends chart and AI summary.
- **Depends on:** TASK-002, TASK-003, TASK-006
- **Files likely to change:**
  - `src/services/insight_service.py`
  - `app/pages/3_insights.py`, `app/components/insight_display.py`
  - `tests/integration/test_insight_service.py`
- **Acceptance criteria:**
  - [ ] Requires ≥ 2 entries in last 7 days for generation
  - [ ] Structured insight displayed (triggers, patterns, themes, suggestions)
  - [ ] Mood trend chart with text summary
  - [ ] Cached insight shown on API failure
  - [ ] Crisis blocks LLM call
- **Test requirement:** Integration test with mocked Grok
- **PRD reference:** FR-007, FR-008, FR-014

---

### TASK-008: Companion chat

- **Status:** Todo
- **Priority:** High
- **Objective:** Chat page with context window, turn limits, crisis gate.
- **Depends on:** TASK-002, TASK-003, TASK-006
- **Files likely to change:**
  - `src/services/chat_service.py`
  - `app/pages/4_chat.py`
  - `tests/integration/test_chat_service.py`
- **Acceptance criteria:**
  - [ ] Recent mood/journal context included in prompts
  - [ ] Max 5 user turns per session enforced
  - [ ] Crisis language blocks LLM and shows helplines
  - [ ] Chat history persisted
  - [ ] Loading and error states
- **Test requirement:** Integration test for turn limit and crisis block
- **PRD reference:** FR-009, FR-015

---

### TASK-009: Coping toolkit

- **Status:** Todo
- **Priority:** Medium
- **Objective:** Generate breathing exercises, reframing prompts, micro-break plans.
- **Depends on:** TASK-003, TASK-006
- **Files likely to change:**
  - `src/services/coping_service.py`
  - `app/pages/5_coping.py`
- **Acceptance criteria:**
  - [ ] User selects exercise type
  - [ ] Output uses exam type context
  - [ ] Crisis blocks generation
  - [ ] Loading and error states
- **Test requirement:** Unit test with mock client
- **PRD reference:** FR-010

---

### TASK-010: History dashboard

- **Status:** Todo
- **Priority:** Medium
- **Objective:** Timeline of moods, journals, insights with empty states.
- **Depends on:** TASK-002
- **Files likely to change:**
  - `app/pages/6_history.py`
- **Acceptance criteria:**
  - [ ] Lists mood entries with date, scores, tags
  - [ ] Lists journal entries (preview, not full content in table)
  - [ ] Lists generated insights with dates
  - [ ] Empty state when no data
  - [ ] Clear all data action with confirmation
- **Test requirement:** Manual verification; repository clear tested in TASK-002
- **PRD reference:** FR-011, FR-016

---

### TASK-011: Accessibility pass

- **Status:** Todo
- **Priority:** High
- **Objective:** High-contrast CSS, labels, chart text alternatives, a11y checklist.
- **Depends on:** TASK-004 through TASK-010
- **Files likely to change:**
  - `app/styles.py`, `app/main.py`, all pages and components
- **Acceptance criteria:**
  - [ ] High-contrast theme toggle or default high-contrast styles
  - [ ] All inputs have labels and help text
  - [ ] Mood colors are color-blind safe
  - [ ] Charts have text summary alongside
  - [ ] A11Y checklist documented in README
- **Test requirement:** Manual checklist per PRD A11Y-009
- **PRD reference:** A11Y-001 through A11Y-009

---

### TASK-012: Security review and dependency audit

- **Status:** Todo
- **Priority:** High
- **Objective:** Verify no secrets, safe logging, input validation, dependency pins.
- **Depends on:** TASK-001 through TASK-010
- **Files likely to change:**
  - `requirements.txt` (pinned versions)
  - `src/utils/logging.py`
- **Acceptance criteria:**
  - [ ] No hardcoded API keys
  - [ ] `.env` in `.gitignore`
  - [ ] Logging excludes sensitive content
  - [ ] `pip-audit` run documented in README
- **Test requirement:** Security unit tests (injection samples, error messages)
- **PRD reference:** SEC-001 through SEC-010

---

### TASK-013: Integration tests and README

- **Status:** Todo
- **Priority:** High
- **Objective:** Full test suite green; README with setup, safety disclaimer, limitations.
- **Depends on:** TASK-001 through TASK-012
- **Files likely to change:**
  - `README.md`, `tests/`
- **Acceptance criteria:**
  - [ ] All pytest tests pass
  - [ ] README covers install, env vars, run, safety disclaimer
  - [ ] README documents app limitations (not medical advice)
  - [ ] `.env.example` complete
- **Test requirement:** Full `pytest` run
- **PRD reference:** AC-008

---

## Implementation Order

```
TASK-001 → TASK-002 + TASK-003 (parallel) → TASK-006
         → TASK-004, TASK-005
         → TASK-007, TASK-008, TASK-009, TASK-010
         → TASK-011, TASK-012, TASK-013
```

**First implementable task:** TASK-001
