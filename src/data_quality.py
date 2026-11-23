
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "data" / "jobpulse.db"
REPORT_FILE = ROOT / "reports" / "data_quality_report.csv"


def generate_quality_report():

    if not DB_FILE.exists():
        print("Database not found.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query("SELECT * FROM jobs", conn)

    if df.empty:
        print("No job records available.")
        return

    total = len(df)

    checks = [
        {
            "metric": "Total job postings",
            "value": total
        },
        {
            "metric": "Duplicate job IDs",
            "value": int(df["job_id"].duplicated().sum())
        },
        {
            "metric": "Missing job titles",
            "value": int(
                df["job_title"].isna().sum()
                + df["job_title"].fillna("").eq("").sum()
                - df["job_title"].isna().sum()
            )
        },
        {
            "metric": "Missing company names",
            "value": int(
                df["company"].fillna("").str.strip().eq("").sum()
            )
        },
        {
            "metric": "Jobs with detected skills",
            "value": int((df["skill_count"] > 0).sum())
        },
        {
            "metric": "Jobs without detected skills",
            "value": int((df["skill_count"] == 0).sum())
        },
        {
            "metric": "Remote jobs",
            "value": int(
                (pd.to_numeric(
                    df["remote"], errors="coerce"
                ) == 1).sum()
            )
        }
    ]

    report = pd.DataFrame(checks)

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    report.to_csv(REPORT_FILE, index=False)

    print("\nJOBPULSE DATA QUALITY REPORT")
    print("-" * 40)
    print(report.to_string(index=False))
    print(f"\nReport saved: {REPORT_FILE}")


if __name__ == "__main__":
    generate_quality_report()
