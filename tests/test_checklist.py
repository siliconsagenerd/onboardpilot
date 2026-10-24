"""Tests for checklist dependency enforcement."""

import pytest


def admin_token(client):
    return client.post("/api/auth/login", json={"username": "admin", "password": "Admin123!"}).json()["access_token"]


def test_blocked_completion(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    c = client.post("/api/cases", json={"employee_name": "Blocked Test", "role_template": "developer", "start_date": "2026-10-20"}, headers=h).json()
    cid = c["id"]
    items = client.get(f"/api/cases/{cid}/checklist", headers=h).json()
    monitor = [i for i in items if i["key"] == "monitor"][0]
    r = client.patch(f"/api/checklist/{monitor['id']}", json={"status": "completed"}, headers=h)
    assert r.status_code == 400
    assert "Blocked" in r.json()["detail"]
    client.delete(f"/api/cases/{cid}", headers=h)


def test_dependency_order_completion(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    # create a fresh case
    c = client.post("/api/cases", json={"employee_name": "Dep Test", "role_template": "developer", "start_date": "2026-10-20"}, headers=h).json()
    cid = c["id"]
    items = client.get(f"/api/cases/{cid}/checklist", headers=h).json()
    # laptop has no deps, complete it
    laptop = [i for i in items if i["key"] == "laptop"][0]
    r = client.patch(f"/api/checklist/{laptop['id']}", json={"status": "completed"}, headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "completed"
    # monitor depends on laptop; now can complete
    monitor = [i for i in client.get(f"/api/cases/{cid}/checklist", headers=h).json() if i["key"] == "monitor"][0]
    r = client.patch(f"/api/checklist/{monitor['id']}", json={"status": "completed"}, headers=h)
    assert r.status_code == 200
    # cleanup
    client.delete(f"/api/cases/{cid}", headers=h)


def test_reopen_item(client):
    tok = admin_token(client)
    h = {"Authorization": f"Bearer {tok}"}
    cases = client.get("/api/cases", headers=h).json()
    anna = [c for c in cases if c["employee_name"] == "Anna Beispiel"][0]
    items = client.get(f"/api/cases/{anna['id']}/checklist", headers=h).json()
    done = [i for i in items if i["status"] == "completed"][0]
    r = client.post(f"/api/checklist/{done['id']}/reopen", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "not_started"
    # restore
    client.patch(f"/api/checklist/{done['id']}", json={"status": "completed"}, headers=h)
