
from pathlib import Path
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "real_jobs.csv"
OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "clean_jobs.csv"

SKILL_PATTERNS = {
    "Python": r"\bpython\b",
    "SQL": r"\bsql\b",
    "Excel": r"\bexcel\b",
    "Tableau": r"\btableau\b",
    "Power BI": r"\bpower\s*bi\b",
    "AWS": r"\baws\b|\bamazon web services\b",
    "Azure": r"\bazure\b",
    "GCP": r"\bgcp\b|\bgoogle cloud\b",
    "Docker": r"\bdocker\b",
    "Kubernetes": r"\bkubernetes\b",
    "Spark": r"\b(?:apache\s+)?spark\b|\bpyspark\b",
    "Machine Learning": r"\bmachine learning\b",
    "NLP": r"\bnlp\b|\bnatural language processing\b",
    "TensorFlow": r"\btensorflow\b",
    "PyTorch": r"\bpytorch\b",
    "Java": r"\bjava\b",
    "JavaScript": r"\bjavascript\b",
    "React": r"\breact(?:\.js)?\b",
    "Git": r"\bgit\b",
}


def extract_skills(text):
    if pd.isna(text):
        return ""

    text = str(text)
    skills = [
        skill
        for skill, pattern in SKILL_PATTERNS.items()
        if re.search(pattern, text, flags=re.IGNORECASE)
    ]
    return ", ".join(skills)


def classify_role(title):
    title = str(title).lower()

    if "data engineer" in title:
        return "Data Engineer"
    if "data scientist" in title:
        return "Data Scientist"
    if "data analyst" in title:
        return "Data Analyst"
    if "business intelligence" in title or "bi analyst" in title:
        return "BI Analyst"
    if "machine learning" in title or "ml engineer" in title:
        return "ML Engineer"
    if "ai engineer" in title:
        return "AI Engineer"

    return "Other"


def clean_jobs():
    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        print("Run python src/fetch_jobs.py first.")
        return

    df = pd.read_csv(INPUT_FILE)

    if df.empty:
        print("The input dataset is empty.")
        return

    df = df.drop_duplicates(subset=["job_id"]).copy()

    for column in ["job_title", "company", "location", "tags"]:
        if column not in df.columns:
            df[column] = ""

        df[column] = df[column].fillna("").astype(str).str.strip()

    df = df[df["job_title"] != ""].copy()

    df["role_category"] = df["job_title"].apply(classify_role)

    # The API tags are not always a complete skills list.
    if "description" not in df.columns:
       df["description"] = ""

    df["description"] = df["description"].fillna("")

    df["combined_text"] = (
    df["job_title"].fillna("") + " " +
    df["tags"].fillna("") + " " +
    df["description"]
)

    df["skills"] = df["combined_text"].apply(extract_skills)

    df["skill_count"] = df["skills"].apply(
        lambda value: len(value.split(", ")) if value else 0
    )

    if "remote" in df.columns:
        df["remote"] = df["remote"].astype("string").str.lower().map(
            {"true": True, "false": False}
        ).astype("boolean")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nDATA CLEANING COMPLETE")
    print("----------------------")
    print(f"Total cleaned jobs: {len(df)}")
    print(f"Jobs with detected skills: {(df['skill_count'] > 0).sum()}")

    print("\nJob categories:")
    print(df["role_category"].value_counts())

    print("\nSample cleaned records:")
    print(df[["job_title", "role_category", "skills"]].head())

    print(f"\nSaved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_jobs()
