import os
import sys

# Ensure backend root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal
from backend.app.services.portfolio_service import PortfolioService
from backend.app.services.matching_service import MatchingService
from backend.app.services.export_service import ResumeExportService
from backend.app.schemas import resume as resume_schemas
from backend.app.api.v1.resume import assemble_tailored_data


def generate_all_samples():
    print("🎨 Generating customized sample resumes for 2 distinct JDs...")
    db = SessionLocal()
    samples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../samples"))
    os.makedirs(samples_dir, exist_ok=True)

    try:
        # Load sample JDs
        with open(os.path.join(samples_dir, "sample_jd_fullstack.txt"), "r") as f:
            jd_fullstack = f.read()

        with open(os.path.join(samples_dir, "sample_jd_data_analyst.txt"), "r") as f:
            jd_data_analyst = f.read()

        # ---------------- 1. SAMPLE 1: Full-Stack Engineer ----------------
        print("⚡ Processing Sample 1: Senior Full-Stack Engineer...")
        match_fs = MatchingService.match_portfolio_to_jd(db, jd_fullstack)
        
        # Pick top relevant skill IDs for full-stack
        portfolio = PortfolioService.get_full_portfolio(db)
        fs_skill_names = {"Python", "FastAPI", "React", "TypeScript", "Docker", "Kubernetes", "PostgreSQL", "Redis", "AWS", "GraphQL", "Git", "GitHub Actions"}
        fs_skill_ids = [s.id for s in portfolio["skills"] if s.name in fs_skill_names]

        # Prioritize Event Streaming and Cloud Cost Dashboard projects
        fs_proj_ids = [p["id"] for p in match_fs["ranked_projects"][:2]]
        fs_exp_ids = [e["id"] for e in match_fs["ranked_experience"]]

        fs_req = resume_schemas.TailorResumeRequest(
            target_role="Senior Full-Stack Engineer",
            target_company="CloudNexus Technologies",
            jd_text=jd_fullstack,
            selected_skill_ids=fs_skill_ids,
            selected_project_ids=fs_proj_ids,
            selected_experience_ids=fs_exp_ids,
            selected_cert_ids=[c.id for c in portfolio["certifications"][:2]],
            custom_summary=(
                "Senior Full-Stack Engineer with 5+ years building resilient web services, low-latency microservices, "
                "and modern responsive React applications. Expert in Python (FastAPI), TypeScript, and containerized cloud systems "
                "with proven metrics including a 45% latency reduction and handling 25M+ daily requests."
            ),
            template_name="modern_clean",
            match_score=match_fs["match_score"]
        )

        fs_resume_data = assemble_tailored_data(db, fs_req)
        pdf_fs = ResumeExportService.generate_pdf(fs_resume_data, template_name="modern_clean")
        docx_fs = ResumeExportService.generate_docx(fs_resume_data, template_name="modern_clean")

        with open(os.path.join(samples_dir, "resume_fullstack.pdf"), "wb") as f:
            f.write(pdf_fs)
        with open(os.path.join(samples_dir, "resume_fullstack.docx"), "wb") as f:
            f.write(docx_fs)
        print("  ✅ Saved samples/resume_fullstack.pdf and samples/resume_fullstack.docx")

        # ---------------- 2. SAMPLE 2: Data Analyst / Analytics Engineer ----------------
        print("⚡ Processing Sample 2: Senior Data & Analytics Engineer...")
        match_da = MatchingService.match_portfolio_to_jd(db, jd_data_analyst)

        # Pick top relevant skill IDs for data analytics
        da_skill_names = {"Python", "SQL", "PostgreSQL", "Pandas", "Apache Kafka", "Redis", "SQLAlchemy", "AWS", "Datadog", "Prometheus", "System Architecture"}
        da_skill_ids = [s.id for s in portfolio["skills"] if s.name in da_skill_names]

        # Prioritize Event Streaming Analytics and DataNexus Experience
        da_proj_ids = [p["id"] for p in match_da["ranked_projects"] if "Analytics" in p["title"] or "Dashboard" in p["title"]]
        da_exp_ids = [e["id"] for e in match_da["ranked_experience"]]

        da_req = resume_schemas.TailorResumeRequest(
            target_role="Senior Data & Analytics Engineer",
            target_company="MetroMetrics Data Labs",
            jd_text=jd_data_analyst,
            selected_skill_ids=da_skill_ids,
            selected_project_ids=da_proj_ids,
            selected_experience_ids=da_exp_ids,
            selected_cert_ids=[c.id for c in portfolio["certifications"]],
            custom_summary=(
                "Senior Systems & Data Analytics Engineer specializing in high-volume event ingestion, SQL query optimization, "
                "and distributed pipeline telemetry. Proven experience automating 500GB+ daily ETL pipelines, "
                "reducing query execution latency by 45%, and architecting real-time streaming infrastructure."
            ),
            template_name="classic_ivy",
            match_score=match_da["match_score"]
        )

        da_resume_data = assemble_tailored_data(db, da_req)
        pdf_da = ResumeExportService.generate_pdf(da_resume_data, template_name="classic_ivy")
        docx_da = ResumeExportService.generate_docx(da_resume_data, template_name="classic_ivy")

        with open(os.path.join(samples_dir, "resume_data_analyst.pdf"), "wb") as f:
            f.write(pdf_da)
        with open(os.path.join(samples_dir, "resume_data_analyst.docx"), "wb") as f:
            f.write(docx_da)
        print("  ✅ Saved samples/resume_data_analyst.pdf and samples/resume_data_analyst.docx")

        print("🎉 Successfully generated all sample JDs, PDFs, and DOCX files!")

    except Exception as e:
        print(f"❌ Error generating samples: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    generate_all_samples()
