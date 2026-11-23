
from pathlib import Path
from collections import Counter
import sqlite3
import sys
import re

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.resume_matcher import (
    extract_resume_text,
    extract_skills,
)

DB_FILE = ROOT / "data" / "jobpulse.db"
DEMO_FILE = ROOT / "data" / "demo_jobs.csv"

st.title("🎯 Personalized Skill Gap Analyzer")

st.write(
    "Upload your resume to identify technical skills "
    "mentioned in job postings but not detected "
    "in your resume."
)

st.info(
    "Skill gaps are based on keyword detection. "
    "A missing skill does not necessarily mean "
    "you lack that experience."
)


@st.cache_data(ttl=300)
def load_jobs():
    if DB_FILE.exists():
        with sqlite3.connect(DB_FILE) as conn:
            return pd.read_sql_query(
                "SELECT * FROM jobs", conn
            )

    if DEMO_FILE.exists():
        return pd.read_csv(DEMO_FILE)

    return pd.DataFrame()


def parse_skills(value):
    if value is None:
        return set()

    if isinstance(value, (list, tuple, set)):
        return {
            str(skill).strip()
            for skill in value
            if str(skill).strip()
        }

    if pd.isna(value):
        return set()

    return {
        skill.strip()
        for skill in re.split(r"[,;|]", str(value))
        if skill.strip()
    }


jobs = load_jobs()

if jobs.empty:
    st.error("No job postings available.")
    st.stop()

if "skills" not in jobs.columns:
    st.error("The dataset has no skills column.")
    st.stop()

jobs["parsed_skills"] = jobs["skills"].apply(parse_skills)

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf"],
)

if uploaded_file is not None:

    try:
        resume_text = extract_resume_text(
            uploaded_file.getvalue()
        )
    except Exception as exc:
        st.error(f"Could not read PDF: {exc}")
        st.stop()

    resume_skills = extract_skills(resume_text)

    if not resume_text.strip():
        st.warning("No readable text found.")
        st.stop()

    st.subheader("Skills Detected in Your Resume")

    if resume_skills:
        st.success(", ".join(sorted(resume_skills)))
    else:
        st.warning("No supported skills detected.")

    st.metric(
        "Detected Resume Skills",
        len(resume_skills),
    )

    st.divider()

    st.subheader("Select Jobs to Analyze")

    if "role_category" in jobs.columns:
        categories = sorted(
            jobs["role_category"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        selected = st.multiselect(
            "Job categories",
            options=categories,
            default=categories,
        )

        selected_jobs = jobs[
            jobs["role_category"].astype(str).isin(
                selected
            )
        ]
    else:
        selected_jobs = jobs.copy()

    st.caption(
        f"Analyzing {len(selected_jobs)} job postings"
    )

    if selected_jobs.empty:
        st.warning("No jobs match the selected filters.")
        st.stop()

    # Normalize capitalization to avoid duplicate names
    resume_normalized = {
        skill.casefold()
        for skill in resume_skills
    }

    skill_counts = Counter()

    for skills in selected_jobs["parsed_skills"]:
        for skill in skills:
            skill_counts[skill.casefold()] += 1

    missing_rows = []

    for skill, count in skill_counts.items():
        if skill not in resume_normalized:
            missing_rows.append({
                "Skill": skill.title(),
                "Jobs Mentioning Skill": count,
                "Demand %": round(
                    count / len(selected_jobs) * 100,
                    1
                ),
            })

    gap_df = pd.DataFrame(
        missing_rows,
        columns=[
            "Skill",
            "Jobs Mentioning Skill",
            "Demand %",
        ],
    )

    gap_df = gap_df.sort_values(
        "Jobs Mentioning Skill",
        ascending=False,
    )

    st.divider()
    st.subheader("Potential Skill Gaps")

    if gap_df.empty:
        st.success(
            "No additional skills detected "
            "in the selected job postings."
        )
    else:
        col1, col2 = st.columns(2)

        col1.metric(
            "Potential Skill Gaps",
            len(gap_df),
        )

        col2.metric(
            "Jobs Analyzed",
            len(selected_jobs),
        )

        top_gaps = gap_df.head(15)

        fig = px.bar(
            top_gaps,
            x="Jobs Mentioning Skill",
            y="Skill",
            orientation="h",
            title="Most Frequently Mentioned Missing Skills",
            text="Jobs Mentioning Skill",
        )

        fig.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            }
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

        st.dataframe(
            gap_df,
            width="stretch",
            hide_index=True,
        )

        st.download_button(
            "Download Skill Gap Report",
            data=gap_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="jobpulse_skill_gaps.csv",
            mime="text/csv",
        )

        st.caption(
            "These are potential learning priorities, "
            "not verified qualifications or hiring "
            "requirements."
        )

else:
    st.info(
        "Upload a PDF resume to begin your skill gap analysis."
    )
