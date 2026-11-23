
from pathlib import Path
from collections import Counter
import ast
import json
import re
import sqlite3
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.resume_matcher import (
    extract_resume_text,
    extract_skills,
)

DB_FILE = ROOT / "data" / "jobpulse.db"
CSV_FILE = ROOT / "data" / "demo_jobs.csv"

st.set_page_config(
    page_title="Resume Analysis Hub",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 Resume Analysis Hub")

st.write(
    "Upload your resume once to explore detected "
    "skills, job-market coverage, and potential gaps."
)

st.caption(
    "This tool uses keyword-based analysis and "
    "historical sample job data. It does not "
    "predict hiring outcomes."
)


@st.cache_data(ttl=300)
def load_jobs():
    if DB_FILE.exists():
        try:
            with sqlite3.connect(DB_FILE) as conn:
                return pd.read_sql_query(
                    "SELECT * FROM jobs",
                    conn,
                )
        except Exception:
            pass

    if CSV_FILE.exists():
        return pd.read_csv(CSV_FILE)

    return pd.DataFrame()


def parse_skills(value):
    if isinstance(value, (list, tuple, set)):
        return {
            str(s).strip().casefold()
            for s in value
            if str(s).strip()
        }

    if value is None:
        return set()

    if not isinstance(value, str):
        if pd.isna(value):
            return set()
        value = str(value)

    value = value.strip()

    if not value:
        return set()

    if value.startswith("["):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                parsed = None

        if isinstance(parsed, list):
            return parse_skills(parsed)

    return {
        s.strip().casefold()
        for s in re.split(r"[,;|]", value)
        if s.strip()
    }


jobs = load_jobs()

if jobs.empty:
    st.error("No job data available.")
    st.stop()

skill_col = next(
    (
        c for c in [
            "skills",
            "detected_skills",
            "required_skills",
        ]
        if c in jobs.columns
    ),
    None,
)

if skill_col is None:
    st.error(
        "No supported skill column found "
        "in the jobs dataset."
    )
    st.stop()

uploaded_file = st.file_uploader(
    "Upload your PDF resume",
    type=["pdf"],
)

if uploaded_file is None:
    st.info("Upload a resume to start the analysis.")
    st.stop()

try:
    resume_text = extract_resume_text(
        uploaded_file.getvalue()
    )
except Exception as exc:
    st.error(f"Could not process the PDF: {exc}")
    st.stop()

if not resume_text or not resume_text.strip():
    st.warning(
        "No readable resume text found. "
        "Try a text-based PDF."
    )
    st.stop()

resume_skills = {
    str(s).strip().casefold()
    for s in extract_skills(resume_text)
    if str(s).strip()
}

st.subheader("1. Resume Skills")

if resume_skills:
    st.write(", ".join(sorted(resume_skills)))
else:
    st.warning("No supported resume skills detected.")

st.divider()

st.subheader("2. Select Job Categories")

if "role_category" in jobs.columns:
    categories = sorted(
        jobs["role_category"]
        .dropna()
        .astype(str)
        .unique()
    )

    selected = st.multiselect(
        "Categories",
        categories,
        default=categories,
    )

    jobs = jobs[
        jobs["role_category"]
        .astype(str)
        .isin(selected)
    ]

if jobs.empty:
    st.warning("No jobs match your selection.")
    st.stop()

job_skill_sets = jobs[skill_col].apply(parse_skills)

skill_counts = Counter()

for skills in job_skill_sets:
    skill_counts.update(skills)

market_skills = set(skill_counts)
matched = resume_skills & market_skills
missing = market_skills - resume_skills

coverage = (
    len(matched) / len(market_skills) * 100
    if market_skills else 0
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Resume Skills", len(resume_skills))
col2.metric("Jobs Analyzed", len(jobs))
col3.metric("Matched Skills", len(matched))
col4.metric("Potential Gaps", len(missing))

st.divider()

st.subheader("3. Skill Coverage")

st.progress(
    min(max(coverage / 100, 0.0), 1.0)
)

st.write(
    f"{coverage:.1f}% of distinct skills "
    "mentioned in the selected job dataset "
    "were detected in your resume."
)

st.caption(
    "This measures unique-skill overlap across "
    "all selected postings, not a match score "
    "for an individual job."
)

left, right = st.columns(2)

with left:
    st.subheader("Matched Skills")
    if matched:
        st.success(", ".join(sorted(matched)))
    else:
        st.info("No matching skills detected.")

with right:
    st.subheader("Potential Missing Skills")
    if missing:
        top_missing = sorted(
            missing,
            key=lambda s: (-skill_counts[s], s),
        )[:15]

        st.warning(", ".join(top_missing))
    else:
        st.success("No additional skills detected.")

st.divider()

st.subheader("4. Skill Gap Priorities")

gap_df = pd.DataFrame(
    [
        {
            "Skill": skill,
            "Jobs Mentioning Skill": skill_counts[skill],
            "Demand %": round(
                skill_counts[skill] / len(jobs) * 100,
                1,
            ),
        }
        for skill in missing
    ]
)

if not gap_df.empty:
    gap_df = gap_df.sort_values(
        "Jobs Mentioning Skill",
        ascending=False,
    )

    st.dataframe(
        gap_df,
        hide_index=True,
        width="stretch",
    )

    st.download_button(
        "Download Skill Gap Report",
        gap_df.to_csv(index=False),
        file_name="jobpulse_analysis.csv",
        mime="text/csv",
    )
else:
    st.info("No potential gaps found.")

st.divider()

st.subheader("5. Continue Your Analysis")

st.write(
    "Use Resume Matcher to explore individual "
    "job matches, and Resume Improvement to "
    "rewrite bullet points based on your "
    "verified experience."
)

st.page_link(
    "pages/1_Resume_Matcher.py",
    label="Open Resume Matcher",
    icon="🔍",
)

st.page_link(
    "pages/4_Resume_Improvement.py",
    label="Open Resume Improvement",
    icon="✨",
)

# ==========================================
# 6. JOB-SPECIFIC MATCH REPORT
# ==========================================

st.divider()
st.subheader("6. Job-Specific Match Report")

st.write(
    "Select an individual job to compare its "
    "detected skills against your resume."
)

# Use the already-filtered jobs dataframe
report_jobs = jobs.reset_index(drop=True).copy()

# Create readable job labels
title_col = next(
    (c for c in ["title", "job_title", "position"]
     if c in report_jobs.columns),
    None,
)

company_col = next(
    (c for c in ["company", "company_name"]
     if c in report_jobs.columns),
    None,
)

def make_job_label(row):
    title = (
        str(row[title_col])
        if title_col else "Untitled Job"
    )
    company = (
        str(row[company_col])
        if company_col else "Unknown Company"
    )
    return f"{title} — {company}"

report_jobs["display_label"] = report_jobs.apply(
    make_job_label,
    axis=1,
)

# Include an index to distinguish duplicate titles
report_jobs["display_label"] = [
    f"{i + 1}. {label}"
    for i, label in enumerate(
        report_jobs["display_label"]
    )
]

selected_index = st.selectbox(
    "Choose a job",
    options=list(range(len(report_jobs))),
    format_func=lambda i: (
        report_jobs.iloc[i]["display_label"]
    ),
)

selected_job = report_jobs.iloc[selected_index]

selected_job_skills = parse_skills(
    selected_job[skill_col]
)

matched_job_skills = (
    resume_skills & selected_job_skills
)

missing_job_skills = (
    selected_job_skills - resume_skills
)

match_score = (
    len(matched_job_skills)
    / len(selected_job_skills) * 100
    if selected_job_skills else 0
)

st.divider()

st.subheader("Job Match Results")

st.metric(
    "Detected Skill Match",
    f"{match_score:.1f}%",
)

st.progress(
    min(max(match_score / 100, 0.0), 1.0)
)

st.caption(
    "This percentage measures detected skill "
    "overlap only. It is not a hiring probability."
)

left_col, right_col = st.columns(2)

with left_col:
    st.markdown("#### Matching Skills")

    if matched_job_skills:
        st.success(
            ", ".join(sorted(matched_job_skills))
        )
    else:
        st.info(
            "No matching skills detected."
        )

with right_col:
    st.markdown("#### Skills Not Detected")

    if missing_job_skills:
        st.warning(
            ", ".join(sorted(missing_job_skills))
        )
    else:
        st.success(
            "All listed skills were detected."
        )

st.divider()

st.subheader("Resume Improvement Guidance")

if matched_job_skills:
    st.write(
        "Consider highlighting relevant projects "
        "where you demonstrated these skills:"
    )

    st.write(
        ", ".join(sorted(matched_job_skills))
    )

if missing_job_skills:
    st.write(
        "Review the following skills mentioned "
        "in the selected posting:"
    )

    st.write(
        ", ".join(sorted(missing_job_skills))
    )

    st.info(
        "If you already have experience with "
        "these skills, consider describing it "
        "more clearly in your resume. "
        "Otherwise, treat them as possible "
        "learning priorities."
    )

if not selected_job_skills:
    st.warning(
        "No skills were detected for this job, "
        "so a meaningful match score cannot "
        "be calculated."
    )

# Downloadable job-specific report
report_text = f"""
JOBPULSE AI - JOB MATCH REPORT

Job: {selected_job["display_label"]}

Detected Skill Match: {match_score:.1f}%

Matching Skills:
{", ".join(sorted(matched_job_skills)) or "None"}

Skills Not Detected:
{", ".join(sorted(missing_job_skills)) or "None"}

Note:
This report uses keyword-based skill overlap.
It does not predict hiring outcomes.
"""

st.download_button(
    "Download Job Match Report",
    data=report_text,
    file_name="jobpulse_job_match_report.txt",
    mime="text/plain",
)
