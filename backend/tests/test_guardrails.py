import pytest
from backend.app.ai.guardrails import AntiHallucinationGuard


def test_metric_invariants_clean_pass():
    source_texts = ["Engineered high-throughput API reducing latency by 45% with 25M+ requests."]
    rewritten_clean = "Orchestrated backend optimization initiative, slashing latency by 45% across 25M+ requests."

    is_valid, issues = AntiHallucinationGuard.verify_numeric_invariants(rewritten_clean, source_texts)
    assert is_valid is True
    assert len(issues) == 0


def test_metric_invariants_hallucination_detected():
    source_texts = ["Engineered high-throughput API reducing latency by 45%."]
    # Rephrase fabricated a new metric: "95%" and "$1.2M"
    rewritten_hallucinated = "Overhauled system architecture achieving 95% latency reduction and saving $1.2M."

    is_valid, issues = AntiHallucinationGuard.verify_numeric_invariants(rewritten_hallucinated, source_texts)
    assert is_valid is False
    assert len(issues) >= 1
    assert any("95%" in issue or "1.2m" in issue.lower() for issue in issues)


def test_record_id_verification_whitelist():
    valid_db_ids = {1, 2, 3}
    ai_generated_items = [
        {"id": 1, "title": "Project Alpha", "relevance_score": 90},
        {"id": 2, "title": "Project Beta", "relevance_score": 85},
        {"id": 9999, "title": "Invented Ghost Project", "relevance_score": 99},
        {"title": "Unidentified Item Without ID", "relevance_score": 50}
    ]

    verified_items, warnings = AntiHallucinationGuard.verify_record_ids(
        ai_generated_items, valid_db_ids, entity_name="project"
    )

    assert len(verified_items) == 2
    assert verified_items[0]["id"] == 1
    assert verified_items[1]["id"] == 2
    assert all(item["is_verified"] is True for item in verified_items)
    assert len(warnings) == 2
    assert any("9999" in w for w in warnings)


def test_bullet_guard_fallback():
    original = "Architected Redis caching layer reducing API response time by 45%."
    # Fabricated metric in candidate rephrase:
    hallucinated = "Architected Redis caching layer cutting response time by 88% and saving $500K."

    final_text, status, issues = AntiHallucinationGuard.guard_bullet_rephrase(
        original_bullet=original,
        candidate_rephrase=hallucinated,
        allowed_skills={"Redis", "Python"},
        retry_callback=None
    )

    assert status == "FALLBACK_ORIGINAL"
    assert final_text == original
    assert len(issues) > 0
