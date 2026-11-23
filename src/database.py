
from pathlib import Path
import sqlite3
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_FILE = PROJECT_ROOT / "data" / "processed" / "clean_jobs.csv"
DB_FILE = PROJECT_ROOT / "data" / "jobpulse.db"


def create_database():
    if not CSV_FILE.exists():
        print("Cleaned dataset not found.")
        print("Run python src/clean_jobs.py first.")
        return

    df = pd.read_csv(CSV_FILE)

    if df.empty:
        print("Cleaned dataset is empty.")
        return

    # Normalize remote values for SQL analysis
    if "remote" in df.columns:
        df["remote"] = (
            df["remote"]
            .astype("string")
            .str.lower()
            .map({"true": 1, "false": 0})
        )

    DB_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_FILE) as conn:
        df.to_sql(
            "jobs",
            conn,
            if_exists="replace",
            index=False
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_role "
            "ON jobs(role_category)"
        )

        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_company "
            "ON jobs(company)"
        )

        total = conn.execute(
            "SELECT COUNT(*) FROM jobs"
        ).fetchone()[0]

    print("DATABASE CREATED SUCCESSFULLY")
    print(f"Database: {DB_FILE}")
    print(f"Total jobs loaded: {total}")


if __name__ == "__main__":
    create_database()
