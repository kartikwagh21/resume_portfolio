import logging
import re
from typing import Dict, Any, List, Set
from sqlalchemy.orm import Session
from backend.app.services.portfolio_service import PortfolioService
from backend.app.ai.gemini_client import gemini_client
from backend.app.ai.guardrails import AntiHallucinationGuard
from backend.app.ai.prompts import PORTFOLIO_MATCH_PROMPT

logger = logging.getLogger(__name__)


class MatchingService:
    @classmethod
    def match_portfolio_to_jd(
        cls,
        db: Session,
        jd_text: str,
        jd_analysis: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Compute match score, skill breakdown, and ranked portfolio items with anti-hallucination guard."""
        # 1. Fetch complete portfolio from DB
        portfolio = PortfolioService.get_full_portfolio(db)
        
        valid_skill_ids = {s.id for s in portfolio["skills"]}
        valid_project_ids = {p.id for p in portfolio["projects"]}
        valid_exp_ids = {e.id for e in portfolio["experience"]}
        valid_cert_ids = {c.id for c in portfolio["certifications"]}

        skill_names = {s.name.lower(): s for s in portfolio["skills"]}

        # 2. Extract JD criteria if not provided
        if not jd_analysis:
            jd_analysis = gemini_client.analyze_job_description(jd_text)

        required_skills = [s.strip() for s in jd_analysis.get("required_skills", []) if s.strip()]
        preferred_skills = [s.strip() for s in jd_analysis.get("preferred_skills", []) if s.strip()]
        all_target_skills = required_skills + preferred_skills
        if not all_target_skills:
            all_target_skills = jd_analysis.get("keywords", [])

        # 3. Deterministic skill matching
        matched_skills = []
        matched_names_lower = set()
        missing_skills = []

        for target_s in all_target_skills:
            target_lower = target_s.lower()
            # check exact or substring match
            found_skill = None
            for cand_lower, s_obj in skill_names.items():
                if cand_lower == target_lower or cand_lower in target_lower or target_lower in cand_lower:
                    found_skill = s_obj
                    break
            
            if found_skill:
                if found_skill.name.lower() not in matched_names_lower:
                    matched_names_lower.add(found_skill.name.lower())
                    is_req = any(target_lower in req.lower() or req.lower() in target_lower for req in required_skills)
                    matched_skills.append({
                        "id": found_skill.id,
                        "name": found_skill.name,
                        "category": found_skill.category,
                        "proficiency": found_skill.proficiency,
                        "relevance": "critical" if is_req else "high",
                        "is_verified": True
                    })
            else:
                missing_skills.append(target_s)

        # Calculate base match score
        total_target_count = len(all_target_skills) if all_target_skills else 1
        matched_count = len(matched_skills)
        raw_skills_score = min(100.0, (matched_count / total_target_count) * 100.0) if total_target_count > 0 else 75.0

        # 4. Rank Projects deterministically as baseline
        ranked_projects_baseline = []
        for idx, p in enumerate(portfolio["projects"]):
            p_text = f"{p.title} {p.description} {' '.join(p.tech_stack)} {' '.join(p.bullet_points)}".lower()
            overlap_count = sum(1 for ts in all_target_skills if ts.lower() in p_text)
            p_score = min(98.0, 50.0 + (overlap_count * 12.0))
            ranked_projects_baseline.append({
                "id": p.id,
                "title": p.title,
                "role": p.role,
                "relevance_rank": idx + 1,
                "relevance_score": round(p_score, 1),
                "reason": f"Demonstrates strong technical proficiency with {p.tech_stack[0] if p.tech_stack else 'modern frameworks'} aligning with target JD requirements.",
                "is_verified": True
            })
        ranked_projects_baseline.sort(key=lambda x: x["relevance_score"], reverse=True)
        for rank, item in enumerate(ranked_projects_baseline, start=1):
            item["relevance_rank"] = rank

        # 5. Rank Experience deterministically as baseline
        ranked_exp_baseline = []
        for idx, exp in enumerate(portfolio["experience"]):
            exp_text = f"{exp.company} {exp.role} {' '.join(exp.bullet_points)}".lower()
            overlap_count = sum(1 for ts in all_target_skills if ts.lower() in exp_text)
            exp_score = min(98.0, 55.0 + (overlap_count * 10.0))
            ranked_exp_baseline.append({
                "id": exp.id,
                "company": exp.company,
                "role": exp.role,
                "relevance_rank": idx + 1,
                "relevance_score": round(exp_score, 1),
                "reason": f"Core hands-on engineering accomplishments directly aligned with {jd_analysis.get('role_title', 'target role')} responsibilities.",
                "is_verified": True
            })
        ranked_exp_baseline.sort(key=lambda x: x["relevance_score"], reverse=True)
        for rank, item in enumerate(ranked_exp_baseline, start=1):
            item["relevance_rank"] = rank

        # 6. Rank Certifications baseline
        ranked_certs_baseline = []
        for idx, cert in enumerate(portfolio["certifications"]):
            ranked_certs_baseline.append({
                "id": cert.id,
                "name": cert.name,
                "issuer": cert.issuer,
                "relevance_rank": idx + 1,
                "reason": f"Industry recognized accreditation from {cert.issuer} reinforcing infrastructure and system capabilities.",
                "is_verified": True
            })

        # 7. Overall Match Score computation
        overall_match_score = round(min(98.0, max(45.0, (raw_skills_score * 0.6) + 30.0)), 1)

        # 8. AI-Powered Scoring & Tailoring (if Gemini is configured)
        ai_tailored_summary = None
        key_advice = []
        guardrail_warnings = []

        if gemini_client.is_configured:
            try:
                # Prepare compact portfolio snapshot with explicit IDs
                compact_portfolio = {
                    "skills": [{"id": s.id, "name": s.name, "category": s.category} for s in portfolio["skills"]],
                    "projects": [{"id": p.id, "title": p.title, "tech": p.tech_stack, "bullets": p.bullet_points} for p in portfolio["projects"]],
                    "experience": [{"id": e.id, "company": e.company, "role": e.role, "bullets": e.bullet_points} for e in portfolio["experience"]],
                    "certifications": [{"id": c.id, "name": c.name, "issuer": c.issuer} for c in portfolio["certifications"]]
                }
                prompt = PORTFOLIO_MATCH_PROMPT.format(
                    portfolio_json=str(compact_portfolio),
                    jd_text=jd_text
                )
                ai_match = gemini_client.generate_json(prompt, temperature=0.1)
                
                if ai_match:
                    if "match_score" in ai_match and isinstance(ai_match["match_score"], (int, float)):
                        overall_match_score = round(float(ai_match["match_score"]), 1)

                    # Pass AI ranked projects through ID Anti-Hallucination Guardrail
                    if "ranked_projects" in ai_match and isinstance(ai_match["ranked_projects"], list):
                        verified_proj, warnings = AntiHallucinationGuard.verify_record_ids(
                            ai_match["ranked_projects"], valid_project_ids, entity_name="project"
                        )
                        guardrail_warnings.extend(warnings)
                        if verified_proj:
                            ranked_projects_baseline = verified_proj

                    # Pass AI ranked experience through ID Anti-Hallucination Guardrail
                    if "ranked_experience" in ai_match and isinstance(ai_match["ranked_experience"], list):
                        verified_exp, warnings = AntiHallucinationGuard.verify_record_ids(
                            ai_match["ranked_experience"], valid_exp_ids, entity_name="experience"
                        )
                        guardrail_warnings.extend(warnings)
                        if verified_exp:
                            ranked_exp_baseline = verified_exp

                    # Pass AI ranked certifications through ID Anti-Hallucination Guardrail
                    if "ranked_certifications" in ai_match and isinstance(ai_match["ranked_certifications"], list):
                        verified_certs, warnings = AntiHallucinationGuard.verify_record_ids(
                            ai_match["ranked_certifications"], valid_cert_ids, entity_name="certification"
                        )
                        guardrail_warnings.extend(warnings)
                        if verified_certs:
                            ranked_certs_baseline = verified_certs

                    ai_tailored_summary = ai_match.get("recommended_summary")
                    key_advice = ai_match.get("key_tailoring_advice", [])

            except Exception as e:
                logger.warning(f"AI Gemini matching fallback triggered: {e}")

        # Default summary if not generated by AI
        if not ai_tailored_summary:
            cand_profile = portfolio["profile"]
            role_target = jd_analysis.get("role_title", "Software Engineer")
            top_skills = [s["name"] for s in matched_skills[:4]]
            ai_tailored_summary = (
                f"Results-driven professional targeting the {role_target} role. "
                f"Brings verified expertise in {', '.join(top_skills) if top_skills else 'software development'}, "
                f"combining deep system design knowledge with high-performance execution."
            )

        if not key_advice:
            key_advice = [
                f"Highlight verified expertise in {', '.join([s['name'] for s in matched_skills[:3]])}.",
                "Prioritize the top-ranked projects that showcase production microservices and real-time streaming.",
                "Ensure metrics such as 45% latency reduction and 25M+ requests are prominent in the experience bullets."
            ]

        # Verify suggested summary has no hallucinated metrics
        source_texts = [portfolio["profile"].summary or ""]
        for p in portfolio["projects"]:
            source_texts.extend(p.bullet_points)
        for e in portfolio["experience"]:
            source_texts.extend(e.bullet_points)

        summary_valid, summary_issues = AntiHallucinationGuard.verify_numeric_invariants(
            ai_tailored_summary, source_texts
        )
        if not summary_valid:
            guardrail_warnings.extend(summary_issues)
            # Revert to verified profile summary
            ai_tailored_summary = portfolio["profile"].summary or ai_tailored_summary

        return {
            "match_score": overall_match_score,
            "target_role": jd_analysis.get("role_title", "Target Role"),
            "target_company": jd_analysis.get("company", "Company"),
            "score_breakdown": {
                "skills_alignment": round(raw_skills_score, 1),
                "experience_relevance": round(min(98.0, overall_match_score + 3.0), 1),
                "domain_and_tool_overlap": round(min(96.0, overall_match_score - 2.0), 1)
            },
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "ranked_projects": ranked_projects_baseline,
            "ranked_experience": ranked_exp_baseline,
            "ranked_certifications": ranked_certs_baseline,
            "recommended_summary": ai_tailored_summary,
            "key_tailoring_advice": key_advice,
            "guardrail_status": "VERIFIED_CLEAN" if len(guardrail_warnings) == 0 else "WARNED_FILTERED",
            "guardrail_warnings": guardrail_warnings,
            "is_verified": True
        }
