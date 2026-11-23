# JobPulse AI

**Job Market Intelligence & AI Resume Matching Platform**

JobPulse AI is a Python-based application for analyzing collected job postings, identifying technical skills, and comparing resumes against available job requirements.

### Live Application

[Launch JobPulse AI](https://jobpulse-ai-jp.streamlit.app)

## Features

- Job data ingestion through a public job-board API
- Data cleaning and preprocessing using Pandas
- SQLite database and SQL analytics
- Interactive dashboards built with Streamlit and Plotly
- Resume PDF text extraction
- Explainable skill-overlap matching
- Semantic similarity matching using sentence embeddings
- CSV report generation

## Technology Stack

Python, Pandas, SQL, SQLite, Streamlit, Plotly, PyMuPDF, Scikit-learn, Sentence Transformers, and Pytest.

## Project Limitations

The current dataset is a collected sample rather than a representative survey of the US job market. Skill extraction is based on available job tags, which may not capture complete requirements. Matching scores describe text similarity or detected skill overlap, not hiring probabilities.

## Running Locally

1. Create and activate a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run the data collection, cleaning, and database scripts.
4. Launch the Streamlit application with `python -m streamlit run app.py`.

## Testing

Run `python -m pytest -v` to execute automated tests.

## Future Improvements

- Broader US job data coverage
- Full job-description extraction
- Improved semantic ranking
- Skill-gap recommendations
- Model evaluation against manually reviewed matches
- Cloud deployment