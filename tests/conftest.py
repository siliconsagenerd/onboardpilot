"""Pytest fixtures for OnboardPilot."""

import os
import tempfile

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPERATOR_AUTH_REQUIRED", "true")
os.environ.setdefault("SEED_ON_STARTUP", "false")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from onboardpilot.db.models import Base
from onboardpilot.db import get_db
from onboardpilot.main import app
from onboardpilot.services.seed import seed_if_empty


@pytest.fixture(scope="function")
def db_session():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = f"sqlite:///{path}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session, engine, path
    finally:
        session.close()
        engine.dispose()
        try:
            os.remove(path)
        except OSError:
            pass


@pytest.fixture(scope="function")
def client(db_session):
    session, engine, path = db_session
    # seed
    from onboardpilot.db import SessionLocal as _SL
    # override SessionLocal temporarily
    import onboardpilot.db as dbmod
    import onboardpilot.services.seed as seedmod
    orig_db = dbmod.SessionLocal
    orig_seed = seedmod.SessionLocal
    new_sessionmaker = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    dbmod.SessionLocal = new_sessionmaker
    seedmod.SessionLocal = new_sessionmaker
    seed_if_empty()

    def override_get_db():
        s = new_sessionmaker()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    dbmod.SessionLocal = orig_db
    seedmod.SessionLocal = orig_seed
