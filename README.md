# Mental Wellness Tracker

A Generative AI-powered mental wellness tracker for Indian students preparing for high-stakes exams (NEET, JEE, CUET, CAT, GATE, UPSC). Built with Python and Streamlit, powered by [Google Gemini](https://ai.google.dev/).

## Important Safety Notice

**This app is not a substitute for professional mental health care, diagnosis, or treatment.**

If you are in crisis, contact:

| Helpline | Number |
|----------|--------|
| Tele-MANAS | 14416 / 1-800-891-4416 |
| iCall (TISS) | +91-9152987821 |
| Vandrevala Foundation | 1860-2662-345 / 1800-233-3330 |

## Features

- Email login with a stable account UUID (derived from your email)
- Per-account daily AI chat token limits, insight limits, and coping exercise limits
- Daily mood check-in (mood, energy, sleep, tags)
- Open-ended journaling with crisis detection
- AI-powered wellness insights (stress triggers, patterns, themes)
- Empathetic companion chat with session limits and optional voice playback (ElevenLabs)
- Coping toolkit (breathing exercises, reframing, micro-breaks)
- Wellness history and local data management

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.10+
- **Database:** SQLite (local) or PostgreSQL on [Supabase](https://supabase.com)
- **LLM:** Google Gemini via Generative Language API
- **Voice:** ElevenLabs TTS on chat responses
- **Testing:** pytest, ruff, mypy

## Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux
```

Add your Gemini API key to `.env` (from [Google AI Studio](https://aistudio.google.com/apikey)):

```
GEMINI_API_KEY=your_key_here
```

### Supabase PostgreSQL (optional)

1. Create a free project at [supabase.com](https://supabase.com).
2. Open **Project Settings → Database → Connection string**.
3. Choose **URI** and copy the string (use **Session** or **Transaction** pooler for apps).
4. In `.env`, change the scheme from `postgresql://` to `postgresql+psycopg://`:

```
DATABASE_URL=postgresql+psycopg://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

Use **Transaction pooler** (port `6543`), not the direct `db.xxx.supabase.co:5432` host — the direct host often fails DNS on Windows or campus/corporate networks.

Tables are created automatically on first run. To stay local, keep the default SQLite URL.

### ElevenLabs voice (optional, chat page)

1. Create an account at [elevenlabs.io](https://elevenlabs.io) and copy your API key.
2. Pick a voice ID from [Voice Library](https://elevenlabs.io/app/voice-library) (default: Rachel).
3. Add to `.env`:

```
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM
```

On the Chat page, click **Listen** on any assistant reply to hear it aloud.

## Run

```bash
streamlit run app/main.py
```

Create an account on first visit (email + password, min 8 characters). Your **UUID** is generated from your email and controls your daily chat token budget. Use **Log out** in the sidebar to switch accounts.

Without `GEMINI_API_KEY`, mood/journal logging works; AI features use mock responses. Without `ELEVENLABS_API_KEY`, chat works but voice playback shows setup instructions.

## Deploy (Streamlit Community Cloud)

1. Push this repo to GitHub (never commit `.env`).
2. Create an app at [share.streamlit.io](https://share.streamlit.io) with main file `app/main.py`.
3. Paste secrets from `.streamlit/secrets.toml.example` into **Settings → Secrets**.
4. Use `DATABASE_URL = "sqlite:///./data/wellness.db"` for SQLite (data may reset on redeploy).

## Testing

```bash
pip install -r requirements-dev.txt
pytest
ruff check .
```

### Dependency audit

```bash
pip install pip-audit
pip-audit -r requirements.txt
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Google Gemini API key (required for live AI) |
| `GEMINI_MODEL_CHAT` | `gemini-2.0-flash` | Chat/coping model |
| `GEMINI_MODEL_INSIGHT` | `gemini-2.0-flash` | Insight model |
| `DAILY_INSIGHT_LIMIT` | `5` | Max AI insights per account per day |
| `DAILY_COPING_LIMIT` | `10` | Max coping exercises per account per day |
| `LOGIN_MAX_ATTEMPTS` | `5` | Failed logins before lockout |
| `LOGIN_LOCKOUT_MINUTES` | `15` | Login lockout window |
| `DATABASE_URL` | `sqlite:///./data/wellness.db` | SQLite or Supabase PostgreSQL connection |
| `ELEVENLABS_API_KEY` | — | ElevenLabs API key (chat TTS) |
| `ELEVENLABS_VOICE_ID` | `21m00Tcm4TlvDq8ikWAM` | ElevenLabs voice ID |
| `ELEVENLABS_MODEL` | `eleven_multilingual_v2` | TTS model |
| `VOICE_ENABLED` | `true` | Enable Listen buttons on chat |
| `MAX_VOICE_CHARS` | `2500` | Max characters sent to TTS per message |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MIN_JOURNAL_CHARS` | `10` | Minimum journal length |
| `MAX_JOURNAL_CHARS` | `5000` | Maximum journal length |
| `MAX_CHAT_TURNS` | `5` | Max user messages per chat session |
| `LLM_TIMEOUT_SECONDS` | `30` | API timeout |

## Accessibility

- Color-blind-safe mood palette (blue/teal/orange, not red/green only)
- Text summaries alongside charts
- Visible labels and help text on all inputs
- High-contrast CSS theme
- Manual WCAG 2.1 AA checklist (see docs/prd.md A11Y section)

## Limitations

- Local single-user MVP; SQLite keeps data on your device (Supabase stores data in the cloud)
- AI responses may be inaccurate; not medical advice
- Streamlit has inherent accessibility constraints
- Requires internet for live Gemini and ElevenLabs API calls
- English-only UI in MVP

## Project Structure

```
app/          Streamlit UI
src/          Models, services, LLM, safety
tests/        Unit and integration tests
docs/         PRD, technical design, tasks
```

## Documentation

- [Product Requirements](docs/prd.md)
- [Technical Design](docs/technical-design.md)
- [Task List](docs/tasks.md)

## License

Internal/educational use. Review Google Gemini API terms before production deployment.
