
import re
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Resume Improvement Assistant",
    page_icon="✨",
    layout="wide",
)

st.title("✨ Resume Improvement Assistant")

st.write(
    "Review resume bullet points and get practical "
    "suggestions for clearer, more impactful writing."
)

st.info(
    "This version uses transparent writing rules, "
    "not a generative AI model. Always verify "
    "suggestions before using them."
)

WEAK_PHRASES = {
    "responsible for": "Describe the action you took",
    "worked on": "Specify what you built or improved",
    "helped with": "Explain your contribution",
    "involved in": "Describe your individual role",
    "familiar with": "Demonstrate the skill through a project",
}

ACTION_VERBS = [
    "analyzed", "built", "developed", "designed",
    "implemented", "automated", "optimized",
    "created", "improved", "evaluated",
    "validated", "integrated", "deployed",
    "maintained", "collaborated", "led",
]

def review_bullet(text):
    suggestions = []
    lower = text.lower()

    if len(text.split()) < 10:
        suggestions.append(
            "Add context about the task, tools, "
            "or business purpose."
        )

    if len(text.split()) > 35:
        suggestions.append(
            "Consider shortening this bullet "
            "to improve readability."
        )

    for phrase, advice in WEAK_PHRASES.items():
        if phrase in lower:
            suggestions.append(
                f"Replace '{phrase}': {advice}."
            )

    if not any(
        re.search(r"\b" + verb + r"\b", lower)
        for verb in ACTION_VERBS
    ):
        suggestions.append(
            "Consider starting with a strong, "
            "accurate action verb."
        )

    if not re.search(r"\d", text):
        suggestions.append(
            "If you have a verified metric, "
            "consider adding it. Do not invent numbers."
        )

    if not suggestions:
        suggestions.append(
            "This bullet has a solid structure. "
            "Check that the details are specific "
            "and factually accurate."
        )

    return suggestions


def create_template(text):
    lower = text.lower()

    if "responsible for" in lower:
        return (
            "Action verb + specific responsibility "
            "+ tools or methods + outcome"
        )

    if "worked on" in lower or "helped with" in lower:
        return (
            "Describe what you personally did "
            "+ how you did it + why it mattered"
        )

    return (
        "Action + task or project + tools "
        "+ measurable outcome (if verified)"
    )


st.subheader("1. Enter a Resume Bullet")

bullet = st.text_area(
    "Paste one resume bullet point",
    placeholder=(
        "Example: Worked on Python and SQL "
        "for data analysis projects."
    ),
    height=130,
)

st.subheader("2. Select Target Role")

role = st.selectbox(
    "Target job role",
    [
        "Data Analyst",
        "Data Scientist",
        "Data Engineer",
        "AI/ML Engineer",
        "Business Intelligence Analyst",
        "Software Engineer",
    ],
)

if st.button(
    "Analyze Resume Bullet",
    type="primary",
):
    if not bullet.strip():
        st.warning(
            "Please enter a resume bullet first."
        )
    else:
        st.subheader("Writing Feedback")

        suggestions = review_bullet(bullet)

        for suggestion in suggestions:
            st.write("•", suggestion)

        st.subheader("Recommended Structure")
        st.success(create_template(bullet))

        st.subheader("Role-Specific Guidance")

        role_guidance = {
            "Data Analyst": (
                "Highlight SQL, reporting, dashboards, "
                "data cleaning, and business insights."
            ),
            "Data Scientist": (
                "Highlight modeling, experimentation, "
                "evaluation, and statistical analysis."
            ),
            "Data Engineer": (
                "Highlight pipelines, ETL, data quality, "
                "cloud platforms, and orchestration."
            ),
            "AI/ML Engineer": (
                "Highlight model development, APIs, "
                "deployment, evaluation, and monitoring."
            ),
            "Business Intelligence Analyst": (
                "Highlight dashboards, KPI definitions, "
                "SQL, and stakeholder reporting."
            ),
            "Software Engineer": (
                "Highlight implementation, testing, "
                "APIs, architecture, and reliability."
            ),
        }

        st.write(role_guidance[role])

        st.caption(
            "Mention technologies only if you "
            "actually used them."
        )

st.divider()

st.subheader("3. Resume Bullet Checklist")

st.checkbox("Starts with a clear action verb")
st.checkbox("Explains what I personally contributed")
st.checkbox("Mentions relevant tools when appropriate")
st.checkbox("Explains the outcome or business value")
st.checkbox("Includes only verified achievements")

st.caption(
    "JobPulse AI — Resume Improvement Assistant v1"
)
