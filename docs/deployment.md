# Deployment Guide — OnboardPilot

Production deployment documentation for OnboardPilot (Railway-only primary deployment plan).

## Architecture

- **Backend**: FastAPI (Python 3.12) + SQLAlchemy + Alembic + SQLite (or PostgreSQL via DATABASE_URL).
- **Frontend**: Vue 3 + TypeScript + Vite + Tailwind, built as static assets served by Nginx.

## Required Environment Variables

Set these in your production hosting environment (e.g. Railway project settings):

- `SECRET_KEY`: A strong random string for session tokens and crypto security.
- `DATABASE_URL`: Connection string (e.g. `sqlite:///./data/onboardpilot.db` or PostgreSQL connection string).
- `CORS_ORIGINS`: Comma-separated list of allowed frontend origins (e.g. `https://your-frontend.railway.app`).
- `OPERATOR_AUTH_REQUIRED`: Set to `true`.

For the Frontend build (build-time environment variable in Railway/Vercel):
- `VITE_API_BASE_URL`: The public backend URL (e.g. `https://your-backend.railway.app`).

## Production Startup Command (Backend)

Railway or container startup command should execute database migrations, optional seeding, and start Uvicorn:

```bash
alembic upgrade head && python -m onboardpilot.services.seed && uvicorn onboardpilot.main:app --host 0.0.0.0 --port 8000
```

## Deployment Sequence (Railway-Only)

1. Connect your GitHub repository to Railway.
2. Create two services or a monorepo multi-service setup on Railway:
   - **Backend Service**: Root directory `.`, Dockerfile at `backend/Dockerfile` (or buildpacks with start command).
   - **Frontend Service**: Root directory `frontend`, Dockerfile at `frontend/Dockerfile` (or static site hosting).
3. Configure environment variables (`SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, `VITE_API_BASE_URL`).
4. Trigger deployment. Railway will build the containers and start services automatically.

## Verification Commands

After deployment finishes, run these checks:

```bash
# Verify backend health
curl -i https://your-backend.railway.app/health

# Verify public demo endpoint
curl -i https://your-backend.railway.app/public/demo

# Verify protected routes require auth
curl -i https://your-backend.railway.app/api/cases
# Expected: 401 Unauthorized
```

## Rollback Steps

If a deployment introduces issues:
1. Go to the Railway deployment history dashboard.
2. Select the previous successful deployment.
3. Click **Rollback** to instantly revert to the stable version.
4. Verify `/health` and core endpoints.
