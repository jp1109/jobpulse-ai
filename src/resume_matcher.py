
import re
import fitz
import pandas as pd

SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b",
    "Excel": r"\bexcel\b",
    "Tableau": r"\btableau\b",
    "Power BI": r"\bpower\s*bi\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "Azure": r"\bazure\b",
    "GCP": r"\bgcp\b|\bgoogle cloud\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b",
    "Spark": r"\b(?:apache\s+)?spark\b|\bpyspark\b",
    "Machine Learning": r"\bmachine learning\b",
    "NLP": r"\bnlp\b|\bnatural language processing\b",
    "TensorFlow": r"\btensorflow\b",
    "PyTorch": r"\bpytorch\b",
    "Java": r"\bjava\b",
    "JavaScript": r"\bjavascript\b",
    "React": r"\breact(?:\.js)?\b",
    "Git": r"\bgit\b",
}


def extract_resume_text(pdf_bytes):
    """Extract selectable text from a PDF resume."""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def extract_skills(text):
    """Find known technical skills in text."""
    if not text:
        return set()

    return {
        skill
        for skill, pattern in SKILL_PATTERNS.items()
        if re.search(pattern, str(text), re.IGNORECASE)
    }


def parse_job_skills(value):
    """Convert stored comma-separated skills to a set."""
    if pd.isna(value) or not str(value).strip():
        return set()

    return {
        skill.strip()
        for skill in str(value).split(",")
        if skill.strip()
    }


def calculate_match(resume_skills, job_skills):
    """Calculate required-skill coverage."""
    if not job_skills:
        return None, set(), set()

    matched = resume_skills.intersection(job_skills)
    missing = job_skills.difference(resume_skills)

    score = round(100 * len(matched) / len(job_skills), 1)

    return score, matched, missing


def rank_jobs(df, resume_skills):
    """Rank postings with detectable skills."""
    results = []

    for _, job in df.iterrows():
        job_skills = parse_job_skills(
            job.get("skills", "")
        )

        score, matched, missing = calculate_match(
            resume_skills, job_skills
        )

        if score is None:
            continue

        results.append({
            "job_title": job.get("job_title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "match_score": score,
            "matched_skills": ", ".join(sorted(matched)),
            "missing_skills": ", ".join(sorted(missing)),
            "job_url": job.get("job_url", "")
        })

    if not results:
        return pd.DataFrame(columns=[
            "job_title", "company", "location",
            "match_score", "matched_skills",
            "missing_skills", "job_url"
        ])

    return (
        pd.DataFrame(results)
        .sort_values("match_score", ascending=False)
        .reset_index(drop=True)
    )