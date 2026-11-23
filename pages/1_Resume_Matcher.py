from src.semantic_matcher import (
    load_model,
    calculate_semantic_matches
)
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.resume_matcher import (
    extract_resume_text,
    extract_skills,
    rank_jobs
)

DB_FILE = PROJECT_ROOT / "data" / "jobpulse.db"

st.set_page_config(
    page_title="Resume Matcher | JobPulse AI",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 AI Resume Matcher")
st.write(
    "Upload your resume and discover which collected "
    "job postings overlap with your technical skills."
)

st.info(
    "Scores are based on detected skills in job tags, "
    "not full job requirements or hiring probabilities."
)

uploaded_file = st.file_uploader(
    "Upload your resume (PDF)",
    type=["pdf"]
)

if uploaded_file is not None:

    try:
        resume_text = extract_resume_text(
            uploaded_file.getvalue()
        )
    except Exception as exc:
        st.error(f"Unable to read this PDF: {exc}")
        st.stop()

    if not resume_text.strip():
        st.warning(
            "No selectable text was found. "
            "Scanned PDFs are not yet supported."
        )
        st.stop()

    resume_skills = extract_skills(resume_text)

    st.subheader("Skills Found in Your Resume")

    if resume_skills:
        st.success(", ".join(sorted(resume_skills)))
    else:
        st.warning("No skills matched our current dictionary.")

    st.metric("Detected Resume Skills", len(resume_skills))

    if not DB_FILE.exists():
        st.error("Job database not found.")
        st.stop()

    with sqlite3.connect(DB_FILE) as conn:
        jobs_df = pd.read_sql_query(
            "SELECT * FROM jobs", conn
        )

    ranked_df = rank_jobs(jobs_df, resume_skills)


    st.divider()
    st.subheader("🧠 Semantic AI Matching")

    if st.button("Run AI Semantic Matching"):

        with st.spinner(
            "Analyzing resume and job similarity..."
        ):
            model = get_embedding_model()

            semantic_results = calculate_semantic_matches(
                resume_text,
                jobs_df,
                model
            )

        if semantic_results.empty:
            st.warning(
                "No suitable job text is available "
                "for semantic comparison."
            )
        else:
            st.success("Semantic matching complete!")

            for _, job in semantic_results.head(10).iterrows():

                with st.container(border=True):
                    st.markdown(
                        f"### {job['job_title']}"
                    )

                    st.write(
                        f"**Company:** {job['company']}"
                    )

                    st.write(
                        f"**Location:** {job['location']}"
                    )

                    st.metric(
                        "Cosine Similarity",
                        f"{job['semantic_similarity']:.3f}"
                    )

                    st.caption(
                        "Similarity is not a hiring "
                        "probability or eligibility score."
                    )


    st.divider()
    st.subheader("Your Top Job Matches")

    if ranked_df.empty:
        st.warning(
            "No postings with detectable technical "
            "skills were found."
        )
    else:
        top_jobs = ranked_df.head(20)

        for _, job in top_jobs.iterrows():

            with st.container(border=True):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"### {job['job_title']}"
                    )
                    st.write(
                        f"**Company:** {job['company']}"
                    )
                    st.write(
                        f"**Location:** {job['location']}"
                    )

                with col2:
                    st.metric(
                        "Skill Overlap",
                        f"{job['match_score']:.1f}%"
                    )

                st.progress(
                    float(job["match_score"]) / 100
                )

                st.write(
                    "**Matched skills:**",
                    job["matched_skills"] or "None"
                )

                st.write(
                    "**Missing skills:**",
                    job["missing_skills"] or "None"
                )

                if pd.notna(job["job_url"]) and str(
                    job["job_url"]
                ).startswith(("https://", "http://")):
                    st.link_button(
                        "View Job Posting",
                        str(job["job_url"])
                    )

        st.download_button(
            "Download Match Results",
            data=ranked_df.to_csv(index=False),
            file_name="jobpulse_resume_matches.csv",
            mime="text/csv"
        )

@st.cache_resource
def get_embedding_model():
    return load_model()
