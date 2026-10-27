"""Tests for authentication and access control."""


def login(client, username="admin", password="Admin123!"):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_valid_login(client):
    r = login(client)
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert data["role"] == "it_admin"


def test_invalid_login(client):
    r = login(client, password="wrong")
    assert r.status_code == 401


def test_me_with_token(client):
    tok = login(client).json()["access_token"]
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200


def test_protected_without_token(client):
    for path in ["/api/cases", "/api/dashboard/summary", "/api/templates", "/api/audit"]:
        r = client.get(path)
        assert r.status_code == 401, path


def test_public_demo_no_auth(client):
    r = client.get("/api/public/demo")
    assert r.status_code == 200
    data = r.json()
    assert data["case"]["employee_name"] == "Anna Beispiel"
    assert data["case"]["is_public_demo"] is True


def test_public_guides(client):
    r = client.get("/api/public/guides")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_docs(client):
    r = client.get("/docs")
    assert r.status_code == 200
