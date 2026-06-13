# Mental Wellness Tracker

A Generative AI-powered mental wellness tracker for Indian students preparing for high-stakes exams (NEET, JEE, CUET, CAT, GATE, UPSC). Built with Python and Streamlit, powered by [xAI Grok](https://docs.x.ai/).

## Important Safety Notice

**This app is not a substitute for professional mental health care, diagnosis, or treatment.**

If you are in crisis, contact:

| Helpline | Number |
|----------|--------|
| Tele-MANAS | 14416 / 1-800-891-4416 |
| iCall (TISS) | +91-9152987821 |
| Vandrevala Foundation | 1860-2662-345 / 1800-233-3330 |

## Features

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
- **LLM:** xAI Grok via OpenAI-compatible API
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

Add your xAI API key to `.env`:

```
XAI_API_KEY=your_key_here
```

Get a key at [accounts.x.ai](https://accounts.x.ai). New accounts receive promotional API credits.

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

Without `XAI_API_KEY`, mood/journal logging works; AI features use mock responses. Without `ELEVENLABS_API_KEY`, chat works but voice playback shows setup instructions.

## Testing

```bash
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
| `XAI_API_KEY` | — | xAI API key (required for live AI) |
| `XAI_MODEL_CHAT` | `grok-4.1-fast` | Chat/coping model |
| `XAI_MODEL_INSIGHT` | `grok-4.1-fast` | Insight model |
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
- Requires internet for live Grok and ElevenLabs API calls
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

Internal/educational use. Review xAI API terms before production deployment.
