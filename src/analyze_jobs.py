
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_FILE = PROJECT_ROOT / "data" / "jobpulse.db"


def run_query(conn, title, query):
    print(f"\n{title}")
    print("-" * 45)
    result = pd.read_sql_query(query, conn)
    print(result.to_string(index=False))


def analyze_jobs():
    if not DB_FILE.exists():
        print("Database not found. Run database.py first.")
        return

    with sqlite3.connect(DB_FILE) as conn:

        run_query(
            conn,
            "1. Total Job Postings",
            """
            SELECT COUNT(*) AS total_jobs
            FROM jobs;
            """
        )

        run_query(
            conn,
            "2. Jobs by Role",
            """
            SELECT
                role_category,
                COUNT(*) AS job_count
            FROM jobs
            GROUP BY role_category
            ORDER BY job_count DESC;
            """
        )

        run_query(
            conn,
            "3. Remote Job Opportunities",
            """
            SELECT
                COUNT(*) AS remote_jobs
            FROM jobs
            WHERE remote = 1;
            """
        )

        run_query(
            conn,
            "4. Top Hiring Companies",
            """
            SELECT
                company,
                COUNT(*) AS total_postings
            FROM jobs
            WHERE company IS NOT NULL
              AND TRIM(company) != ''
            GROUP BY company
            ORDER BY total_postings DESC
            LIMIT 10;
            """
        )

        run_query(
            conn,
            "5. Jobs With Identified Skills",
            """
            SELECT
                job_title,
                company,
                skills,
                skill_count
            FROM jobs
            WHERE skill_count > 0
            ORDER BY skill_count DESC
            LIMIT 10;
            """
        )

        run_query(
            conn,
            "6. Average Skills Detected by Role",
            """
            SELECT
                role_category,
                ROUND(AVG(skill_count), 2)
                    AS avg_detected_skills
            FROM jobs
            GROUP BY role_category
            ORDER BY avg_detected_skills DESC;
            """
        )


if __name__ == "__main__":
    analyze_jobs()
