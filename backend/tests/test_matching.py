import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.scripts.seed_data import seed_database

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def prepare_seed():
    seed_database()


def test_matching_endpoint_fullstack_jd():
    jd = """
    We are seeking a Lead Full-Stack Engineer with strong Python and React skills.
    Requirements:
    - 4+ years of professional experience with Python, FastAPI, and PostgreSQL.
    - Deep knowledge of Docker, Kubernetes, and AWS cloud architecture.
    - Hands-on experience with Kafka and distributed event architectures.
    Nice to have:
    - Rust or Go experience.
    """
    res = client.post("/api/v1/matching/match", json={"jd_text": jd})
    assert res.status_code == 200
    data = res.json()

    assert "match_score" in data
    assert data["match_score"] > 60
    assert "score_breakdown" in data
    assert len(data["matched_skills"]) > 0
    assert any(s["name"] == "Python" for s in data["matched_skills"])
    assert any(s["name"] == "FastAPI" for s in data["matched_skills"])
    assert len(data["ranked_projects"]) > 0
    assert len(data["ranked_experience"]) > 0
    assert data["is_verified"] is True
    # All ranked projects must have is_verified == True
    assert all(p.get("is_verified") for p in data["ranked_projects"])


def test_rephrase_bullet_endpoint():
    payload = {
        "original_bullet": "Optimized high-volume database queries and introduced Redis distributed caching, slashing average API response latency by 45%.",
        "keywords": "high throughput, low latency, database scaling",
        "target_role": "Senior Backend Engineer"
    }
    res = client.post("/api/v1/matching/rephrase-bullet", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "rephrased_bullet" in data
    assert data["is_verified"] is True
