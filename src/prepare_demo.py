
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / "data" / "jobpulse.db"
DEMO_FILE = ROOT / "data" / "demo_jobs.csv"


def prepare_demo():
    if not DB_FILE.exists():
        print("Database not found.")
        return

    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(
            "SELECT * FROM jobs",
            conn
        )

    if df.empty:
        print("No jobs available.")
        return

    # Use a reproducible subset.
    demo = df.sample(
        n=min(100, len(df)),
        random_state=42
    )

    # Exclude full descriptions and unnecessary columns.
    columns = [
        "job_id",
        "job_title",
        "company",
        "location",
        "remote",
        "role_category",
        "skills",
        "skill_count",
        "job_url",
        "source",
        "collected_at"
    ]

    columns = [c for c in columns if c in demo.columns]
    demo = demo[columns]

    DEMO_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    demo.to_csv(DEMO_FILE, index=False)

    print(f"Demo dataset created: {DEMO_FILE}")
    print(f"Records: {len(demo)}")


if __name__ == "__main__":
    prepare_demo()
