import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_profile_lifecycle():
    # 1. Fetch initial or auto-created profile
    res = client.get("/api/v1/profile")
    assert res.status_code == 200
    data = res.json()
    assert "email" in data

    # 2. Update profile
    update_payload = {
        "full_name": "Test Engineer",
        "headline": "Senior Cloud Developer",
        "email": "test@example.com",
        "summary": "Building resilient systems."
    }
    put_res = client.put("/api/v1/profile", json=update_payload)
    assert put_res.status_code == 200
    updated = put_res.json()
    assert updated["full_name"] == "Test Engineer"
    assert updated["headline"] == "Senior Cloud Developer"
    assert updated["email"] == "test@example.com"


def test_skills_crud():
    # 1. Create skill
    skill_data = {
        "name": "Python",
        "category": "technical",
        "proficiency": "expert",
        "include_by_default": True
    }
    res = client.post("/api/v1/portfolio/skills", json=skill_data)
    assert res.status_code == 201
    created = res.json()
    assert created["name"] == "Python"
    skill_id = created["id"]

    # 2. List skills
    list_res = client.get("/api/v1/portfolio/skills")
    assert list_res.status_code == 200
    skills = list_res.json()
    assert any(s["id"] == skill_id for s in skills)

    # 3. Update skill
    upd_res = client.put(f"/api/v1/portfolio/skills/{skill_id}", json={"proficiency": "advanced"})
    assert upd_res.status_code == 200
    assert upd_res.json()["proficiency"] == "advanced"

    # 4. Duplicate handling
    dup_res = client.post("/api/v1/portfolio/skills", json=skill_data)
    assert dup_res.status_code == 201
    assert dup_res.json()["id"] == skill_id  # Returns existing updated record


def test_education_crud():
    edu_data = {
        "institution": "Stanford University",
        "degree": "Master of Science",
        "field_of_study": "Computer Science",
        "start_date": "2020-09",
        "end_date": "2022-06",
        "gpa": "3.9 / 4.0",
        "highlights": ["Published research paper in ML", "Teaching Assistant for CS101"]
    }
    create_res = client.post("/api/v1/portfolio/education", json=edu_data)
    assert create_res.status_code == 201
    item = create_res.json()
    edu_id = item["id"]
    assert item["institution"] == "Stanford University"
    assert len(item["highlights"]) == 2

    # Update
    upd_res = client.put(f"/api/v1/portfolio/education/{edu_id}", json={"gpa": "3.95 / 4.0"})
    assert upd_res.status_code == 200
    assert upd_res.json()["gpa"] == "3.95 / 4.0"

    # Delete
    del_res = client.delete(f"/api/v1/portfolio/education/{edu_id}")
    assert del_res.status_code == 204


def test_projects_crud():
    # Create a skill to associate
    sk_res = client.post("/api/v1/portfolio/skills", json={"name": "FastAPI", "category": "technical", "proficiency": "expert"})
    skill_id = sk_res.json()["id"]

    project_data = {
        "title": "Cloud Monitoring Engine",
        "role": "Backend Lead",
        "description": "High performance telemetry backend.",
        "tech_stack": ["FastAPI", "Python", "Docker"],
        "bullet_points": ["Engineered distributed worker pool", "Reduced query latency by 50%"],
        "live_url": "https://monitor.example.com",
        "start_date": "2023-01",
        "skill_ids": [skill_id]
    }
    res = client.post("/api/v1/portfolio/projects", json=project_data)
    assert res.status_code == 201
    p = res.json()
    p_id = p["id"]
    assert p["title"] == "Cloud Monitoring Engine"
    assert len(p["skills"]) == 1
    assert p["skills"][0]["id"] == skill_id

    # Update
    upd_res = client.put(f"/api/v1/portfolio/projects/{p_id}", json={"role": "Lead Architect"})
    assert upd_res.status_code == 200
    assert upd_res.json()["role"] == "Lead Architect"


def test_experience_crud():
    exp_data = {
        "company": "Apex Cloud Systems",
        "role": "Senior Engineer",
        "employment_type": "Full-time",
        "location": "Remote",
        "start_date": "2022-01",
        "end_date": "Present",
        "is_current": True,
        "bullet_points": ["Scaled API gateway to 10M requests daily", "Maintained 99.99% availability"]
    }
    res = client.post("/api/v1/portfolio/experience", json=exp_data)
    assert res.status_code == 201
    exp = res.json()
    assert exp["company"] == "Apex Cloud Systems"
    assert exp["is_current"] is True


def test_certifications_and_credentials_crud():
    cert_data = {
        "name": "AWS Solutions Architect",
        "issuer": "Amazon Web Services",
        "issue_date": "2023-01",
        "credential_id": "AWS-12345"
    }
    res = client.post("/api/v1/portfolio/certifications", json=cert_data)
    assert res.status_code == 201
    cert = res.json()
    assert cert["name"] == "AWS Solutions Architect"

    ach_data = {
        "title": "Hackathon Winner",
        "issuer": "TechCon",
        "date": "2023-05",
        "description": "First place out of 100 teams"
    }
    res = client.post("/api/v1/portfolio/achievements", json=ach_data)
    assert res.status_code == 201

    pub_data = {
        "title": "Scalable Vector Databases",
        "publisher": "ACM Tech",
        "publication_date": "2023-07",
        "description": "Analysis of indexing approaches"
    }
    res = client.post("/api/v1/portfolio/publications", json=pub_data)
    assert res.status_code == 201


def test_aggregate_portfolio_endpoint():
    res = client.get("/api/v1/portfolio")
    assert res.status_code == 200
    data = res.json()
    assert "profile" in data
    assert "skills" in data
    assert "projects" in data
    assert "experience" in data
    assert "counts" in data
    assert data["counts"]["skills"] >= 1
    assert data["counts"]["projects"] >= 1
