# DegreeBaba Content Publisher

Internal Streamlit micro-app for turning DegreeBaba `.docx` content into reviewed, ACF-compatible WordPress draft payloads.

## Run Locally

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run app.py --server.port 8601 --server.headless true
```

Open `http://localhost:8601`.

## What Is Included

- Dashboard, single upload, bulk upload, upload history, and settings screens.
- Real DegreeBaba ACF field sets for university, course, specialization, category, and blog pages.
- Existing-page detection state before image upload.
- Dynamic image slots by page type.
- Validation table with field names, source headings, word counts, confidence, status, and draft-only WordPress action.
- AI Mapping Review screen for low-confidence or missing mappings.
- WordPress create/update draft path through the REST API when credentials are configured.
- Deterministic extraction fallbacks for title, hero, SEO meta, headings, tables, repeaters, and common stats.

## Generate Submission Artifacts

```bash
.venv/bin/python scripts/generate_test_artifacts.py
```

This writes payloads and validation summaries to `outputs/`.

## Documentation

- [Assignment alignment report](docs/ALIGNMENT_REPORT.md)
- [Interview explanation](docs/INTERVIEW_EXPLANATION.md)
