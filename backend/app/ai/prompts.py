"""CareerVault & ResumeForge AI - Gemini Prompts
Original, zero-hallucination structured prompt specifications.
"""

RESUME_PARSE_PROMPT = """
You are an expert ATS Curriculum Vitae parser.
Analyze the following unstructured resume text and extract all identifiable candidate information into structured JSON.

STRICT INSTRUCTIONS:
1. Extract ONLY facts explicitly stated in the input text. Do NOT fabricate, extrapolate, or assume dates, metrics, companies, or credentials.
2. If an optional field is missing, set it to null or an empty list.
3. Categorize skills accurately into "technical", "soft", or "tool".
4. Ensure bullet points are cleanly parsed into individual strings.

Input Resume Text:
{raw_text}

Respond ONLY with a valid JSON object matching this schema:
{{
  "profile": {{
    "full_name": string,
    "headline": string or null,
    "email": string,
    "phone": string or null,
    "location": string or null,
    "website": string or null,
    "linkedin_url": string or null,
    "github_url": string or null,
    "summary": string or null
  }},
  "education": [
    {{
      "institution": string,
      "degree": string,
      "field_of_study": string,
      "location": string or null,
      "start_date": string,
      "end_date": string or null,
      "gpa": string or null,
      "highlights": [string]
    }}
  ],
  "skills": [
    {{
      "name": string,
      "category": "technical" | "soft" | "tool",
      "proficiency": "beginner" | "intermediate" | "advanced" | "expert"
    }}
  ],
  "projects": [
    {{
      "title": string,
      "role": string or null,
      "description": string,
      "tech_stack": [string],
      "bullet_points": [string],
      "live_url": string or null,
      "repo_url": string or null,
      "start_date": string or null,
      "end_date": string or null
    }}
  ],
  "experience": [
    {{
      "company": string,
      "role": string,
      "employment_type": string,
      "location": string or null,
      "start_date": string,
      "end_date": string or null,
      "is_current": boolean,
      "bullet_points": [string]
    }}
  ],
  "certifications": [
    {{
      "name": string,
      "issuer": string,
      "issue_date": string,
      "expiry_date": string or null,
      "credential_id": string or null,
      "credential_url": string or null
    }}
  ],
  "achievements": [
    {{
      "title": string,
      "issuer": string or null,
      "date": string or null,
      "description": string
    }}
  ],
  "publications": [
    {{
      "title": string,
      "publisher": string or null,
      "publication_date": string or null,
      "url": string or null,
      "description": string or null
    }}
  ],
  "languages": [
    {{
      "language": string,
      "proficiency": string
    }}
  ],
  "extra_activities": [
    {{
      "title": string,
      "organization": string or null,
      "role": string or null,
      "start_date": string or null,
      "end_date": string or null,
      "description": string
    }}
  ]
}}
"""

JD_ANALYSIS_PROMPT = """
You are a senior technical hiring manager and ATS optimization specialist.
Analyze the following Job Description (JD) and extract the key target criteria into structured JSON.

STRICT INSTRUCTIONS:
1. Extract the primary role title, target company (if mentioned), and expected seniority level.
2. Differentiate strictly between "required_skills" (must-haves) and "preferred_skills" (nice-to-haves/pluses).
3. Identify relevant keywords, tools/technologies, and core day-to-day responsibilities.
4. Provide a 2-3 sentence summary of what this role seeks.

Job Description:
{jd_text}

Respond ONLY with a valid JSON object matching this schema:
{{
  "role_title": string,
  "company": string or null,
  "seniority_level": string,
  "required_skills": [string],
  "preferred_skills": [string],
  "keywords": [string],
  "tools_and_technologies": [string],
  "key_responsibilities": [string],
  "summary_requirements": string
}}
"""

PORTFOLIO_MATCH_PROMPT = """
You are an unbiased ATS scoring engine and candidate evaluation analyst.
Compare the candidate's verified portfolio against the target Job Description (JD).

CRITICAL ANTI-HALLUCINATION RULES:
1. You may ONLY reference and score items that exist in the provided Candidate Portfolio.
2. Every ranked project, experience, and certification MUST reference its exact integer `id` from the portfolio. Never invent an ID.
3. Compute an objective match score (0 to 100) reflecting skill alignment, seniority, and domain relevance.
4. Categorize candidate skills into:
   - `matched_skills`: Skills the candidate possesses that are explicitly requested or relevant to the JD.
   - `missing_skills`: Skills requested by the JD that the candidate DOES NOT currently list in their verified portfolio.
5. Rank projects, experience, and certifications by relevance, providing a concise justification explaining why they matter for this specific role.

Candidate Portfolio:
{portfolio_json}

Target Job Description:
{jd_text}

Respond ONLY with a valid JSON object matching this schema:
{{
  "match_score": number (0-100),
  "score_breakdown": {{
    "skills_alignment": number (0-100),
    "experience_relevance": number (0-100),
    "domain_and_tool_overlap": number (0-100)
  }},
  "matched_skills": [
    {{
      "id": integer,
      "name": string,
      "relevance": "critical" | "high" | "medium"
    }}
  ],
  "missing_skills": [string],
  "ranked_projects": [
    {{
      "id": integer,
      "title": string,
      "relevance_rank": integer,
      "relevance_score": number (0-100),
      "reason": string
    }}
  ],
  "ranked_experience": [
    {{
      "id": integer,
      "company": string,
      "role": string,
      "relevance_rank": integer,
      "relevance_score": number (0-100),
      "reason": string
    }}
  ],
  "ranked_certifications": [
    {{
      "id": integer,
      "name": string,
      "relevance_rank": integer,
      "reason": string
    }}
  ],
  "recommended_summary": string,
  "key_tailoring_advice": [string]
}}
"""

BULLET_REPHRASE_PROMPT = """
You are an ATS resume editor.
Rephrase the candidate's existing accomplishment bullet point to align with the target job keywords and emphasize high-impact action verbs.

ABSOLUTE ZERO-HALLUCINATION GUARDRAILS:
1. DO NOT change, invent, or extrapolate any numbers, metrics, percentages, volume metrics, or quantitative results.
2. DO NOT introduce new technologies, programming languages, or tools that were not in the original bullet point or the candidate's verified skill list.
3. DO NOT change the company, role, or factual premise.
4. Only reword the sentence structure and strengthen action verbs (e.g., "Led", "Engineered", "Orchestrated").

Original Bullet Point:
"{original_bullet}"

Target Job Role / Keywords:
"{keywords}"

Allowed Verified Skills for this candidate:
{verified_skills}

Respond ONLY with a valid JSON object:
{{
  "rephrased_bullet": string,
  "confidence_score": number (0.0 to 1.0),
  "preserved_metrics": [string],
  "changes_made": string
}}
"""
