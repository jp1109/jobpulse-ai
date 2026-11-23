
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Project setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.resume_matcher import (
    extract_resume_text,
    extract_skills,
    rank_jobs,
)

from src.semantic_matcher import (
    load_model,
    calculate_semantic_matches,
)

DB_FILE = PROJECT_ROOT / "data" / "jobpulse.db"
DEMO_FILE = PROJECT_ROOT / "data" / "demo_jobs.csv"


@st.cache_data(ttl=300)
def load_job_data(db_path, demo_path):
    db_file = Path(db_path)
    demo_file = Path(demo_path)

    if db_file.exists():
        try:
            with sqlite3.connect(db_file) as conn:
                jobs = pd.read_sql_query(
                    "SELECT * FROM jobs", conn
                )
            return jobs, "Local SQLite database"
        except (sqlite3.Error, OSError):
            pass

    if demo_file.exists():
        jobs = pd.read_csv(demo_file)
        return jobs, "Historical demo dataset"

    return pd.DataFrame(), "No dataset available"


st.title("🎯 AI Resume Matcher")

st.write(
    "Upload your resume and discover which collected "
    "job postings overlap with your technical skills."
)

st.info(
    "Match scores are based on available job information. "
    "They are not hiring probabilities."
)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF)",
    type=["pdf"],
)

if uploaded_file is not None:

    try:
        resume_text = extract_resume_text(uploaded_file)
    except Exception as exc:
        st.error(f"Unable to read PDF: {exc}")
        st.stop()

    if not resume_text or not resume_text.strip():
        st.warning(
            "No readable text was found in this PDF."
        )
        st.stop()

    resume_skills = extract_skills(resume_text)

    st.subheader("Skills Found in Your Resume")

    if resume_skills:
        st.success(", ".join(sorted(resume_skills)))
    else:
        st.warning("No supported technical skills detected.")

    st.metric(
        "Detected Resume Skills",
        len(resume_skills),
    )

    jobs_df, source_label = load_job_data(
        str(DB_FILE),
        str(DEMO_FILE),
    )

    if jobs_df.empty:
        st.error(
            "No job postings available. "
            "Check data/demo_jobs.csv."
        )
        st.stop()

    st.caption(f"Data source: {source_label}")
    st.caption(f"Loaded {len(jobs_df)} job postings")

    st.divider()

    # Keyword matching
    st.subheader("🔎 Skill-Based Job Matching")

    if resume_skills:
        try:
            ranked_jobs = rank_jobs(
                jobs_df,
                resume_skills,
            )

            if ranked_jobs.empty:
                st.info("No matching jobs found.")
            else:
                st.dataframe(
                    ranked_jobs.head(20),
                    width="stretch",
                    hide_index=True,
                )

                st.download_button(
                    "Download Skill Matches",
                    data=ranked_jobs.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="jobpulse_skill_matches.csv",
                    mime="text/csv",
                )

        except (KeyError, ValueError, TypeError) as exc:
            st.error(f"Skill matching error: {exc}")

    st.divider()

    # Semantic matching
    st.subheader("🧠 Semantic AI Matching")

    st.write(
        "Compare the meaning of your resume with "
        "the available job information using "
        "sentence embeddings."
    )

    if st.button(
        "Run AI Semantic Matching",
        type="primary",
    ):

        try:
            with st.spinner(
                "Analyzing resume and job similarity..."
            ):

                model = load_model()

                semantic_results = (
                    calculate_semantic_matches(
                        resume_text,
                        jobs_df,
                        model,
                    )
                )

            if semantic_results is None or semantic_results.empty:
                st.warning(
                    "No semantic matching results available."
                )
            else:
                st.success(
                    "Semantic matching completed!"
                )

                st.dataframe(
                    semantic_results.head(20),
                    width="stretch",
                    hide_index=True,
                )

                st.download_button(
                    "Download Semantic Matches",
                    data=semantic_results.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="jobpulse_semantic_matches.csv",
                    mime="text/csv",
                )

        except Exception as exc:
            st.error(
                f"Semantic matching failed: {exc}"
            )

else:
    st.info(
        "Upload a PDF resume to begin matching."
    )
