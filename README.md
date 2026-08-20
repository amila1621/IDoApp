# I DO — Smart To-Do App

A small task-list app with one lightweight LLM feature type a task in plain English (or Finnish) and it's turned into a structured, categorised, scheduled item. If no API key is present or the model call fails, the app degrades gracefully to a pure-Python fallback and keeps working.

---

## Features

**Core**
- Add, mark-as-done, and delete tasks
- Tasks grouped into fixed category folders in the UI
- Persistence via local SQLite (no auth, no setup)

**LLM feature — Natural language → structured task**
- Extracts `title`, `category`, `priority`, `is_outdoor`, `duration_minutes`, `best_time`, a date expression, and optional `steps`
- Deterministic date resolution (LLM proposes a phrase, Python resolves the actual datetime)
- Works with English and Finnish input
- Graceful fallback when the key is missing or the model misbehaves

**Weather**
- Outdoor tasks due within the next 7 days get a short forecast note (via [Open-Meteo](https://open-meteo.com/), no key required)
- Best-effort only — weather never blocks a task from loading

---

## Tech stack

| Layer     | Choice                                                        |
| --------- | ------------------------------------------------------------- |
| Frontend  | React 19 + Vite 8 (plain React, JavaScript), oxlint           |
| Backend   | Python + FastAPI, SQLModel (SQLAlchemy + Pydantic), SQLite    |
| LLM       | Anthropic API (`claude-haiku-4-5` by default, configurable)   |
| Dates     | `dateparser` (timezone-aware, Europe/Helsinki)                |
| Weather   | Open-Meteo daily forecast API                                 |
| Tests     | `pytest` (LLM mocked — no key or network needed)              |

---

## Project structure

```
todo-app/
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── main.py            # FastAPI app, CORS, startup table creation
│   │   ├── db.py              # SQLite engine + session dependency
│   │   ├── models.py          # Task table + Priority/Category enums
│   │   ├── schemas.py         # API request/response schemas
│   │   ├── schemas_llm.py     # Enrichment — the contract for LLM output
│   │   ├── weather.py         # Open-Meteo forecast + "needs weather?" logic
│   │   ├── llm/
│   │   │   ├── client.py      # Anthropic call, availability check, fence-stripping
│   │   │   ├── prompt.py      # System prompt + few-shot examples
│   │   │   ├── enrich.py      # Orchestration: LLM → validate → fallback
│   │   │   └── resolve.py     # Natural-language date → concrete datetime
│   │   └── routers/
│   │       └── tasks.py       # CRUD + /tasks/enrich
│   └── tests/
│       ├── test_llm.py        # Date resolution + enrichment (incl. fallbacks)
│       └── test_weather.py
└── frontend/
    ├── index.html
    ├── vite.config.js
    └── src/
        ├── App.jsx            # Whole UI: folders, cards, add/toggle/delete
        ├── api.js             # Fetch wrappers for the backend
        └── App.css
```

---

## Getting started

### Prerequisites
- Python 3.11+ (for `X | None` typing and `datetime` timezone handling)
- Node.js 20.19+ or 22.12+ (required by Vite 8 / oxlint)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # then edit .env (see below)

uvicorn app.main:app --reload
```

The API runs at **http://127.0.0.1:8000** — interactive docs at **http://127.0.0.1:8000/docs**.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs at **http://localhost:5173** (the backend's CORS is configured for this origin).

### Environment variables

`.env.example` documents everything:

```
ANTHROPIC_API_KEY="anthropic-api-key-here"
ANTHROPIC_MODEL="claude-haiku-4-5"
SQL_ECHO=false
OPEN_METEO_API_URL="https://api.open-meteo.com/v1/forecast"
```

**The API key is optional.** Without it, `client.available()` returns `False` and every add goes straight to the deterministic fallback — the app is fully usable, tasks just aren't enriched. This matches the exercise's "provide mock or fallback data so the app still runs without an API key."

---

## How the LLM feature works

The design goal was to keep the AI portion **tiny but real**, and to let the model do only what models are actually good at.

### Separation of concerns: understanding vs. computation

The LLM is asked to *understand* the task and to propose a **date phrase** (e.g. `"next Monday at 5pm"`) — it is **not** asked to compute an actual date. That job belongs to deterministic Python (`resolve.py` + `dateparser`), because:

- LLM date arithmetic is unreliable and non-reproducible ("what's next Monday?" depends on today).
- Timezone handling (Europe/Helsinki) should be exact and testable.
- It keeps the model's output small and easy to validate.

So the flow is:

```
raw text ──▶ LLM (prompt.py) ──▶ JSON string
                                    │
                          strip fences (client.py)
                                    │
                    validate against Enrichment (schemas_llm.py)
                                    │
              when_expression ──▶ resolve_when() ──▶ concrete datetime
                                    │
                            enriched dict (source: "llm")
```

### Structured output & prompt strategy

- **`schemas_llm.Enrichment`** is a Pydantic model that defines *exactly* what the model must return. The raw output is validated against it (`model_validate_json`), so malformed or off-spec responses are caught rather than trusted.
- **`prompt.py`** pairs a strict system prompt (fixed category set, "keep the title free of time words", "output only JSON") with **few-shot examples** covering the tricky cases: date-vs-time-of-day splitting, priority inference, and when to emit `steps` vs. an empty list.
- The call uses low temperature (`0.2`) and a small `max_tokens` for consistent, cheap, deterministic-ish output.
- `strip_fences()` tolerates the common case of the model wrapping JSON in ```` ```json ```` fences.

### Error handling & fallback

`enrich_task()` (`enrich.py`) is the single orchestration point and is defensive at every step:

1. **No key** → return `_fallback()` immediately, never touch the network.
2. **Model called** → any `LLMError` (network/API failure) or `ValidationError` (bad JSON / wrong shape) is caught and logged, then falls back.
3. **Fallback** → stores the raw text as the title with sane defaults (medium priority, personal category, no date), tagged `source: "fallback"`.

Every enrichment result carries a `source` field (`"llm"` or `"fallback"`) so the tests always know which path ran. The failure modes are exercised directly in the test suite.

### Weather enrichment

`weather.py` adds a small contextual touch: for an **outdoor**, **not-done**, **dated** task falling within the next 7 days, the list endpoint attaches a short forecast note. The forecast fetch is wrapped so it **never raises** — if Open-Meteo is down, tasks still load, just without weather.

---

## API endpoints

| Method | Path                | Purpose                                                        |
| ------ | ------------------- | ------------------------------------------------------------- |
| GET    | `/tasks`            | List all tasks, each with an attached `weather` note (or null)|
| POST   | `/tasks/enrich`     | NL text → enriched task, **persisted**; returns `{task, source}` |
| POST   | `/tasks`            | Create a task from already-structured fields                  |
| GET    | `/tasks/{id}`       | Fetch one task                                                |
| PATCH  | `/tasks/{id}`       | Partial update (title, done, date, category, …)               |
| DELETE | `/tasks/{id}`       | Delete a task                                                 |

> The frontend adds tasks exclusively through `POST /tasks/enrich`, so every new task passes through the LLM (or fallback) path. `POST /tasks` exists for structured/programmatic creation.

---

## Running the tests

```bash
cd backend
pytest
```

The suite runs **without an API key or network access** — the LLM client is monkeypatched. Coverage includes:

- **Date resolution** — `"tomorrow"`, the `"next monday"` edge case, and the empty/None case (`test_llm.py`).
- **Enrichment paths** — the happy LLM path, fallback on a simulated API failure, and fallback when no key is configured (`test_llm.py`).
- **Weather gating** — the full truth table for `needs_weather` (outdoor/indoor, done, undated, far-future) (`test_weather.py`).

There's at least one test around the AI logic with a mocked response, as the exercise suggests.

---

## Design decisions & trade-offs

- **LLM proposes, Python decides (dates).** The most deliberate choice — it keeps the unreliable part (arithmetic, timezones) deterministic and unit-testable, and the model's job narrow.
- **Pydantic contract for model output.** Validating against `Enrichment` turns "the model returned something weird" into a caught, logged, recoverable event instead of a crash or bad data.
- **Enrich = enrich *and* persist.** `POST /tasks/enrich` does both in one call. This keeps the frontend dead simple (one call to add a task), at the cost of coupling enrichment and persistence — a cleaner split would separate "preview enrichment" from "save".
- **SQLite, no auth.** Right-sized for a demo: zero setup, one file, easy to reset (`todo.db` is gitignored).
- **Weather is an enhancement, never a dependency.** It fails silently by design.
- **Fixed location.** Latitude/longitude are hardcoded to Oulu, Finland — fine for a single-user demo, not for real multi-user use.

---

## Known limitations

Being honest about the small slice that's deliberately unfinished:

- **No in-place edit UI.** The backend fully supports editing (`PATCH /tasks/{id}`), but the frontend currently only exposes add, toggle-done, and delete.
- **Single hardcoded location** for weather.
- **No frontend tests** — testing focuses on the backend logic, especially the AI path.

---

## Next steps

- Wire the existing `PATCH` endpoint to an inline edit affordance in the UI.
- Make the weather location configurable (or per-task).
- Add a bulk daily-summary LLM view over pending tasks.
- Add voice input — speak a task instead of typing, transcribed text feeds into the existing enrich flow.
- Wire weather with relevant time — show time-specific forecasts matched to the task's `best_time` and `due_at` hour.
- Mobile app — convert the React frontend into a mobile-friendly app (with React Native).
- Add filtering — filter tasks by category, priority, date range, and completion status.