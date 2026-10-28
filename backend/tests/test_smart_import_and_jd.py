import io
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_jd_analysis_endpoint():
    sample_jd = """
    Senior Full-Stack Engineer at Acme Corp
    We are looking for an experienced Senior Full-Stack Engineer to scale our cloud-native platforms.
    Responsibilities:
    - Architect and build high-throughput microservices using Python, FastAPI, and Docker.
    - Design reactive user interfaces using React and TypeScript.
    - Optimize SQL queries on PostgreSQL and configure Redis caching layers.
    Requirements:
    - 4+ years experience with Python, FastAPI, React, and TypeScript.
    - Strong knowledge of Docker, Kubernetes, and AWS cloud environments.
    - Experience in database optimization and CI/CD pipelines.
    Nice to have:
    - Experience with Kafka and GraphQL.
    """
    res = client.post("/api/v1/jd/analyze", json={"jd_text": sample_jd})
    assert res.status_code == 200
    data = res.json()
    assert "role_title" in data
    assert len(data["required_skills"]) > 0
    assert any("Python" in s or "FastAPI" in s or "React" in s for s in data["required_skills"] + data["keywords"])
    assert len(data["key_responsibilities"]) > 0


def test_smart_import_parse_text():
    sample_resume = """
    Jane Doe
    jane.doe@example.com | (555) 019-2834 | New York, NY
    Summary: Experienced full stack software engineer specializing in Python and React.
    
    Skills: Python, FastAPI, React, PostgreSQL, Docker, Git
    
    Education:
    BS in Computer Science, Columbia University, 2018-2022.
    """
    res = client.post("/api/v1/import/parse-text", json={"raw_text": sample_resume})
    assert res.status_code == 200
    draft = res.json()
    assert draft["profile"]["email"] == "jane.doe@example.com"
    assert len(draft["skills"]) > 0


def test_smart_import_file_upload():
    file_content = b"John Smith\njohn.smith@example.com\nSkills: Python, React, AWS\n"
    files = {"file": ("resume.txt", io.BytesIO(file_content), "text/plain")}
    res = client.post("/api/v1/import/parse-file", files=files)
    assert res.status_code == 200
    draft = res.json()
    assert draft["profile"]["email"] == "john.smith@example.com"


def test_smart_import_commit():
    payload = {
        "profile": {
            "full_name": "Imported User",
            "email": "imported@example.com",
            "headline": "Lead Architect",
            "summary": "Imported professional profile."
        },
        "skills": [
            {"name": "GraphQL", "category": "technical", "proficiency": "advanced"}
        ],
        "education": [],
        "projects": [],
        "experience": [],
        "certifications": [],
        "achievements": [],
        "publications": [],
        "languages": [],
        "extra_activities": [],
        "replace_existing": False
    }
    res = client.post("/api/v1/import/commit", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["committed_counts"]["skills"] == 1
