---
name: PumpShield AI MVP
overview: Bootstrap PumpShield AI from scratch as a monolithic Next.js + FastAPI + PostgreSQL app with Gemini-powered fraud analysis and Notion audit logging, following the provided spec and MVP success criteria.
todos:
  - id: bootstrap
    content: Create monorepo (FastAPI backend, Next.js frontend, docker-compose PostgreSQL, .env.example)
    status: completed
  - id: auth
    content: "Implement JWT auth: User model, register/login endpoints, password hashing, protected route middleware"
    status: completed
  - id: database
    content: Add Analysis model, Alembic migrations, history/detail API endpoints
    status: completed
  - id: market-data
    content: Build market_data service with yfinance snapshot (price, volume, volatility, ownership)
    status: completed
  - id: risk-engine
    content: Implement modular weighted risk_engine with 5 indicators and Green/Red threshold at 80
    status: completed
  - id: gemini
    content: Integrate Gemini for explainable JSON responses layered on deterministic scores
    status: completed
  - id: notion-sync
    content: Create Notion audit database schema and notion_service to mirror each analysis post-commit
    status: completed
  - id: frontend
    content: Build auth pages, dashboard, analyze page with RiskScoreCard, and history page
    status: completed
  - id: e2e-verify
    content: Run end-to-end MVP verification against all 9 success criteria
    status: in_progress
isProject: false
---

# PumpShield AI — Greenfield MVP Implementation Plan

## Current State

- **Workspace:** Empty (`empty-window`) — no existing code to extend.
- **Approach:** Bootstrap the full MVP from scratch in a new project directory.
- **LLM:** Google Gemini for explainable fraud analysis.
- **Notion:** Two roles — (1) **runtime** audit log via Notion REST API from the backend, and (2) **development** tracking via the Cursor Notion plugin you installed (`/tasks-setup`, `/spec-to-implementation`).

## Target Architecture

```mermaid
flowchart TB
    subgraph client [Client]
        NextApp["Next.js App"]
    end

    subgraph backend [FastAPI Monolith]
        Auth["JWT Auth"]
        AnalysisAPI["Analysis API"]
        MarketData["Market Data Collector"]
        RiskEngine["Risk Engine"]
        GeminiClient["Gemini Client"]
        NotionSync["Notion Sync Service"]
    end

    subgraph storage [Storage]
        Postgres["PostgreSQL"]
        NotionDB["Notion Audit Database"]
    end

    NextApp -->|"REST + JWT"| Auth
    NextApp --> AnalysisAPI
    AnalysisAPI --> MarketData
    MarketData --> RiskEngine
    RiskEngine --> GeminiClient
    RiskEngine --> Postgres
    RiskEngine --> NotionSync
    NotionSync --> NotionDB
    Auth --> Postgres
```

## Proposed Repository Layout

Create a single repo at a path you choose (e.g. `C:\Users\satya\pumpshield-ai`):

```
pumpshield-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/          # SQLAlchemy: User, Analysis
│   │   ├── schemas/         # Pydantic request/response
│   │   ├── routers/         # auth.py, analysis.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── market_data.py
│   │   │   ├── risk_engine.py
│   │   │   ├── gemini_service.py
│   │   │   └── notion_service.py
│   │   └── core/            # security.py (JWT, password hash)
│   ├── alembic/             # migrations
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/                 # Next.js App Router
│   │   ├── (auth)/login, register
│   │   ├── dashboard/
│   │   ├── analyze/
│   │   └── history/
│   ├── components/
│   ├── lib/api.ts
│   └── package.json
├── docker-compose.yml       # PostgreSQL for local dev
└── README.md
```

## Phase 1 — Project Bootstrap & Authentication

**Goal:** Runnable monorepo with secure JWT auth.

### Backend
- Initialize FastAPI app with CORS for `http://localhost:3000`.
- Add dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `psycopg2-binary`, `alembic`, `pydantic-settings`, `python-jose`, `passlib[bcrypt]`, `httpx`.
- Implement `User` model: `id`, `name`, `email`, `password_hash`, `created_at`.
- Endpoints:
  - `POST /auth/register` — validate email uniqueness, hash password, return user
  - `POST /auth/login` — verify credentials, return JWT access token
- JWT middleware protecting analysis routes (`Authorization: Bearer <token>`).

### Frontend
- Scaffold Next.js 14+ with Tailwind CSS.
- Pages: `/register`, `/login` with form validation.
- Store JWT in `httpOnly` cookie or `localStorage` (MVP: `localStorage` + API client interceptor for speed).
- Redirect unauthenticated users from protected routes.

### Deliverable
User can register, log in, and hit a protected `/dashboard` stub.

---

## Phase 2 — Database & Analysis Persistence

**Goal:** PostgreSQL schema and analysis history APIs.

### Database
- `docker-compose.yml` with PostgreSQL 16.
- SQLAlchemy `Analysis` model:
  - `id`, `user_id` (FK), `stock_symbol`, `risk_score` (0–100), `risk_level` (`green`/`red`), `explanation` (text), `indicators` (JSON), `created_at`
- Alembic initial migration.

### API
- `POST /analysis` — protected; accepts `{ "symbol": "AAPL" }`
- `GET /analysis/history` — paginated list for current user
- `GET /analysis/{id}` — single record with ownership check

### Deliverable
Analysis records persist in PostgreSQL even before AI is wired (stub responses acceptable temporarily).

---

## Phase 3 — AI Risk Engine (Gemini)

**Goal:** Explainable 0–100 fraud score with Green/Red classification.

### Market Data (MVP — free tier friendly)
- Use `yfinance` for: price history, volume, volatility, basic fundamentals (institutional ownership proxy).
- Normalize symbol input (uppercase, strip whitespace).
- Return a structured `MarketSnapshot` dict used by the risk engine.

### Modular Risk Engine
Create `backend/app/services/risk_engine.py` with pluggable indicators:

| Indicator | MVP signal source | Max weight |
|-----------|-------------------|------------|
| Volume spike | 3-day vs 30-day avg volume | 30 |
| Social hype | Gemini-estimated from news/symbol context (stub until live APIs) | 25 |
| Price volatility | Std dev of daily returns | 20 |
| Low institutional ownership | yfinance fundamentals | 15 |
| Insider selling | Stub / partial from filings if available | 10 |

- Sum weighted sub-scores → `risk_score` (cap at 100).
- `risk_level = "red" if score >= 80 else "green"`.

### Gemini Integration
- Use `google-generativeai` SDK with `GEMINI_API_KEY`.
- Prompt template includes:
  - Market snapshot data
  - Computed indicator breakdown
  - Instruction to produce a beginner-friendly explanation and bullet-point reasons
- Parse structured JSON from Gemini (use `response_mime_type: application/json` or fenced JSON parsing).
- Fallback: if Gemini fails, return score from deterministic engine + generic explanation.

### Analysis Flow (`POST /analysis`)
1. Validate symbol via Pydantic
2. Fetch market data
3. Compute indicator weights
4. Call Gemini for narrative explanation
5. Save to PostgreSQL
6. Trigger Notion sync (Phase 4)
7. Return full analysis to client

### Deliverable
`POST /analysis` returns score, level, explanation, and indicator breakdown for real symbols.

---

## Phase 4 — Notion Integration (Runtime)

**Goal:** Every completed analysis mirrored to Notion for audit trail and ops dashboard.

> **Note:** This is separate from the Cursor Notion plugin. The backend uses the [Notion API](https://developers.notion.com/) with an integration token.

### Notion Setup (manual, one-time)
1. Create a Notion integration at https://www.notion.so/my-integrations
2. Create **PumpShield Audit Log** database with properties:
   - `Stock` (title)
   - `User` (rich text or email)
   - `Risk Score` (number)
   - `Risk Level` (select: Green, Red)
   - `Explanation` (rich text)
   - `Timestamp` (date)
   - `Analysis ID` (rich text) — for cross-reference with PostgreSQL
3. Share the database with the integration; copy `NOTION_TOKEN` and `NOTION_DATABASE_ID` to `.env`

### Backend Service
- `notion_service.py` using `httpx` → `POST https://api.notion.com/v1/pages`
- Called **after** PostgreSQL commit (fire-and-forget with error logging; do not block user response on Notion failure).
- Log sync failures to app logs for debugging.

### Notion Dashboard (no custom admin UI)
- Use Notion database views:
  - **All Analyses** — default table
  - **High Risk** — filter `Risk Level = Red`
  - **This Week** — filter by `Timestamp`
- Optional: add a Notion page with linked database views for "Total analyses" and "High-risk count" (rollup/count formulas).

### Deliverable
Each analysis appears in Notion within seconds of completion.

---

## Phase 5 — Frontend UI

**Goal:** Complete user-facing MVP per success criteria.

### Pages
| Route | Purpose |
|-------|---------|
| `/login`, `/register` | Auth |
| `/dashboard` | Welcome + quick search + recent analyses |
| `/analyze` | Stock search form + results card |
| `/history` | Paginated analysis history |

### Key UI Components
- **RiskScoreCard** — large score, Green/Red badge, explanation bullets
- **IndicatorBreakdown** — bar/list of weighted factors
- **AnalysisHistoryTable** — symbol, score, level, date, link to detail
- **StockSearchForm** — symbol input with loading state

### Design
- Tailwind: Green (`#22c55e`) for safe, Red (`#ef4444`) for high risk
- Mobile-responsive; beginner-friendly copy (no jargon without tooltips)

### Deliverable
End-to-end flow: register → login → analyze → view history.

---

## Environment Variables

```env
# Backend
DATABASE_URL=postgresql://pumpshield:pumpshield@localhost:5432/pumpshield
JWT_SECRET=<random-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

GEMINI_API_KEY=<google-ai-key>
GEMINI_MODEL=gemini-2.0-flash

NOTION_TOKEN=<notion-integration-token>
NOTION_DATABASE_ID=<audit-log-database-id>

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Development Workflow with Cursor Notion Plugin

Use the plugin for **project management**, not runtime:

1. **Authenticate** Notion MCP (`mcp_auth` for `plugin-notion-workspace-notion`)
2. **`/knowledge-capture`** — save this spec to Notion as project docs
3. **`/spec-to-implementation`** — break phases into Notion tasks
4. **`/tasks-build`** — implement tasks one-by-one with live status updates

---

## MVP Verification Checklist

- [ ] Register and login with JWT
- [ ] Analyze `AAPL` → Green zone with explanation
- [ ] Analyze a volatile/low-float symbol → potentially Red zone
- [ ] History page shows past analyses
- [ ] PostgreSQL stores all records
- [ ] Notion audit database receives mirrored rows
- [ ] Gemini explanation is human-readable with bullet reasons
- [ ] Invalid symbol returns clear error (no crash)

---

## Implementation Order (Recommended)

Build vertically in thin slices rather than finishing entire layers:

1. **Slice 1:** Bootstrap + auth + empty dashboard
2. **Slice 2:** PostgreSQL models + stub `POST /analysis`
3. **Slice 3:** Market data + deterministic risk engine (no Gemini yet)
4. **Slice 4:** Gemini explanations layered on top
5. **Slice 5:** Notion sync
6. **Slice 6:** Frontend analyze + history pages
7. **Slice 7:** Polish, error handling, README

---

## Out of Scope for MVP (per spec)

- Microservices, Redis, Kafka, Kubernetes
- Real-time social media APIs (Reddit/X/Telegram) — stub via Gemini context for now
- Custom admin panel (Notion replaces this)
- Multi-market exchange routing (treat all symbols as Yahoo Finance compatible)
- ArmorSDK (explicitly removed)

---

## Key Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Yahoo Finance rate limits / outages | Cache recent snapshots per symbol (in-memory, 15-min TTL) |
| Gemini JSON parse failures | Retry once; fallback to template explanation |
| Notion sync failures | Async with logging; PostgreSQL remains source of truth |
| Social/insider data gaps in MVP | Weight those indicators lower; label as "limited data" in explanation |
