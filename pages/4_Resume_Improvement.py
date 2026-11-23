

import re
import streamlit as st

st.set_page_config(
    page_title="Smart Resume Rewriter",
    page_icon="✨",
    layout="wide",
)

st.title("✨ Smart Resume Rewriter")

st.write(
    "Improve resume bullet points with clearer "
    "action verbs, role-specific guidance, "
    "and practical writing feedback."
)

st.info(
    "This version uses rule-based rewriting, "
    "not a generative AI model. It does not "
    "invent metrics, technologies, or achievements."
)

ROLES = [
    "Data Analyst",
    "Data Scientist",
    "Data Engineer",
    "AI/ML Engineer",
    "Business Intelligence Analyst",
    "Software Engineer",
]

ROLE_GUIDANCE = {
    "Data Analyst": (
        "Emphasize data analysis, SQL, dashboards, "
        "reporting, and verified business outcomes."
    ),
    "Data Scientist": (
        "Emphasize modeling, experimentation, "
        "evaluation, and statistical analysis."
    ),
    "Data Engineer": (
        "Emphasize data pipelines, ETL, data quality, "
        "orchestration, and cloud infrastructure."
    ),
    "AI/ML Engineer": (
        "Emphasize model development, APIs, "
        "deployment, evaluation, and monitoring."
    ),
    "Business Intelligence Analyst": (
        "Emphasize KPIs, dashboard development, "
        "reporting, and stakeholder insights."
    ),
    "Software Engineer": (
        "Emphasize implementation, testing, "
        "system design, APIs, and reliability."
    ),
}

# Conservative rewriting rules.
# Only change phrasing when the action is explicit.
REWRITE_RULES = [
    (
        r"^responsible for creating\b",
        "Created",
    ),
    (
        r"^responsible for developing\b",
        "Developed",
    ),
    (
        r"^responsible for analyzing\b",
        "Analyzed",
    ),
    (
        r"^responsible for designing\b",
        "Designed",
    ),
    (
        r"^responsible for maintaining\b",
        "Maintained",
    ),
    (
        r"^responsible for testing\b",
        "Tested",
    ),
    (
        r"^responsible for implementing\b",
        "Implemented",
    ),
    (
        r"^worked on creating\b",
        "Created",
    ),
    (
        r"^worked on developing\b",
        "Developed",
    ),
    (
        r"^worked on analyzing\b",
        "Analyzed",
    ),
    (
        r"^worked on building\b",
        "Built",
    ),
    (
        r"^was involved in creating\b",
        "Contributed to creating",
    ),
    (
        r"^helped with developing\b",
        "Contributed to developing",
    ),
]


def rewrite_bullet(text):
    original = re.sub(
        r"\s+", " ", text.strip()
    )

    improved = original

    for pattern, replacement in REWRITE_RULES:
        updated = re.sub(
            pattern,
            replacement,
            improved,
            count=1,
            flags=re.IGNORECASE,
        )

        if updated != improved:
            improved = updated
            break

    if improved:
        improved = (
            improved[0].upper() + improved[1:]
        )

        if improved[-1] not in ".!?":
            improved += "."

    return improved


def analyze_bullet(text):
    suggestions = []
    lower = text.lower()
    words = text.split()

    if len(words) < 10:
        suggestions.append(
            "Consider adding more specific context "
            "about your contribution."
        )

    if len(words) > 35:
        suggestions.append(
            "Consider shortening this bullet "
            "for readability."
        )

    if re.search(
        r"\b(responsible for|worked on|"
        r"helped with|involved in)\b",
        lower,
    ):
        suggestions.append(
            "Replace indirect wording with a "
            "clear description of your actual work."
        )

    if not re.search(r"\d", text):
        suggestions.append(
            "Add a measurable outcome only "
            "if you have a verified metric."
        )

    if not suggestions:
        suggestions.append(
            "The bullet is reasonably structured. "
            "Check its accuracy and relevance."
        )

    return suggestions


st.subheader("1. Enter Your Resume Bullet")

bullet = st.text_area(
    "Original resume bullet",
    placeholder=(
        "Responsible for creating dashboards "
        "using Tableau and SQL."
    ),
    height=130,
)

st.subheader("2. Select Target Role")

role = st.selectbox(
    "Target job role",
    ROLES,
)

if st.button(
    "✨ Rewrite My Bullet",
    type="primary",
):
    if not bullet.strip():
        st.warning(
            "Please enter a resume bullet."
        )
    else:
        improved = rewrite_bullet(bullet)

        st.session_state["original_bullet"] = (
            bullet.strip()
        )

        st.session_state["improved_bullet"] = (
            improved
        )

        st.session_state["selected_role"] = role


if "improved_bullet" in st.session_state:

    original = st.session_state[
        "original_bullet"
    ]

    improved = st.session_state[
        "improved_bullet"
    ]

    selected_role = st.session_state[
        "selected_role"
    ]

    st.divider()

    st.subheader(
        "3. Original vs Improved"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Original")
        st.info(original)

    with col2:
        st.markdown("#### Improved")
        st.success(improved)

    st.code(
        improved,
        language=None,
    )

    if improved == original:
        st.caption(
            "No safe automatic wording change "
            "was identified. The original wording "
            "has been preserved."
        )

    st.divider()

    st.subheader("4. Writing Feedback")

    for suggestion in analyze_bullet(original):
        st.write("•", suggestion)

    st.subheader("5. Role-Specific Guidance")

    st.write(
        ROLE_GUIDANCE[selected_role]
    )

    st.caption(
        "Include role-specific tools or achievements "
        "only when they reflect your real experience."
    )

    st.divider()

    st.subheader("6. Download Improved Bullet")

    st.download_button(
        "Download as Text",
        data=improved,
        file_name="improved_resume_bullet.txt",
        mime="text/plain",
    )

    st.caption(
        "Use the copy icon in the code box "
        "above to copy your improved bullet."
    )

st.divider()

st.subheader("Resume Quality Checklist")

st.checkbox(
    "Starts with a clear action verb"
)
st.checkbox(
    "Describes my actual contribution"
)
st.checkbox(
    "Mentions only technologies I used"
)
st.checkbox(
    "Includes verified results where available"
)
st.checkbox(
    "Is relevant to my target role"
)

st.caption(
    "JobPulse AI | Smart Resume Rewriter v2"
)
