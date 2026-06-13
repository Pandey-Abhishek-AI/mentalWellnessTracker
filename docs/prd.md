# Product Requirements Document

> **Project:** Mental Wellness Tracker  
> **Status:** Draft  
> **Last updated:** 2026-06-13

## 1. Problem Statement

Indian students preparing for high-stakes board and entrance exams (NEET, JEE, CUET, CAT, GATE, UPSC) face chronic stress, burnout, and self-doubt during months or years of intense study. Standard mood trackers reduce well-being to numeric scales and miss the emotional nuance in open-ended daily journals. Students lack affordable, stigma-free, always-available support that connects their study context to personalized coping strategies.

This product uses Generative AI to analyze open-ended journals and mood logs, surface hidden stress triggers and emotional patterns, and provide hyper-personalized wellness support through conversational AI—including tailored coping strategies, adaptive mindfulness exercises, and motivational encouragement. The app acts as an empathetic digital companion while **not** replacing professional mental health care.

## 2. Goals

1. Enable daily mood check-ins and open-ended journaling with minimal friction.
2. Use Grok (xAI API) to extract stress triggers, patterns, and emotional themes from user data.
3. Provide contextual, empathetic companion chat grounded in recent mood and journal history.
4. Generate adaptive coping strategies and mindfulness exercises tied to exam-prep context.
5. Implement full safety guardrails: crisis detection, India helpline resources, disclaimers.
6. Deliver a local-first MVP architected for future multi-user authentication.
7. Meet engineering standards for code quality, security, efficiency, testing, and accessibility.

## 3. Non-Goals

- Replacing professional therapy, diagnosis, or medication guidance.
- User registration/login in MVP (schema hooks only).
- Mobile native apps, Hindi/regional languages, parent/teacher dashboards.
- Social/community features, payments, push notifications, teletherapy booking.
- Medical claims or exam-specific factual advice from the LLM.

## 4. User Personas

| Persona | Age | Context | Primary needs |
|---------|-----|---------|---------------|
| **Arjun** | 16–18 | NEET/JEE repeater, 10–14 hr study days | Quick check-in, burnout detection, exam-day anxiety coping |
| **Priya** | 20–22 | CAT/GATE aspirant, part-time work | Evening journaling, stress trigger patterns, guilt-free motivation |
| **Rohan** | 18–21 | UPSC/CUET first attempt | Long-horizon tracking, consistency, low-friction companion chat |

**[ASSUMPTION]** English-first UI; Hindi/regional language deferred to post-MVP.

## 5. User Journeys

### Journey 1: First-time onboarding

1. User opens the app and sees a safety disclaimer and privacy notice (local storage warning).
2. User selects exam type (NEET, JEE, CUET, CAT, GATE, UPSC, Board).
3. User optionally sets study schedule context.
4. User acknowledges disclaimer to proceed.

### Journey 2: Daily wellness routine

1. User completes mood check-in (mood 1–5, energy, sleep, optional tags).
2. User writes a journal entry (validated length).
3. Safety module scans input; if crisis language detected, helpline panel shown and LLM blocked.
4. User views insights dashboard or chats with wellness companion.

### Journey 3: AI insights

1. User requests weekly or on-demand insight generation.
2. System aggregates last 7 days of mood/journal data (summarized context).
3. Grok returns structured JSON: triggers, patterns, themes, suggestions.
4. User sees visual trends plus text summary; cached on API failure.

### Journey 4: Companion chat

1. User opens chat with recent mood/journal context injected.
2. User sends message (max 5 turns per session). **[ASSUMPTION]**
3. Crisis check runs before each LLM call.
4. Empathetic, contextual response returned; rate-limited and token-budgeted.

### Journey 5: Crisis escalation

1. User enters self-harm or suicide-related language in journal or chat.
2. Crisis detector flags content before any LLM call.
3. Static India helpline resources displayed; generative advice suppressed.
4. User can still save mood/journal data locally.

## 6. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-001 | Onboarding with safety disclaimer, exam type selection, and acknowledgment | Must |
| FR-002 | Daily mood check-in: mood (1–5), energy (1–5), sleep quality (1–5), optional tags | Must |
| FR-003 | Open-ended journal entry with min/max character validation | Must |
| FR-004 | Persist mood and journal entries to SQLite with user-scoped schema | Must |
| FR-005 | Crisis keyword detection on all user text before LLM calls | Must |
| FR-006 | Display India helpline resources (Tele-MANAS, iCall, Vandrevala) on crisis detection | Must |
| FR-007 | AI insight generation: structured JSON with triggers, patterns, themes, suggestions | Must |
| FR-008 | Insights dashboard with mood trends and AI summary | Must |
| FR-009 | Companion chat with recent context window and session turn limit | Must |
| FR-010 | Coping toolkit: AI-generated breathing exercises, reframing prompts, micro-break plans | Must |
| FR-011 | History timeline of moods, journals, and insights | Must |
| FR-012 | Loading, error, and empty states on all pages | Must |
| FR-013 | Grok API integration via env-configured adapter with mock support for tests | Must |
| FR-014 | Cache last successful insight; retry on API failure without blocking data save | Should |
| FR-015 | Daily chat token budget and request rate limiting | Should |
| FR-016 | Clear all local data action | Should |

## 7. Non-Functional Requirements

- **Code quality:** Modular Python packages; type hints; `ruff` + `mypy` compliance.
- **Maintainability:** Repository pattern; service layer; prompt templates separated from UI.
- **Reliability:** Mood/journal save succeeds even when LLM is unavailable.
- **Efficiency:** Summarized 7-day context window; token budgets per chat session.
- **Portability:** Runs locally via `streamlit run` on Windows/macOS/Linux.

## 8. Security Requirements

| ID | Requirement |
|---|---|
| SEC-001 | `XAI_API_KEY` only via environment variables; never committed |
| SEC-002 | No journal or chat content in application logs |
| SEC-003 | Input validation on all user text (length, sanitization) |
| SEC-004 | Prompt injection mitigation: delimiter wrapping, hardened system prompts |
| SEC-005 | LLM system prompts forbid diagnosis, medication advice, crisis minimization |
| SEC-006 | Repository layer scoped by `user_id`; MVP uses default local user |
| SEC-007 | Crisis-flagged content not sent to external analytics |
| SEC-008 | Dependency audit (`pip-audit`); no GPL/AGPL libraries without approval |
| SEC-009 | Safe error messages; no internal stack traces exposed to user |
| SEC-010 | Post-filter banned harmful advice phrases from LLM output |

## 9. Accessibility Requirements

| ID | Requirement |
|---|---|
| A11Y-001 | WCAG 2.1 AA target for applicable criteria |
| A11Y-002 | All inputs have visible labels and help text |
| A11Y-003 | Color-blind-safe mood palette (not red/green only) |
| A11Y-004 | Minimum 4.5:1 contrast for body text; high-contrast theme option |
| A11Y-005 | Text summary alongside charts (not color-only information) |
| A11Y-006 | Plain-language error messages |
| A11Y-007 | Loading states with descriptive text (`st.spinner` / `st.status`) |
| A11Y-008 | Keyboard-operable form controls where Streamlit allows |
| A11Y-009 | Manual accessibility checklist documented and completed before release |

## 10. Responsive Design Requirements

- Streamlit default responsive layout; usable on laptop (1280px+) and tablet (768px+).
- Sidebar navigation collapses on narrow viewports.
- Charts scale within container; text summaries always visible.
- Touch-friendly button sizing on tablet.

## 11. Performance Requirements

| Metric | Target |
|--------|--------|
| Mood/journal save | < 500 ms p95 |
| Page load (local) | < 2 s |
| Insight generation | < 15 s p95 (LLM-dependent) |
| Chat response | < 10 s p95 (LLM-dependent) |
| SQLite queries | < 100 ms p95 for MVP data volumes |

## 12. Scalability Requirements

| Layer | MVP | Future |
|-------|-----|--------|
| Users | Single local profile (`user_id=1`) | Email/OAuth auth, row-level isolation |
| Database | SQLite file | PostgreSQL |
| LLM | Direct Grok calls | Response caching, journal summarization |
| Hosting | Local `streamlit run` | Streamlit Cloud / container |

## 13. Data Requirements

### Entities

- **User:** id, exam_type, study_context, disclaimer_accepted_at, created_at
- **MoodEntry:** id, user_id, mood, energy, sleep_quality, tags (JSON), created_at
- **JournalEntry:** id, user_id, content, crisis_flagged, created_at
- **Insight:** id, user_id, summary_json, period_start, period_end, created_at
- **ChatMessage:** id, user_id, role, content, crisis_flagged, created_at

### Retention

- Local SQLite; user controls data via "clear my data" (FR-016).
- No cloud sync in MVP.

### Privacy

- Health-adjacent data stored only in local `data/wellness.db`.
- Warning shown for shared-family-computer use.

## 14. API Requirements

### External: xAI Grok API

- Auth: `XAI_API_KEY` header
- Models: `XAI_MODEL_CHAT` (default `grok-4.1-fast`), `XAI_MODEL_INSIGHT` (default `grok-4.1-fast`)
- Structured JSON output for insights via prompt + JSON parsing
- Retry with exponential backoff (max 3 attempts)
- Timeout: 30 seconds per request

### Internal: Service interfaces

- `MoodService`, `JournalService`, `InsightService`, `ChatService`, `SafetyService`
- `GrokClient` abstract interface with `MockGrokClient` for tests

## 15. Error Handling Requirements

| Scenario | User-facing behavior |
|----------|---------------------|
| Grok API timeout | "Insight unavailable. Your entry was saved. Try again." + retry button |
| Grok rate limit | Friendly message; suggest waiting; show cached insight if available |
| Invalid journal length | Inline validation message before submit |
| Empty insight data | Empty state: "Log a few more days to unlock insights." |
| Database error | Generic error; log internally without sensitive content |
| Crisis detected | Helpline panel; no LLM response |

## 16. Testing Requirements

| Layer | Coverage |
|-------|----------|
| Unit | Mood validation, crisis detector, prompt builders, JSON parsing, date aggregation |
| Integration | SQLite repository CRUD; Grok client with mocks |
| Security | Prompt injection samples; crisis path bypasses LLM; no secret leakage in errors |
| Accessibility | Manual checklist per A11Y-009 |
| Smoke | Seed data → mocked insight → verify key service paths |

**Tooling:** `pytest`, `pytest-mock`, `ruff`, `mypy`.

## 17. Acceptance Criteria

### AC-001: Onboarding
- [ ] Disclaimer must be acknowledged before accessing main features
- [ ] Exam type saved to user profile

### AC-002: Mood check-in
- [ ] User can log mood, energy, sleep with valid ranges (1–5)
- [ ] Entry persisted and visible in history
- [ ] One mood entry per day (update allowed)

### AC-003: Journal
- [ ] Journal accepts 10–5000 characters **[ASSUMPTION]**
- [ ] Crisis language triggers helpline panel
- [ ] Entry saved even when crisis flagged

### AC-004: Insights
- [ ] Insight generated from last 7 days when ≥ 2 journal or mood entries exist
- [ ] Structured output displays triggers, patterns, themes, suggestions
- [ ] Cached insight shown on API failure

### AC-005: Companion chat
- [ ] Chat uses recent mood/journal context
- [ ] Max 5 turns per session enforced
- [ ] Crisis language blocks LLM and shows helplines

### AC-006: Coping toolkit
- [ ] User can generate breathing exercise, reframing prompt, or micro-break plan
- [ ] Output is exam-context aware (uses user exam type)

### AC-007: Safety
- [ ] No LLM call when crisis detected
- [ ] India helplines displayed with correct numbers
- [ ] Disclaimer visible on first launch

### AC-008: Quality
- [ ] All unit and integration tests pass
- [ ] No secrets in repository
- [ ] README documents setup, limitations, and safety disclaimer

## 18. Out of Scope

- User registration/login (MVP)
- Mobile native app
- Hindi/regional languages
- Parent/teacher dashboards
- Professional teletherapy booking
- Medical diagnosis or medication guidance
- Social/community features
- Payment/subscription
- Push notifications / SMS reminders
- PIN lock for shared devices (post-MVP candidate)

## 19. Open Questions

| # | Question | Status |
|---|----------|--------|
| OQ-001 | Exam types: NEET, JEE, CUET, CAT, GATE, UPSC, Board — extend? | **[ASSUMPTION]** Accepted as-is |
| OQ-002 | Max 5 companion chat turns per session? | **[ASSUMPTION]** Accepted |
| OQ-003 | Optional PIN lock for shared devices in MVP? | Deferred post-MVP |
| OQ-004 | Journal min 10 / max 5000 characters? | **[ASSUMPTION]** Accepted |
