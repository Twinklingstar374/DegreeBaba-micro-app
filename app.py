import streamlit as st
import json
from src.pipeline import ContentPipeline

st.set_page_config(page_title="DegreeBaba Publisher MVP", layout="wide")

st.title("DegreeBaba Content Publisher MVP")
st.markdown("Converts DOCX into validated ACF-compatible JSON payloads.")
st.markdown("*Prioritizing explainability and deterministic traceability.*")

@st.cache_resource
def get_pipeline():
    return ContentPipeline()

pipeline = get_pipeline()

uploaded_file = st.file_uploader("Upload .docx content file", type=["docx"])

if uploaded_file:
    st.info(f"Processing: {uploaded_file.name}")
    
    with st.spinner("Extracting and mapping content..."):
        report = pipeline.process_file(uploaded_file, uploaded_file.name)
        
    st.subheader(f"Page Classification: `{report.page_type.upper()}`")
    
    # Validation Report Section
    st.header("Validation Report")
    
    if report.is_publishable:
        st.success("✅ Document is ready for publishing.")
    else:
        st.error("❌ Document has critical errors and cannot be published.")
        
    if report.warnings:
        for w in report.warnings:
            if w.severity == "error":
                st.error(f"**{w.field_name}**: {w.message}")
            else:
                st.warning(f"**{w.field_name}**: {w.message}")
    else:
        st.write("No warnings found.")
        
    if report.fields_needing_review:
        st.info(f"Fields flagged for manual review: {', '.join(report.fields_needing_review)}")

    # Extracted Data Section
    st.header("Extraction Traceability")
    
    traceability_data = []
    for field, data in report.extracted_fields.items():
        traceability_data.append({
            "Field": field,
            "Method": data.extraction_method,
            "Confidence": f"{data.confidence:.2f}",
            "Source Heading": data.source_heading,
            "Review Flag": "Yes" if data.needs_review else "No"
        })
    
    if traceability_data:
        st.table(traceability_data)

    # JSON Payload Output
    st.header("ACF JSON Payload")
    
    # Convert ExtractedFields to raw values for JSON
    final_payload = {
        field: data.value for field, data in report.extracted_fields.items()
    }
    
    st.json(final_payload)
    
    st.download_button(
        label="Download JSON Payload",
        data=json.dumps(final_payload, indent=2),
        file_name=f"{uploaded_file.name.replace('.docx', '')}_payload.json",
        mime="application/json"
    )
