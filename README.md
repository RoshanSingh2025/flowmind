# FlowMind

**FlowMind** is an AI Workflow Copilot that converts software screen recordings into
documentation, FAQs, onboarding guides, and an interactive AI knowledge base.

> Status: Foundation phase. AI features are intentionally **not implemented yet** — this
> repository currently ships the production-grade scaffolding (infra, API skeleton, DI,
> repository/service layers, frontend shell) that AI features will be built on top of.

---

## Monorepo layout

```
flowmind/
├── backend/                 # FastAPI 3.12 + Poetry, Clean Architecture
│   └── app/
│       ├── api/             # HTTP layer only (routers + DI wiring) — no business logic
│       ├── core/            # config, logging, middleware, exception handling
│       ├── agents/          # (reserved) AI agent orchestration — empty for now
│       ├── services/        # business logic / use cases
│       ├── repositories/    # persistence access (repository pattern)
│       ├── models/          # SQLAlchemy ORM models
│       ├── schemas/         # Pydantic request/response schemas
│       ├── database/        # engine/session management
│       ├── vectorstore/     # (reserved) Qdrant client wrapper
│       ├── evaluation/      # (reserved) eval harness for AI agents
│       ├── prompts/         # (reserved) prompt templates
│       └── utils/           # generic helpers
├── frontend/                 # Next.js 15 App Router + TS + Tailwind + shadcn/ui
├── .github/workflows/         # CI (lint, type-check, test)
├── docker-compose.yml
└── .pre-commit-config.yaml
```

## Architecture

The backend follows **Clean Architecture** with a strict dependency direction:

```
api (routers) → services (use cases) → repositories (data access) → models (ORM)
                       ↓
                   schemas (I/O contracts, never leak ORM models to the API layer)
```

Rules enforced by convention (and reviewed in PRs):

- Routers never contain business logic. They validate input (via Pydantic schemas),
  call a service through FastAPI's dependency injection, and shape the HTTP response.
- Services own business rules and orchestrate one or more repositories. Services never
  touch `Request`/`Response` objects or raw SQL.
- Repositories are the only layer allowed to talk to SQLAlchemy. They expose
  intention-revealing methods (e.g. `get_by_id`, `create`), not generic query builders.
- Everything is wired through `Depends(...)` so every layer is swappable and testable in
  isolation (e.g. swap a repository for a fake in unit tests).

## Getting started (local dev)

### Prerequisites
- Docker + Docker Compose
- Node.js 20+ / pnpm (frontend, if running outside Docker)
- Python 3.12 + Poetry (backend, if running outside Docker)

### Run everything with Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend API → http://localhost:8000
- API docs (Swagger) → http://localhost:8000/docs
- Postgres → localhost:5432
- Redis → localhost:6379
- Qdrant → http://localhost:6333

### Run backend locally (without Docker)

```bash
cd backend
poetry install
cp .env.example .env
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

### Run frontend locally (without Docker)

```bash
cd frontend
pnpm install
cp .env.example .env.local
pnpm dev
```

## Quality tooling

| Concern           | Tool                          |
|--------------------|-------------------------------|
| Lint / format (py) | Ruff + Black                  |
| Tests (py)         | Pytest (+ pytest-asyncio)     |
| Lint (ts)          | ESLint                        |
| Pre-commit hooks   | pre-commit (ruff, black, eslint, trailing whitespace) |
| CI                 | GitHub Actions                |

```bash
pre-commit install   # run once after cloning
```

## Roadmap (next phases — not in this delivery)

1. Screen recording ingestion pipeline (upload → storage → frame/audio extraction).
2. Agent pipeline in `app/agents` (transcription, scene segmentation, doc generation).
3. Embedding + retrieval via `app/vectorstore` (Qdrant) for the interactive knowledge base.
4. Prompt library in `app/prompts` and eval harness in `app/evaluation`.
5. Frontend workspace UI (recording upload, generated docs viewer, chat-with-your-docs).

Each phase will be proposed and approved separately before implementation.
