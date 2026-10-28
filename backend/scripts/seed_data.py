import os
import sys

# Ensure backend root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.core.database import SessionLocal, Base, engine
from backend.app.models.portfolio import Profile, Education, Skill, Project, Experience
from backend.app.models.credentials import Certification, Achievement, Publication
from backend.app.models.activities import Language, ExtraActivity
from backend.app.models.history import ResumeHistory


def seed_database():
    print("🌱 Re-initializing database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        print("🌱 Seeding Profile...")
        profile = Profile(
            full_name="Alex Rivera",
            headline="Lead Full-Stack & Cloud Systems Engineer",
            email="alex.rivera.dev@example.com",
            phone="+1 (555) 234-5678",
            location="San Francisco, CA",
            website="https://alexrivera.example.com",
            linkedin_url="https://linkedin.com/in/alexrivera-example",
            github_url="https://github.com/alexrivera-example",
            summary=(
                "Accomplished Full-Stack & Cloud Systems Engineer with 5+ years of experience designing "
                "high-throughput distributed backends, resilient event-driven architectures, and modern responsive web apps. "
                "Proven track record of reducing query latency by 45%, architecting microservices handling 25M+ daily requests, "
                "and mentoring cross-functional engineering teams."
            )
        )
        db.add(profile)
        db.flush()

        print("🌱 Seeding Education...")
        edu = Education(
            institution="University of California, Berkeley",
            degree="Bachelor of Science",
            field_of_study="Computer Science",
            location="Berkeley, CA",
            start_date="2016-08",
            end_date="2020-05",
            gpa="3.85 / 4.0",
            highlights=[
                "Dean's Honors List (6 consecutive semesters)",
                "Relevant Coursework: Distributed Systems, Database Architecture, Machine Learning, Operating Systems",
                "President of Association for Computing Machinery (ACM) Student Chapter"
            ],
            include_by_default=True
        )
        db.add(edu)

        print("🌱 Seeding Skills...")
        skills_data = [
            # Technical Skills
            ("Python", "technical", "expert"),
            ("FastAPI", "technical", "expert"),
            ("TypeScript", "technical", "advanced"),
            ("React", "technical", "advanced"),
            ("PostgreSQL", "technical", "expert"),
            ("Docker", "technical", "expert"),
            ("Kubernetes", "technical", "advanced"),
            ("Redis", "technical", "advanced"),
            ("Apache Kafka", "technical", "advanced"),
            ("GraphQL", "technical", "intermediate"),
            ("Node.js", "technical", "advanced"),
            ("AWS", "technical", "expert"),
            ("SQLAlchemy", "technical", "expert"),
            ("Next.js", "technical", "intermediate"),
            ("Go", "technical", "intermediate"),
            ("Pandas", "technical", "advanced"),
            ("SQL", "technical", "expert"),
            # Tools
            ("Git", "tool", "expert"),
            ("Terraform", "tool", "advanced"),
            ("Datadog", "tool", "advanced"),
            ("Prometheus", "tool", "intermediate"),
            ("GitHub Actions", "tool", "expert"),
            ("Linux", "tool", "expert"),
            ("Vite", "tool", "advanced"),
            ("Postman", "tool", "expert"),
            # Soft Skills
            ("System Architecture", "soft", "expert"),
            ("Agile Leadership", "soft", "advanced"),
            ("Technical Mentorship", "soft", "advanced"),
            ("Incident Response", "soft", "advanced"),
            ("Cross-Functional Collaboration", "soft", "expert")
        ]

        skill_records = {}
        for name, category, proficiency in skills_data:
            skill = Skill(
                name=name,
                category=category,
                proficiency=proficiency,
                include_by_default=True
            )
            db.add(skill)
            skill_records[name] = skill
        db.flush()

        print("🌱 Seeding Projects...")
        p1 = Project(
            title="Distributed Event Stream Analytics Platform",
            role="Lead Architect & Developer",
            description="Engineered a scalable distributed ingestion pipeline processing IoT metrics and transactional event streams in real time.",
            tech_stack=["Python", "FastAPI", "Apache Kafka", "Redis", "PostgreSQL", "Docker"],
            bullet_points=[
                "Architected an event ingestion pipeline using FastAPI and Apache Kafka handling over 12,000 events/sec with sub-50ms latency.",
                "Implemented Redis caching and partitioned PostgreSQL tables, reducing repetitive database read queries by 60%.",
                "Containerized the microservices stack using Docker Compose and orchestrated deployment via Kubernetes manifests.",
                "Configured Prometheus metric exporters and custom Grafana dashboards for proactive latency alerting."
            ],
            live_url="https://demo-analytics.example.com",
            repo_url="https://github.com/alexrivera-example/event-stream-analytics",
            start_date="2023-01",
            end_date="2023-08",
            include_by_default=True
        )
        p1.skills = [
            skill_records["Python"], skill_records["FastAPI"], skill_records["Apache Kafka"],
            skill_records["Redis"], skill_records["PostgreSQL"], skill_records["Docker"]
        ]

        p2 = Project(
            title="Cloud Cost & Telemetry Dashboard",
            role="Full-Stack Developer",
            description="Built a centralized enterprise dashboard consolidating multi-cloud resource utilization, anomaly detection, and spend forecasts.",
            tech_stack=["React", "TypeScript", "Tailwind CSS", "FastAPI", "AWS", "SQLAlchemy"],
            bullet_points=[
                "Designed a responsive Single Page Application using React, TypeScript, and Tailwind CSS with interactive chart visualizations.",
                "Integrated AWS Cost Explorer API and CloudWatch metrics to automatically detect anomalous infrastructure spend spikes.",
                "Engineered automated daily report generation exporting multi-tenant summaries to PDF and CSV formats.",
                "Reduced monthly development AWS expenditures by 28% across 14 team accounts."
            ],
            live_url="https://cost-telemetry.example.com",
            repo_url="https://github.com/alexrivera-example/cloud-cost-dashboard",
            start_date="2022-06",
            end_date="2022-12",
            include_by_default=True
        )
        p2.skills = [
            skill_records["React"], skill_records["TypeScript"], skill_records["FastAPI"],
            skill_records["AWS"], skill_records["SQLAlchemy"]
        ]

        p3 = Project(
            title="Real-Time Collaborative Document Canvas",
            role="Creator & Lead Developer",
            description="Developed an operational transformation based live document collaboration editor supporting concurrent writers and conflict resolution.",
            tech_stack=["Node.js", "TypeScript", "React", "Redis", "Docker"],
            bullet_points=[
                "Constructed WebSocket synchronization server in Node.js facilitating sub-20ms multi-client cursor updates.",
                "Utilized Redis pub/sub channels to broadcast delta patches across distributed server instances with zero state corruption.",
                "Engineered end-to-end unit and integration test suites achieving 94% test coverage using Jest and GitHub Actions CI."
            ],
            live_url="https://canvas-demo.example.com",
            repo_url="https://github.com/alexrivera-example/collab-doc-canvas",
            start_date="2021-03",
            end_date="2021-09",
            include_by_default=True
        )
        p3.skills = [
            skill_records["Node.js"], skill_records["TypeScript"], skill_records["React"],
            skill_records["Redis"], skill_records["Docker"], skill_records["Git"]
        ]

        db.add_all([p1, p2, p3])

        print("🌱 Seeding Experience...")
        exp1 = Experience(
            company="CloudScale Technologies",
            role="Senior Full-Stack Engineer",
            employment_type="Full-time",
            location="San Francisco, CA",
            start_date="2022-03",
            end_date="Present",
            is_current=True,
            bullet_points=[
                "Architected resilient REST and GraphQL microservices in Python (FastAPI) and TypeScript that serve 25M+ requests daily with 99.98% uptime.",
                "Optimized high-volume database queries and introduced Redis distributed caching, slashing average API response latency by 45%.",
                "Spearheaded the migration of monolithic workloads to AWS EKS (Kubernetes), reducing infrastructure provisioning time from 4 hours to 8 minutes.",
                "Mentored 6 software engineers on clean code practices, system observability, and CI/CD automated test pipelines.",
                "Collaborated with product designers and frontend teams to deliver 12 major enterprise features with zero critical production bugs."
            ],
            include_by_default=True
        )

        exp2 = Experience(
            company="DataNexus Systems",
            role="Full-Stack Software Engineer",
            employment_type="Full-time",
            location="San Jose, CA",
            start_date="2020-06",
            end_date="2022-02",
            is_current=False,
            bullet_points=[
                "Built and maintained core SaaS web applications using React, TypeScript, Python, and PostgreSQL.",
                "Automated data pipeline extraction workflows handling 500GB+ daily customer telemetry data using Python and SQL.",
                "Designed role-based access control (RBAC) and OAuth2 authentication safeguarding sensitive client data.",
                "Authored 150+ unit and integration tests, increasing core backend service code coverage from 68% to 91%."
            ],
            include_by_default=True
        )

        exp3 = Experience(
            company="NovaTech Labs",
            role="Software Engineering Intern",
            employment_type="Internship",
            location="Palo Alto, CA",
            start_date="2019-06",
            end_date="2019-08",
            is_current=False,
            bullet_points=[
                "Developed internal administration portal widgets in React and Flask to monitor background ETL jobs.",
                "Refactored legacy database migration scripts, resolving recurring deadlock issues during scheduled batch processing.",
                "Participated in daily standups and sprint planning sessions within an agile Scrum squad."
            ],
            include_by_default=True
        )

        db.add_all([exp1, exp2, exp3])

        print("🌱 Seeding Certifications...")
        cert1 = Certification(
            name="AWS Certified Solutions Architect - Associate",
            issuer="Amazon Web Services (AWS)",
            issue_date="2022-11",
            expiry_date="2025-11",
            credential_id="AWS-SAA-8392019",
            credential_url="https://aws.amazon.com/verification",
            include_by_default=True
        )
        cert2 = Certification(
            name="Certified Kubernetes Administrator (CKA)",
            issuer="Linux Foundation & CNCF",
            issue_date="2023-05",
            expiry_date="2026-05",
            credential_id="CKA-9402847",
            credential_url="https://www.cncf.io/certification/cka/",
            include_by_default=True
        )
        cert3 = Certification(
            name="HashiCorp Certified: Terraform Associate",
            issuer="HashiCorp",
            issue_date="2023-09",
            expiry_date="2025-09",
            credential_id="HC-TA-182746",
            credential_url="https://www.credly.com/org/hashicorp",
            include_by_default=True
        )
        db.add_all([cert1, cert2, cert3])

        print("🌱 Seeding Achievements...")
        ach1 = Achievement(
            title="1st Place Winner - SF Global Cloud Hackathon 2023",
            issuer="SF Tech Collective & AWS",
            date="2023-10",
            description="Designed and deployed an AI-assisted cloud incident triaging engine in 36 hours among 180 participating engineering teams.",
            include_by_default=True
        )
        ach2 = Achievement(
            title="Engineering Excellence Award",
            issuer="CloudScale Technologies",
            date="2023-12",
            description="Awarded for leading the zero-downtime database migration initiative and achieving a 45% query latency improvement.",
            include_by_default=True
        )
        db.add_all([ach1, ach2])

        print("🌱 Seeding Publications...")
        pub1 = Publication(
            title="Optimizing Query Latency in High-Throughput Sharded Databases",
            publisher="IEEE Distributed Systems Workshop",
            publication_date="2022-09",
            url="https://doi.org/10.1109/dsw.2022.948271",
            description="Authored peer-reviewed paper examining partitioning strategies, connection pooling overhead, and Redis caching topologies in distributed OLTP systems.",
            include_by_default=True
        )
        db.add(pub1)

        print("🌱 Seeding Languages...")
        lang1 = Language(language="English", proficiency="Native")
        lang2 = Language(language="Spanish", proficiency="Professional")
        db.add_all([lang1, lang2])

        print("🌱 Seeding Extra Activities...")
        act1 = ExtraActivity(
            title="Open-Source Maintainer",
            organization="AsyncPy Community",
            role="Core Maintainer",
            start_date="2021-01",
            end_date="Present",
            description="Maintain lightweight Python async utility library with over 2,500 GitHub stars and 120,000 monthly PyPI downloads.",
            include_by_default=True
        )
        act2 = ExtraActivity(
            title="Technical Mentor",
            organization="CodeBridge SF",
            role="Volunteer Mentor",
            start_date="2022-04",
            end_date="Present",
            description="Mentor underrepresented career changers and aspiring software engineers through bi-weekly resume reviews and mock interviews.",
            include_by_default=True
        )
        db.add_all([act1, act2])

        db.commit()
        print("✅ Database successfully seeded with rich realistic dummy data for Alex Rivera!")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
