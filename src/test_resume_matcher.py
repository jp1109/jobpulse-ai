
import pandas as pd

from src.resume_matcher import (
    extract_skills,
    calculate_match,
    rank_jobs,
)


def test_extract_skills():
    text = "I have experience with Python, SQL and Tableau."

    skills = extract_skills(text)

    assert "Python" in skills
    assert "SQL" in skills
    assert "Tableau" in skills


def test_calculate_match():
    resume_skills = {"Python", "SQL", "Tableau"}
    job_skills = {"Python", "SQL", "AWS"}

    score, matched, missing = calculate_match(
        resume_skills,
        job_skills
    )

    assert score == 66.7
    assert matched == {"Python", "SQL"}
    assert missing == {"AWS"}


def test_empty_job_skills():
    score, matched, missing = calculate_match(
        {"Python"}, set()
    )

    assert score is None
    assert matched == set()
    assert missing == set()


def test_job_ranking():
    jobs = pd.DataFrame([
        {
            "job_title": "Data Analyst",
            "company": "Example A",
            "location": "Remote",
            "skills": "Python, SQL",
            "job_url": "https://example.com/a"
        },
        {
            "job_title": "Cloud Engineer",
            "company": "Example B",
            "location": "Remote",
            "skills": "AWS, Docker",
            "job_url": "https://example.com/b"
        }
    ])

    results = rank_jobs(
        jobs,
        {"Python", "SQL", "Tableau"}
    )

    assert len(results) == 2
    assert results.iloc[0]["job_title"] == "Data Analyst"
    assert results.iloc[0]["match_score"] == 100.0
    assert results.iloc[1]["match_score"] == 0.0
