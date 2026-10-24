# OnboardPilot

Internal IT onboarding orchestration for IT, managers, and new employees. One case per starter, with checklist dependencies, hardware handover, access provisioning, open items, audit trail, and a printable handover protocol.

Live demo: (placeholder)

## Features

- Role-based access: IT Admin, Manager, New Employee
- Onboarding cases with status tracking and progress
- Dependency-aware checklist with blocked-state explanations
- Hardware handover that updates the related checklist item
- Access-request state machine: requested, approved, provisioned, verified
- Open items with owners, priorities, due dates, and overdue detection
- Bilingual IT guides (German/English) with search
- Full audit trail per case
- Printable handover PDF protocol
- Read-only public demo case (Anna Beispiel, synthetic data only)
- German/English UI toggle

## Architecture

Backend: FastAPI + SQLAlchemy + SQLite + Alembic. Frontend: Vue 3 + TypeScript + Vite + Tailwind. Docker Compose for local full-stack run.

```
onboardpilot/
  src/onboardpilot/   FastAPI app, models, routers, services
  alembic/            database migrations
  frontend/           Vue 3 SPA
  tests/              pytest suite
  docker-compose.yml
```

## Quick start (local)

Backend:
```
cd onboardpilot
python -m venv .venv && source .venv/bin/activate
pip install -e .
PYTHONPATH=src alembic upgrade head
PYTHONPATH=src python -m onboardpilot.services.seed
PYTHONPATH=src uvicorn onboardpilot.main:app --reload
```

Frontend:
```
cd frontend
npm install
npm run dev
```

## Docker

```
docker compose up --build
```
Backend: http://localhost:8000, Frontend: http://localhost:5173. SQLite data persists in the `onboardpilot_data` volume.

## Demo credentials

- admin / Admin123! (IT Admin)
- manager / Manager123! (Manager)
- employee / Employee123! (New Employee)

## API overview

See docs/api.md. All `/api/*` routes require Bearer token except `/api/auth/login`. `/public/*` and `/health` are open.

## Security and privacy

- Synthetic data only; no real identities.
- No real emails, SMS, or notifications.
- Secrets via environment variables; never committed.
- SQLite database files excluded from Git.

## Deployment plan

Prefer Railway for backend and database; Vercel for frontend if split is clean, otherwise both on Railway. Railway login required from the user before deployment.

## Roadmap

- Email notifications (optional, off by default)
- Manager approval UI polish
- E2E test suite
- Production database migration to PostgreSQL
