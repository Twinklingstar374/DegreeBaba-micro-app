# Interview Explanation: DegreeBaba Content Publisher MVP

## 1. Problem I Was Solving

DegreeBaba has content writers preparing University, Course, and Specialization pages in Word documents. The website, however, renders those pages from structured WordPress ACF fields. The assignment was to build an MVP that takes a `.docx` file, understands its sections, maps them to the correct ACF fields, validates the output, and prepares a draft payload for WordPress without losing data.

The hardest part is not simply reading a Word file. The hard part is reliability: headings vary, stats can be confused, repeaters need JSON arrays, WYSIWYG fields must preserve HTML, and re-uploading must update an existing WordPress page instead of creating duplicates.

## 2. Approach Chosen

I implemented the research recommendation: a deterministic + AI-assisted hybrid pipeline.

I did not make the LLM responsible for everything because the task brief explicitly warns about hallucination, stat confusion, repeated values, thin content, and malformed repeater JSON. Instead, the system first uses deterministic parsing, heading rules, regex extraction, table extraction, and schema validation. AI mapping is only a fallback for ambiguous fields when an API key is available.

## 3. System Flow

1. The user uploads a `.docx` file in the Streamlit app.
2. The user selects the page type: University, Course, Specialization, Category, or Blog.
3. `DocumentParser` uses Mammoth to convert the Word document into HTML.
4. `DocumentSegmenter` groups HTML under document headings.
5. `PageTypeClassifier` can infer the page type from headings and file name if needed.
6. `ContentPipeline` maps sections into page-specific ACF fields.
7. `DeterministicExtractor` extracts stats and tables with regex/structured parsing.
8. The pipeline preserves body content as HTML for WYSIWYG fields.
9. Repeaters such as FAQs, highlights, reviews, admissions, and accreditations are converted into JSON arrays where possible.
10. `ValidationEngine` checks missing fields, thin content, low confidence, malformed repeaters, and stat length constraints.
11. The UI shows mapped fields, source headings, word counts, confidence, warnings, and missing fields.
12. Low-confidence fields can be reviewed in the AI Mapping Review screen.
13. The final ACF JSON can be downloaded or sent to WordPress as a draft if credentials are configured.

## 4. Why This Design Reduces Risk

The system keeps traceability for every extracted field: value, source heading, extraction method, confidence, and review status. This means a content reviewer can see exactly why a field was populated and where it came from.

For critical structured values, the pipeline uses deterministic extraction before AI. This avoids known failure cases from the brief, such as confusing faculty count with number of programs or turning a repeater into a flat string.

The app never silently publishes live. It saves as draft, and the WordPress client checks for an existing page before creating a new one. This directly addresses the duplicate post constraint.

## 5. UI Screens Implemented

- Dashboard: overview of published pages, drafts, issues, and recent uploads.
- New Upload: upload `.docx`, select page type, parse and validate.
- Existing Page Detection: shows whether the upload will create a new draft or update an existing draft.
- Image Upload: dynamic image slots based on page type.
- Validation Report: field-by-field mapping, confidence, status, warnings, and JSON export.
- AI Mapping Review: confirm or override low-confidence mappings.
- Bulk Upload: MVP batch upload surface.
- Upload History: session history for processed files.
- Settings: WordPress and AI credential inputs.

## 6. WordPress Integration

The `WPClient` is designed to prevent duplicates:

1. Search WordPress pages by title.
2. If an existing page is found, update it.
3. If not found, create a new page.
4. Always set `status` to `draft`.
5. Put the final payload under the `acf` key for ACF REST compatibility.

If credentials are not configured, the app clearly tells the user that the save was simulated locally instead of pretending to publish.

## 7. Validation Strategy

Validation is deliberately strict because the assignment has zero-data-loss expectations.

The validator checks:

- Missing required fields.
- Missing optional fields.
- Low-confidence mappings.
- Thin WYSIWYG content.
- Empty repeaters.
- Stat values that are too long for hero badges.

The result is a review report, not just a JSON payload. This is important because the content team needs to know what is safe and what still needs human review.

## 8. Test Artifacts

I added `scripts/generate_test_artifacts.py`. It extracts the supplied sample DOCX files, runs them through the pipeline, and writes:

- Per-document ACF payload JSON files.
- `outputs/validation-summary.json`
- `outputs/validation-report.md`

The brief asks for two Word files per page type. The supplied archive contains three DOCX files, so the script processes all available samples and is ready for more files when added to `data/sample_docs/`.

Current generated results from the supplied archive:

| Document | Page Type | Score |
|---|---:|---:|
| Copy of Amity Online MBA in Data Science.docx | Specialization | 89 |
| Copy of Amity University Online MBA program.docx | Course | 93 |
| Copy of Amity University Online.docx | University | 90 |

## 9. What I Would Improve With Two More Weeks

First, I would connect the full production ACF schema document if available, including exact field types and required/optional rules. Second, I would add stronger template-aware parsing for Quick Facts blocks so hero stats become even more reliable. Third, I would add automated tests using six or more real documents across all three page types. Fourth, I would build a richer manual mapping editor with drag-and-drop section assignment and persisted reviewer decisions. Finally, I would test the WordPress integration against a staging site with ACF-to-REST enabled.

## 10. Summary Pitch

This MVP is built around reliability rather than flashy automation. It parses Word documents, preserves HTML, maps sections into ACF fields, validates risky areas, supports manual review, and prepares WordPress draft payloads. The key idea is that AI helps where language is ambiguous, but deterministic extraction and validation protect the publishing workflow from data loss.
