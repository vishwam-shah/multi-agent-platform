# Multi-Agent AI Workflow Platform

[![CI](https://github.com/vishwam-shah/multi-agent-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/vishwam-shah/multi-agent-platform/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A full-stack platform that orchestrates **planner** and **worker** AI agents to decompose high-level goals into executable steps, with tool calling, persistent memory, automatic retries, and per-run tracing.

## Architecture

```
User Goal
    │
    ▼
┌──────────┐    plan_json     ┌──────────────┐
│ Planner  │ ───────────────► │ Orchestrator │
│  Agent   │                  │   (run loop) │
└──────────┘                  └──────┬───────┘
                                     │ for each step
                                     ▼
                              ┌──────────────┐
                              │   Worker     │◄── Tools: web_search, code_exec
                              │   Agent      │──► Memory Store
                              └──────┬───────┘
                                     │ trace events
                                     ▼
                              ┌──────────────┐
                              │   Tracer     │──► SQLite
                              └──────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLAlchemy (async), SQLite |
| AI/LLM | LangChain, OpenAI API, Anthropic Claude API |
| Tools | Tavily web search, sandboxed Python execution |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |

## Features

- **Goal Decomposition** — Planner agent breaks goals into 2-8 actionable steps
- **Tool Calling** — Worker agents use web search and code execution tools
- **Memory Persistence** — Results from each step are stored and passed to subsequent steps
- **Retry with Backoff** — Failed steps retry up to 3 times with exponential backoff
- **Full Tracing** — Every LLM call, tool invocation, and decision is logged with timing and token counts
- **Model Selection** — Choose between OpenAI (GPT-4o) and Anthropic (Claude) per run
- **React Dashboard** — Submit goals, monitor progress, drill into step results and traces

## Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- API keys: OpenAI, Anthropic, Tavily

### Backend

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys

pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`. SQLite database is auto-created at `data/platform.db`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` requests to the backend.

### Run Tests

```bash
cd backend
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/runs` | Create and start a new run |
| GET | `/api/runs` | List all runs |
| GET | `/api/runs/{id}` | Get run detail with steps |
| DELETE | `/api/runs/{id}` | Cancel a running run |
| GET | `/api/runs/{id}/steps` | List steps for a run |
| GET | `/api/runs/{id}/traces` | List all traces for a run |
| GET | `/api/health` | Health check |

## Project Structure

```
multi-agent-platform/
├── backend/
│   ├── app/
│   │   ├── agents/          # Planner, worker, orchestrator, LLM providers
│   │   ├── api/             # FastAPI route handlers
│   │   ├── memory/          # Per-run memory store
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── tools/           # Web search, code execution, tool registry
│   │   ├── tracing/         # Event tracer
│   │   ├── config.py        # Settings (env vars)
│   │   ├── database.py      # Async SQLAlchemy setup
│   │   └── main.py          # FastAPI app
│   └── tests/
├── frontend/
│   └── src/
│       ├── api/             # Backend API client
│       ├── components/      # Reusable UI components
│       ├── pages/           # Dashboard, RunDetail, TraceView
│       └── types/           # TypeScript interfaces
└── README.md
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, coding guidelines, and how to submit a pull request. Please open an issue first for larger changes so we can discuss the approach.

## License

MIT — see [LICENSE](LICENSE).
