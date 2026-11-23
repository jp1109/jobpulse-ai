
from pathlib import Path
import sqlite3
from collections import Counter

import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------------
# PAGE CONFIGURATION
# ------------------------------------

st.set_page_config(
    page_title="JobPulse AI",
    page_icon="📊",
    layout="wide"
)


PROJECT_ROOT = Path(__file__).resolve().parent
DB_FILE = PROJECT_ROOT / "data" / "jobpulse.db"
DEMO_FILE = PROJECT_ROOT / "data" / "demo_jobs.csv"


@st.cache_data(ttl=300)
def load_jobs(source_path, source_mtime):
    path = Path(source_path)

    if path.suffix == ".db":
        with sqlite3.connect(path) as conn:
            return pd.read_sql_query(
                "SELECT * FROM jobs", conn
            )

    return pd.read_csv(path)


if DB_FILE.exists():
    source_file = DB_FILE
    source_label = "Local SQLite database"
elif DEMO_FILE.exists():
    source_file = DEMO_FILE
    source_label = "Historical demo dataset"
else:
    st.error("No job data available.")
    st.stop()

try:
    df = load_jobs(
        str(source_file),
        source_file.stat().st_mtime
    )
except (sqlite3.Error, pd.errors.DatabaseError, OSError) as exc:
    st.error(f"Unable to load job data: {exc}")
    st.stop()

st.caption(f"Data source: {source_label}")

if df.empty:
    st.warning("No job records available.")
    st.stop()


# ------------------------------------
# SIDEBAR FILTERS
# ------------------------------------

st.sidebar.header("🔎 Filter Jobs")

roles = sorted(
    df["role_category"].dropna().unique().tolist()
)

selected_roles = st.sidebar.multiselect(
    "Select job roles",
    options=roles,
    default=roles
)

filtered_df = df[
    df["role_category"].isin(selected_roles)
].copy()

work_options = ["All", "Remote", "Non-remote", "Unknown"]

work_filter = st.sidebar.selectbox(
    "Work arrangement",
    work_options
)

remote_values = (
    pd.to_numeric(filtered_df["remote"], errors="coerce")
)

if work_filter == "Remote":
    filtered_df = filtered_df[remote_values == 1]
elif work_filter == "Non-remote":
    filtered_df = filtered_df[remote_values == 0]
elif work_filter == "Unknown":
    filtered_df = filtered_df[remote_values.isna()]

search = st.sidebar.text_input(
    "Search job title or company"
)

if search:
    mask = (
        filtered_df["job_title"].fillna("")
        .str.contains(search, case=False, regex=False)
        |
        filtered_df["company"].fillna("")
        .str.contains(search, case=False, regex=False)
    )
    filtered_df = filtered_df[mask]

st.sidebar.divider()
st.sidebar.caption(
    "Source: Arbeitnow API | Collected sample, "
    "not a representative US labor-market survey."
)

# ------------------------------------
# KPI CARDS
# ------------------------------------

total_jobs = len(filtered_df)

remote_count = int(
    (pd.to_numeric(
        filtered_df["remote"], errors="coerce"
    ) == 1).sum()
)

company_count = filtered_df["company"].nunique()

skill_counter = Counter()

for skills in filtered_df["skills"].dropna():
    for skill in str(skills).split(","):
        skill = skill.strip()
        if skill:
            skill_counter[skill] += 1

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Jobs", total_jobs)
col2.metric("Remote Jobs", remote_count)
col3.metric("Companies", company_count)
col4.metric("Detected Skills", len(skill_counter))

st.divider()

if filtered_df.empty:
    st.info("No jobs match your current filters.")
    st.stop()

# ------------------------------------
# JOB DISTRIBUTION
# ------------------------------------

st.subheader("📈 Job Opportunities by Role")

role_counts = (
    filtered_df["role_category"]
    .value_counts()
    .reset_index()
)

role_counts.columns = ["Role", "Jobs"]

fig_roles = px.bar(
    role_counts,
    x="Role",
    y="Jobs",
    color="Role",
    title="Job Postings by Category"
)

fig_roles.update_layout(showlegend=False)

st.plotly_chart(fig_roles, width="stretch")

# ------------------------------------
# TOP HIRING COMPANIES
# ------------------------------------

left, right = st.columns(2)

with left:
    st.subheader("🏢 Top Hiring Companies")

    company_counts = (
        filtered_df["company"]
        .value_counts()
        .head(10)
        .reset_index()
    )

    company_counts.columns = ["Company", "Jobs"]

    fig_companies = px.bar(
        company_counts,
        x="Jobs",
        y="Company",
        orientation="h"
    )

    fig_companies.update_layout(
        yaxis={"categoryorder": "total ascending"}
    )

    st.plotly_chart(fig_companies, width="stretch")

# ------------------------------------
# SKILL DEMAND
# ------------------------------------

with right:
    st.subheader("💻 Most Detected Skills")

    if skill_counter:
        skills_df = pd.DataFrame(
            skill_counter.most_common(10),
            columns=["Skill", "Mentions"]
        )

        fig_skills = px.bar(
            skills_df,
            x="Mentions",
            y="Skill",
            orientation="h"
        )

        fig_skills.update_layout(
            yaxis={"categoryorder": "total ascending"}
        )

        st.plotly_chart(fig_skills, width="stretch")
    else:
        st.info(
            "No technical skills were detected "
            "in the available job tags."
        )

# ------------------------------------
# JOB LISTINGS
# ------------------------------------

st.divider()

st.subheader("📋 Explore Job Listings")

display_columns = [
    "job_title",
    "company",
    "location",
    "role_category",
    "skills",
    "job_url"
]

available_columns = [
    col for col in display_columns
    if col in filtered_df.columns
]

st.dataframe(
    filtered_df[available_columns],
    width="stretch",
    hide_index=True
)

# ------------------------------------
# EXPORT DATA
# ------------------------------------

csv_data = filtered_df.to_csv(index=False)

st.download_button(
    label="⬇️ Download Filtered Job Data",
    data=csv_data,
    file_name="jobpulse_filtered_jobs.csv",
    mime="text/csv"
)

st.divider()

st.caption(
    "JobPulse AI | Python • SQL • Pandas • Plotly • Streamlit"
)
