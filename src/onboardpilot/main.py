"""FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from onboardpilot.config import settings
from onboardpilot.db import engine
from onboardpilot.db.models import Base
from onboardpilot.routers import (
    access,
    audit,
    auth,
    cases,
    checklist,
    dashboard,
    guides,
    handover,
    hardware,
    open_items,
    public,
    templates,
)

app = FastAPI(title="OnboardPilot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    settings.ensure_dirs()
    Base.metadata.create_all(bind=engine)
    # run migrations not required for sqlite dev; alembic for prod
    if settings.seed_on_startup:
        try:
            from onboardpilot.services.seed import seed_if_empty

            seed_if_empty()
        except Exception as e:
            print("seed error:", e)


app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(checklist.router)
app.include_router(hardware.router)
app.include_router(access.router)
app.include_router(open_items.router)
app.include_router(audit.router)
app.include_router(guides.router)
app.include_router(dashboard.router)
app.include_router(templates.router)
app.include_router(handover.router)
app.include_router(public.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "OnboardPilot"}
