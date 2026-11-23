from pathlib import Path
import pandas as pd


def test_sample_jobs_have_unique_ids():
    path = Path(__file__).resolve().parents[1] / "data" / "raw" / "sample_jobs.csv"
    df = pd.read_csv(path)
    assert df["job_id"].is_unique
    assert (df["salary_min"] <= df["salary_max"]).all()
