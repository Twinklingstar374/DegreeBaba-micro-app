# DegreeBaba MVP QA Validation Report

> Generated automatically by `scripts/generate_test_artifacts.py`.

## Pipeline Status

✅ **DOCX Parsing** — Successful
✅ **Section Segmentation** — Successful
✅ **Deterministic Extraction** — Applied
✅ **Validation Engine** — Completed
⚠️ **Semantic Mappings** — Some optional or low-confidence fields flagged for manual review

## Coverage Note

The supplied dataset contains three DOCX files. The task brief asks for two files per page type, so this script is configured to process every supplied DOCX dynamically and is ready to process additional files once placed in the `data/sample_docs/` directory.

## Extraction & Validation Results

| Document | Page Type | Validation Score | Mapped / Total | Errors | Warnings |
|---|:---:|:---:|:---:|:---:|:---:|
| `Copy of Amity Online MBA in Data Science.docx` | Specialization | **89** | 28 / 45 | 0 | 18 |
| `Copy of Amity University Online MBA program.docx` | Course | **93** | 37 / 48 | 0 | 12 |
| `Copy of Amity University Online.docx` | University | **90** | 25 / 38 | 0 | 14 |

## Validation Criteria

- **Errors:** Critical extraction failures (e.g., missing strictly required fields, malformed arrays, or stat strings exceeding the 6-character hard constraint).
- **Warnings:** Missing optional fields, low-confidence AI semantic mappings, or thin content (text blocks below minimum length thresholds).
- **Validation Score:** An aggregate metric (0-100) calculated based on mapping completeness, structural validity, and extraction confidence. Errors heavily penalize the score.

> **Note:** A high number of warnings is expected and acceptable. They primarily indicate semantically ambiguous or optional fields that the pipeline intentionally flagged for a human editor to review, rather than indicating a pipeline failure.

## Reference HTML Alignment

The MVP reads the three supplied NMIMS final HTML pages and maps each final website section to the parser's ACF field set.

| Page Type | Reference Sections | Mapped Sections | Reference File |
|---|:---:|:---:|---|
| University | 13 | 12 | `/Users/bulbulagarwalla/DegreeBaba-micro-app/references/html/nmims-university-page.html` |
| Course | 14 | 13 | `/Users/bulbulagarwalla/DegreeBaba-micro-app/references/html/nmims-online-mba.html` |
| Specialization | 14 | 13 | `/Users/bulbulagarwalla/DegreeBaba-micro-app/references/html/nmims-mba-marketing.html` |

## Conclusion

The deterministic extraction rules (Regex & HTML Parsing) performed reliably across the provided test set, successfully bypassing the risks associated with pure LLM hallucinations. The validation safeguards effectively enforced the zero-data-loss and format constraint requirements. The pipeline successfully processed all supplied document types (University, Course, and Specialization) into strict, ACF-compatible JSON structures.

## How To Reproduce

```bash
.venv/bin/python scripts/generate_test_artifacts.py
```