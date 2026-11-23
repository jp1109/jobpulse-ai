
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import requests

API_URL = "https://www.arbeitnow.com/api/job-board-api"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "real_jobs.csv"


def fetch_jobs():
    print("Connecting to the job board API...")

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    jobs = response.json().get("data", [])

    if not jobs:
        print("No jobs returned by the API.")
        return

    records = []
    collected_at = datetime.now(timezone.utc).isoformat()

    for job in jobs:
        records.append({
            "job_id": job.get("slug"),
            "job_title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "remote": job.get("remote"),
            "tags": ", ".join(job.get("tags") or []),
            "description": job.get("description") or "",
            "job_url": job.get("url"),
            "source": "Arbeitnow",
            "collected_at": collected_at
        })

    df = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Successfully collected {len(df)} jobs.")
    print(f"Saved to: {OUTPUT_FILE}")
    print(df[["job_title", "company", "location"]].head())


if __name__ == "__main__":
    fetch_jobs()
