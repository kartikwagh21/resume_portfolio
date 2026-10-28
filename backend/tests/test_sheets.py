import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.scripts.seed_data import seed_database

client = TestClient(app)


def test_sheets_status():
    res = client.get("/api/v1/sheets/status")
    assert res.status_code == 200
    data = res.json()
    assert "is_configured" in data
    assert "last_sync_status" in data
    assert "mode" in data


def test_sheets_export_and_sync():
    # 1. Export
    exp_res = client.post("/api/v1/sheets/export", json={})
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["status"] == "success"
    assert "tabs_exported" in exp_data
    assert "Skills" in exp_data["tabs_exported"]
    assert "Projects" in exp_data["tabs_exported"]
    assert "Profile" in exp_data["tabs_exported"]

    # 2. Check status updated
    status_res = client.get("/api/v1/sheets/status")
    assert status_res.status_code == 200
    assert status_res.json()["last_synced_at"] is not None

    # 3. Sync back from sheet
    sync_res = client.post("/api/v1/sheets/sync", json={})
    assert sync_res.status_code == 200
    sync_data = sync_res.json()
    assert sync_data["status"] == "success"
