
from pathlib import Path
from collections import Counter
import sqlite3
import re

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_FILE = PROJECT_ROOT / "data" / "jobpulse.db"
DEMO_FILE = PROJECT_ROOT / "data" / "demo_jobs.csv"

st.title("📊 Skill Demand Intelligence")
st.write(
    "Explore technical skills mentioned in collected "
    "job postings and identify recurring requirements."
)

st.info(
    "This analysis uses a limited historical dataset. "
    "Results are not representative of the entire job market."
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


jobs = load_jobs()

if jobs.empty:
    st.error("No job data available.")
    st.stop()

# Find the column containing skills
skill_column = next(
    (
        col for col in [
            "detected_skills",
            "required_skills",
            "skills",
            "tags",
        ]
        if col in jobs.columns
    ),
    None,
)

if skill_column is None:
    st.error("No skill column found in the dataset.")
    st.stop()


def parse_skills(value):
    if pd.isna(value):
        return []

    return [
        skill.strip()
        for skill in re.split(r"[,;|]", str(value))
        if skill.strip()
    ]


# Count each skill once per job
skill_counter = Counter()

for value in jobs[skill_column]:
    unique_skills = set(parse_skills(value))
    skill_counter.update(unique_skills)

skill_df = pd.DataFrame(
    skill_counter.items(),
    columns=["Skill", "Job Count"],
)

if skill_df.empty:
    st.warning("No skills detected.")
    st.stop()

skill_df = skill_df.sort_values(
    "Job Count",
    ascending=False,
)

skill_df["Demand %"] = (
    skill_df["Job Count"] / len(jobs) * 100
).round(1)

# Summary metrics
col1, col2, col3 = st.columns(3)

col1.metric("Jobs Analyzed", len(jobs))
col2.metric("Unique Skills", len(skill_df))
col3.metric("Most Mentioned Skill", skill_df.iloc[0]["Skill"])

st.divider()

st.subheader("🔥 Top Technical Skills")

top_n = st.slider(
    "Number of skills to display",
    min_value=5,
    max_value=min(30, max(5, len(skill_df))),
    value=min(10, max(5, len(skill_df))),
)

top_skills = skill_df.head(top_n)

fig = px.bar(
    top_skills,
    x="Job Count",
    y="Skill",
    orientation="h",
    title="Most Frequently Mentioned Skills",
    text="Job Count",
)

fig.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    }
)

st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("📋 Skill Demand Table")

st.dataframe(
    skill_df,
    width="stretch",
    hide_index=True,
)

st.download_button(
    "Download Skill Demand Report",
    data=skill_df.to_csv(index=False).encode("utf-8"),
    file_name="jobpulse_skill_demand.csv",
    mime="text/csv",
)

st.caption(
    "Demand percentage = postings mentioning a skill "
    "divided by total postings analyzed."
)
