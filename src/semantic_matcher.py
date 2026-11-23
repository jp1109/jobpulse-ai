
import pandas as pd
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_model():
    return SentenceTransformer(MODEL_NAME)


def calculate_semantic_matches(
    resume_text,
    jobs_df,
    model
):
    """
    Rank jobs using semantic similarity.
    Scores measure text similarity, not hiring probability.
    """

    if not resume_text.strip() or jobs_df.empty:
        return pd.DataFrame()

    jobs = jobs_df.copy()

    # Use available job fields as the comparison text.
    # This is a limited proxy until we collect full descriptions.
    columns = [
    col for col in [
        "job_title",
        "description",
        "tags",
        "skills"
    ]
    if col in jobs.columns
]
    if not columns:
        return pd.DataFrame()

    jobs["comparison_text"] = (
        jobs[columns]
        .fillna("")
        .astype(str)
        .agg(" ".join, axis=1)
    )

    resume_embedding = model.encode(
        resume_text[:12000],
        convert_to_tensor=True
    )

    job_embeddings = model.encode(
        jobs["comparison_text"].tolist(),
        convert_to_tensor=True,
        batch_size=32,
        show_progress_bar=False
    )

    similarities = util.cos_sim(
        resume_embedding,
        job_embeddings
    )[0].cpu().numpy()

    jobs["semantic_similarity"] = similarities

    return jobs.sort_values(
        "semantic_similarity",
        ascending=False
    ).reset_index(drop=True)
