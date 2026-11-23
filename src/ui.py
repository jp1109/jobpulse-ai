
from pathlib import Path

import streamlit as st


def apply_custom_css():
    root = Path(__file__).resolve().parent.parent
    css_path = root / ".streamlit" / "style.css"

    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.html(f"<style>{css}</style>")


def show_branding():
    st.sidebar.markdown("## 🚀 JobPulse AI")
    st.sidebar.caption(
        "Job Market Intelligence & Resume Analytics"
    )
    st.sidebar.divider()
