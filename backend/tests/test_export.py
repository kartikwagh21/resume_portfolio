import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.scripts.seed_data import seed_database

client = TestClient(app)


def test_resume_preview():
    payload = {
        "target_role": "Staff Backend Engineer",
        "target_company": "CloudTech",
        "custom_summary": "Seasoned backend specialist focused on high performance distributed systems.",
        "template_name": "modern_clean",
        "save_to_history": False
    }
    res = client.post("/api/v1/resume/preview", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "html_preview" in data
    assert ("Alex Rivera" in data["html_preview"] or "Test Engineer" in data["html_preview"])
    assert "Staff Backend Engineer" in data["html_preview"]
    assert "Professional Summary" in data["html_preview"]


def test_resume_export_pdf():
    payload = {
        "target_role": "Senior Full-Stack Engineer",
        "target_company": "Tech Innovations",
        "template_name": "modern_clean"
    }
    res = client.post("/api/v1/resume/export/pdf", json=payload)
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    # PDF files start with %PDF
    assert res.content.startswith(b"%PDF")
    assert len(res.content) > 1000


def test_resume_export_docx():
    payload = {
        "target_role": "Senior Cloud Engineer",
        "target_company": "Enterprise Cloud",
        "template_name": "classic_ivy"
    }
    res = client.post("/api/v1/resume/export/docx", json=payload)
    assert res.status_code == 200
    assert "officedocument.wordprocessingml" in res.headers["content-type"]
    # DOCX files are zip archives starting with PK
    assert res.content.startswith(b"PK")
    assert len(res.content) > 1000


def test_resume_history_lifecycle():
    payload = {
        "target_role": "Principal Systems Architect",
        "target_company": "Scalable Systems Inc",
        "custom_summary": "Architect with 5+ years building distributed pipelines.",
        "template_name": "classic_ivy",
        "match_score": 94.5,
        "save_to_history": True
    }
    # 1. Generate preview and save to history
    prev_res = client.post("/api/v1/resume/preview", json=payload)
    assert prev_res.status_code == 200
    history_id = prev_res.json()["history_id"]
    assert history_id is not None

    # 2. List history
    hist_list = client.get("/api/v1/resume/history")
    assert hist_list.status_code == 200
    items = hist_list.json()
    assert len(items) >= 1
    assert any(item["id"] == history_id for item in items)

    # 3. Retrieve history item
    get_item = client.get(f"/api/v1/resume/history/{history_id}")
    assert get_item.status_code == 200
    item_data = get_item.json()
    assert item_data["target_role"] == "Principal Systems Architect"
    assert item_data["match_score"] == 94.5
