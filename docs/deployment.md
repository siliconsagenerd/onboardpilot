# Deployment

## Services

1. `sublime-vibrancy` (FastAPI backend)
   - Source: `siliconsagenerd/onboardpilot`
   - Root directory: repository root
   - Dockerfile: `backend/Dockerfile`
   - Public URL: `https://sublime-vibrancy-production-3a42.up.railway.app`
2. `onboardpilot-frontend` (Vue 3 SPA served by nginx)
   - Source: `siliconsagenerd/onboardpilot`
   - Root directory: `frontend`
   - Dockerfile: `Dockerfile`
   - Public URL: `https://onboardpilot-frontend-production.up.railway.app`

## Backend variables (names only)

- `APP_ENV=production`
- `SECRET_KEY` (required, non-default)
- `OPERATOR_AUTH_REQUIRED=true`
- `DATABASE_URL=sqlite:////data/onboardpilot.db`
- `CORS_ORIGINS=https://onboardpilot-frontend-production.up.railway.app`
- `SEED_ON_STARTUP=false`
- `PORT=8000`
- `RAILWAY_DOCKERFILE_PATH=backend/Dockerfile`

## Frontend variables (names only)

- `VITE_API_BASE_URL=https://sublime-vibrancy-production-3a42.up.railway.app`
- `PORT=80`

## Deployment sequence

1. Rotate `SECRET_KEY` if compromised.
2. Deploy backend with migrations (`alembic upgrade head`).
3. Run seeding explicitly only when needed (`SEED_ON_STARTUP=true` for one deploy, then set false).
4. Set backend `CORS_ORIGINS` to the exact frontend origin.
5. Deploy frontend with `VITE_API_BASE_URL`.
6. Verify backend and frontend URLs.

## Code rollback

1. `git revert <commit>` or checkout the previous commit.
2. Push the reverted commit.
3. Redeploy the affected Railway service.

## Database recovery

1. Back up `/data/onboardpilot.db` before any risky change.
2. Restore the SQLite file from backup into the mounted volume.
3. Restart the backend once.
4. Verify `/api/public/demo` and a protected route.
