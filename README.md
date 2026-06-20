# PumpShield AI

AI-powered financial fraud detection platform that identifies pump-and-dump manipulation risk in stocks.

## Stack

- **Frontend:** Next.js 15, React, Tailwind CSS
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Database:** SQLite (local dev) or PostgreSQL (production)
- **AI:** Google Gemini
- **Audit Log:** Notion API

## Quick Start

### 1. Start PostgreSQL (optional — SQLite used by default for local dev)

```bash
docker compose up -d
```

For PostgreSQL, set in `backend/.env`:
```
DATABASE_URL=postgresql+psycopg://pumpshield:pumpshield@localhost:5432/pumpshield
```

### 2. Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Edit with your keys
# SQLite: tables auto-create on startup. PostgreSQL: run `alembic upgrade head` first.
uvicorn app.main:app --reload --port 8001
```

### 3. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment Variables

See `backend/.env.example` and `frontend/.env.local.example`.

### Notion Audit Log Setup

1. Create an integration at https://www.notion.so/my-integrations
2. Create a database named **PumpShield Audit Log** with properties:
   - Stock (title), User (rich text), Risk Score (number)
   - Risk Level (select: Green, Red), Explanation (rich text)
   - Timestamp (date), Analysis ID (rich text)
3. Share the database with your integration
4. Set `NOTION_TOKEN` and `NOTION_DATABASE_ID` in `backend/.env`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, get JWT |
| POST | `/analysis` | Analyze a stock symbol |
| GET | `/analysis/history` | List past analyses |
| GET | `/analysis/{id}` | Get single analysis |
| GET | `/health` | Health check |

## Risk Scoring

- **Green (0–79):** Low manipulation risk
- **Red (80–100):** High manipulation risk

Five weighted indicators: volume spike, social hype, price volatility, institutional ownership, insider selling.

## Smoke Test

With the backend running on port 8001:

```bash
cd backend
python scripts/smoke_test.py
```
