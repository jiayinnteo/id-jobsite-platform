"""Smoke tests for system endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_ok():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "storage_mode" in body


def test_root():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "message" in resp.json()
