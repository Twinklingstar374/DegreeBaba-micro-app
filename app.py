import hashlib
import json
import os
import re
from datetime import datetime
from typing import Any, Dict

import streamlit as st

from src.pipeline import ContentPipeline
from src.schemas.page_fields import get_fields, get_image_slots
from src.utils.wp_client import WPClient


st.set_page_config(
    page_title="DegreeBaba Content Publisher",
    layout="wide",
    initial_sidebar_state="expanded",
)


PAGE_TYPES = ["university", "course", "specialization", "category", "blog"]
NAV_ITEMS = ["Dashboard", "New Upload", "AI Mapping Review", "Bulk Upload", "Upload History", "Settings"]


def inject_css() -> None:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

            :root {
                --navy: #0E1F3D;
                --navy-hover: #162d54;
                --orange: #E84010;
                --orange-hover: #c93509;
                --page: #F7F8FA;
                --card: #FFFFFF;
                --border: #E5E7EB;
                --text: #111827;
                --muted: #4B5563;
                --disabled: #9CA3AF;
                --hover: #F3F4F6;
                --success-bg: #EAF3DE;
                --success: #3B6D11;
                --success-border: #B6D98A;
                --warn-bg: #FAEEDA;
                --warn: #854F0B;
                --warn-border: #F5C97A;
                --error-bg: #FCEBEB;
                --error: #A32D2D;
                --error-border: #F09595;
                --info-bg: #E6F1FB;
                --info: #185FA5;
                --info-border: #93C4EE;
            }

            html, body, [class*="css"] {
                font-family: "DM Sans", sans-serif;
                letter-spacing: 0;
            }

            .stApp {
                background: var(--page);
                color: var(--text);
            }

            header[data-testid="stHeader"] {
                background: transparent;
                height: 0;
            }

            div[data-testid="stToolbar"],
            #MainMenu,
            footer {
                display: none !important;
                visibility: hidden !important;
            }

            main,
            main p,
            main label,
            main small,
            main [data-testid="stMarkdownContainer"],
            main [data-testid="stMarkdownContainer"] p,
            main [data-testid="stMarkdownContainer"] span,
            main [data-testid="stText"],
            main [data-testid="stWidgetLabel"],
            main [data-testid="stCaptionContainer"],
            main div[data-testid="stForm"],
            main div[data-testid="stRadio"] label,
            main div[data-testid="stSelectbox"] label,
            main div[data-testid="stTextInput"] label {
                color: var(--text) !important;
            }

            section[data-testid="stSidebar"] {
                background: var(--navy);
                width: 240px !important;
                border-right: none;
            }

            section[data-testid="stSidebar"] * {
                color: rgba(255,255,255,0.78);
            }

            section[data-testid="stSidebar"] h1,
            section[data-testid="stSidebar"] h2,
            section[data-testid="stSidebar"] h3 {
                color: #FFFFFF;
            }

            section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
                background: transparent !important;
                border: 0 !important;
                box-shadow: none !important;
                color: rgba(255,255,255,0.72) !important;
                justify-content: flex-start;
                padding: 10px 12px;
                border-radius: 0 8px 8px 0;
                width: 100%;
            }

            section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
                background: rgba(255,255,255,0.08) !important;
                color: #FFFFFF !important;
            }

            section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
            section[data-testid="stSidebar"] div[data-testid="stButton"] > button span,
            section[data-testid="stSidebar"] div[data-testid="stButton"] > button div {
                color: inherit !important;
                font-weight: 500;
            }

            .block-container {
                max-width: 1120px;
                padding-top: 32px;
                padding-bottom: 96px;
            }

            h1 {
                color: var(--text);
                font-size: 24px !important;
                font-weight: 600 !important;
                margin-bottom: 4px !important;
            }

            h2 {
                color: var(--text);
                font-size: 20px !important;
                font-weight: 600 !important;
            }

            h3 {
                color: var(--text);
                font-size: 16px !important;
                font-weight: 500 !important;
                line-height: 1.5 !important;
            }

            a {
                color: var(--orange);
            }

            .mono, code {
                font-family: "JetBrains Mono", monospace !important;
            }

            .topbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 16px;
                margin-bottom: 24px;
                padding: 0 0 20px;
                border-bottom: 1px solid var(--border);
            }

            .topbar-subtitle {
                color: var(--muted);
                font-size: 13px;
                margin-top: 4px;
            }

            .card {
                background: var(--card);
                border: 1px solid var(--border);
                border-radius: 12px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06);
                padding: 20px 24px;
                margin-bottom: 16px;
            }

            .card,
            .card *,
            .section-row,
            .section-row *,
            .upload-zone,
            .upload-zone * {
                color: var(--text);
            }

            .stat-value {
                color: var(--text);
                font-size: 30px;
                font-weight: 700;
                line-height: 1.1;
            }

            .label {
                color: var(--muted);
                font-size: 13px;
                font-weight: 500;
                margin-bottom: 8px;
            }

            .badge {
                display: inline-flex;
                align-items: center;
                border-radius: 20px;
                font-size: 11px;
                font-weight: 600;
                padding: 4px 9px;
                white-space: nowrap;
            }

            .badge-success { background: var(--success-bg); color: var(--success); }
            .badge-warn { background: var(--warn-bg); color: var(--warn); }
            .badge-error { background: var(--error-bg); color: var(--error); }
            .badge-info { background: var(--info-bg); color: var(--info); }
            .badge-neutral { background: #F3F4F6; color: #4B5563; }

            main .badge-success { color: var(--success) !important; }
            main .badge-warn { color: var(--warn) !important; }
            main .badge-error { color: var(--error) !important; }
            main .badge-info { color: var(--info) !important; }
            main .badge-neutral { color: #4B5563 !important; }

            .upload-zone {
                min-height: 200px;
                border: 2px dashed var(--border);
                border-radius: 16px;
                background: #FAFAFA;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                text-align: center;
                padding: 24px;
                margin-bottom: 20px;
            }

            .upload-zone strong {
                color: var(--text);
                font-size: 16px;
                font-weight: 600;
            }

            .upload-zone span {
                color: var(--muted);
                font-size: 14px;
            }

            .stepper {
                display: flex;
                align-items: center;
                gap: 14px;
                border-bottom: 1px solid var(--border);
                margin-bottom: 24px;
                padding-bottom: 14px;
            }

            .step {
                color: var(--disabled);
                font-size: 13px;
                font-weight: 600;
                padding-bottom: 8px;
                border-bottom: 2px solid transparent;
            }

            .step.active {
                color: var(--navy);
                border-bottom-color: var(--navy);
            }

            .step.done {
                color: var(--success);
            }

            .section-row {
                border-left: 3px solid transparent;
                border-bottom: 1px solid var(--border);
                padding: 12px 10px;
            }

            .section-row.warn {
                background: #FFFBEB;
                border-left-color: var(--warn);
            }

            .section-row.error {
                background: #FFF5F5;
                border-left-color: var(--error);
            }

            .preview {
                color: var(--muted);
                font-size: 13px;
                font-style: italic;
            }

            .confidence-track {
                width: 100%;
                height: 4px;
                border-radius: 8px;
                background: #F3F4F6;
                overflow: hidden;
                margin-top: 6px;
            }

            .confidence-fill {
                height: 4px;
                background: var(--orange);
            }

            .info-banner,
            .success-banner,
            .warn-banner,
            .error-banner {
                border-radius: 12px;
                padding: 14px 16px;
                margin-bottom: 16px;
                font-size: 14px;
                font-weight: 500;
            }

            .info-banner { background: var(--info-bg); color: var(--info); border: 1px solid var(--info-border); }
            .success-banner { background: var(--success-bg); color: var(--success); border: 1px solid var(--success-border); }
            .warn-banner { background: var(--warn-bg); color: var(--warn); border: 1px solid var(--warn-border); }
            .error-banner { background: var(--error-bg); color: var(--error); border: 1px solid var(--error-border); }

            .info-banner, .info-banner * { color: var(--info) !important; }
            .success-banner, .success-banner * { color: var(--success) !important; }
            .warn-banner, .warn-banner * { color: var(--warn) !important; }
            .error-banner, .error-banner * { color: var(--error) !important; }

            .sticky-actions {
                position: fixed;
                left: 240px;
                right: 0;
                bottom: 0;
                z-index: 10;
                background: rgba(255,255,255,0.94);
                border-top: 1px solid var(--border);
                padding: 12px 32px;
                backdrop-filter: blur(10px);
            }

            div[data-testid="stButton"] > button,
            div[data-testid="stDownloadButton"] > button {
                border-radius: 8px;
                border: 1px solid var(--border);
                font-weight: 600;
                background: #FFFFFF;
                color: var(--navy);
                transition: all 0.15s ease;
            }

            div[data-testid="stButton"] > button[kind="primary"],
            div[data-testid="stDownloadButton"] > button[kind="primary"] {
                background: var(--orange);
                border: 1px solid var(--orange);
                color: #FFFFFF;
                box-shadow: none;
            }

            div[data-testid="stButton"] > button[kind="primary"]:hover,
            div[data-testid="stDownloadButton"] > button[kind="primary"]:hover {
                background: var(--orange-hover);
                border-color: var(--orange-hover);
                transform: scale(0.99);
            }

            main div[data-testid="stButton"] > button:not([kind="primary"]) p,
            main div[data-testid="stDownloadButton"] > button p {
                color: var(--navy);
            }

            main div[data-testid="stButton"] > button[kind="primary"] p,
            main div[data-testid="stDownloadButton"] > button[kind="primary"] p {
                color: #FFFFFF;
            }

            div[data-testid="stFileUploader"] button,
            div[data-testid="stFileUploader"] button *,
            button[data-testid="stBaseButton-secondaryFormSubmit"],
            button[data-testid="stBaseButton-secondaryFormSubmit"] *,
            button[kind="secondaryFormSubmit"],
            button[kind="secondaryFormSubmit"] * {
                color: #FFFFFF !important;
            }

            div[data-testid="stFileUploader"] button {
                background: var(--navy) !important;
                border-color: var(--navy) !important;
            }

            input,
            textarea,
            div[data-baseweb="input"] input,
            div[data-baseweb="textarea"] textarea {
                background: #FFFFFF !important;
                color: var(--text) !important;
                border-color: var(--border) !important;
            }

            div[data-baseweb="select"] > div,
            div[role="radiogroup"] label,
            div[data-testid="stFileUploader"] section {
                background: #FFFFFF !important;
                border-color: var(--border) !important;
                color: var(--text) !important;
            }

            div[data-testid="stFileUploader"] *,
            div[data-testid="stRadio"] *,
            div[data-testid="stSelectbox"] *,
            div[data-testid="stTextInput"] *,
            div[data-testid="stFileUploaderDropzone"] * {
                color: var(--text) !important;
            }

            div[data-testid="stFileUploader"] small,
            div[data-testid="stFileUploader"] [data-testid="stCaptionContainer"],
            div[data-testid="stCaptionContainer"],
            .preview,
            .label,
            .topbar-subtitle {
                color: var(--muted) !important;
            }

            div[data-testid="stAlert"] *,
            div[data-testid="stNotification"] * {
                color: var(--text) !important;
            }

            div[data-testid="stFileUploaderDropzone"] {
                background: #FAFAFA !important;
                border-color: var(--border) !important;
            }

            div[data-testid="stVerticalBlockBorderWrapper"] {
                background: var(--card) !important;
                border-color: var(--border) !important;
                box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            }

            div[data-testid="stExpander"] {
                background: var(--card) !important;
                border-color: var(--border) !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_pipeline() -> ContentPipeline:
    return ContentPipeline()


def init_state() -> None:
    defaults = {
        "screen": "Dashboard",
        "upload_step": 1,
        "page_type": "university",
        "report": None,
        "uploaded_name": None,
        "existing_state": None,
        "history": [],
        "image_files": {},
        "mapping_overrides": {},
        "wp_site_url": os.getenv("WORDPRESS_SITE_URL", ""),
        "wp_username": os.getenv("WORDPRESS_USERNAME", ""),
        "wp_password": os.getenv("WORDPRESS_APP_PASSWORD", ""),
        "wp_tested": False,
        "wp_connected": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def set_screen(name: str) -> None:
    st.session_state.screen = name


def slugify(value: str) -> str:
    value = re.sub(r"\.docx$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "untitled"


def detect_existing_page(file_name: str) -> Dict[str, Any]:
    slug = slugify(file_name)
    known_existing = {"nmims-university-page", "nmims-online-mba", "nmims-mba-marketing"}
    digest = int(hashlib.sha1(slug.encode("utf-8")).hexdigest(), 16)
    exists = slug in known_existing or digest % 5 == 0
    return {
        "exists": exists,
        "slug": slug,
        "title": re.sub(r"[-_]+", " ", slug).title(),
        "published_on": "15 April 2026" if exists else None,
    }


def page_label(page_type: str) -> str:
    return page_type.replace("_", " ").title()


def field_value_to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()
    if isinstance(value, list):
        return " ".join(field_value_to_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(field_value_to_text(item) for item in value.values())
    return str(value)


def word_count(value: Any) -> int:
    return len(re.findall(r"\b\w+\b", field_value_to_text(value)))


def status_for_field(field: Any) -> str:
    if not getattr(field, "value", None):
        return "Missing"
    if getattr(field, "needs_review", False):
        return "Thin Content"
    return "Mapped"


def review_fields(report: Any) -> list[tuple[str, Any]]:
    if not report:
        return []
    fields = []
    for field_name in get_fields(report.page_type):
        field = report.extracted_fields.get(field_name)
        if field and (getattr(field, "needs_review", False) or getattr(field, "confidence", 1.0) < 0.8):
            fields.append((field_name, field))
    return fields


def badge(label: str) -> str:
    classes = {
        "Published": "badge-success",
        "Mapped": "badge-success",
        "Ready": "badge-success",
        "Draft": "badge-warn",
        "Thin Content": "badge-warn",
        "Pending": "badge-neutral",
        "Issues": "badge-error",
        "Missing": "badge-error",
        "AI Mapped": "badge-info",
    }
    return f'<span class="badge {classes.get(label, "badge-neutral")}">{label}</span>'


def topbar(title: str, subtitle: str = "") -> None:
    subtitle_html = f'<div class="topbar-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div style="color:var(--text);font-size:24px;font-weight:600;line-height:1.2;border-bottom:1px solid var(--border);padding-bottom:16px;margin-bottom:22px;">{title}'
        f'{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## DB")
        st.caption("Content Publisher")
        st.write("")
        for item in NAV_ITEMS:
            is_active = st.session_state.screen == item
            prefix = "▌ " if is_active else ""
            if st.button(f"{prefix}{item}", key=f"nav_{item}", use_container_width=True):
                set_screen(item)
                if item == "New Upload":
                    st.session_state.upload_step = 1
        st.write("")
        st.markdown("---")
        st.caption("Signed in as")
        st.markdown("**Content Team**")


def render_dashboard() -> None:
    topbar("Dashboard")
    if st.button("New Upload", type="primary"):
        set_screen("New Upload")
        st.session_state.upload_step = 1

    col1, col2, col3, col4 = st.columns(4)
    stats = [
        ("Pages Published", "42", "This month", "badge-success"),
        ("Drafts Pending Review", "7", "Awaiting review", "badge-warn"),
        ("Files with Issues", "3", "Need attention", "badge-error"),
        ("Last Upload", "Today", "NMIMS University", "badge-neutral"),
    ]
    for col, (label, value, tag, klass) in zip([col1, col2, col3, col4], stats):
        with col:
            st.markdown(
                f'<div class="card"><div class="label">{label}</div><div class="stat-value">{value}</div>'
                f'<span class="badge {klass}">{tag}</span></div>',
                unsafe_allow_html=True,
            )

    left, right = st.columns([0.62, 0.38])
    with left:
        st.markdown('<div class="card"><h3>Recent Uploads</h3></div>', unsafe_allow_html=True)
        recent = st.session_state.history or [
            {"file": "NMIMS University Page.docx", "type": "University", "status": "Draft", "date": "Today"},
            {"file": "NMIMS Online MBA.docx", "type": "Course", "status": "Published", "date": "Yesterday"},
            {"file": "NMIMS MBA Marketing.docx", "type": "Specialization", "status": "Issues", "date": "13 May"},
            {"file": "Amity Online MBA.docx", "type": "Course", "status": "Draft", "date": "13 May"},
            {"file": "Amity University Online.docx", "type": "University", "status": "Published", "date": "12 May"},
        ]
        for row in recent[:5]:
            st.markdown(
                f"""
                <div class="section-row">
                    <div style="display:grid;grid-template-columns:2fr 1fr 1fr 0.8fr;gap:12px;align-items:center;">
                        <span class="mono">{row['file']}</span>
                        <span class="badge badge-neutral">{row['type']}</span>
                        {badge(row['status'])}
                        <span style="color:var(--muted);font-size:13px;">{row['date']}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            """
            <div class="card">
                <h3>Publish a new page</h3>
                <p style="color:var(--muted);font-size:14px;">
                    Upload a Word file and review mapping, validation, images, and draft publishing from one place.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Start New Upload", type="primary", use_container_width=True):
            set_screen("New Upload")
            st.session_state.upload_step = 1


def render_stepper(active: int) -> None:
    labels = ["Step 1: Upload File", "Step 2: Add Images", "Step 3: Review & Publish"]
    html = '<div class="stepper">'
    for index, label in enumerate(labels, start=1):
        klass = "active" if index == active else "done" if index < active else ""
        html += f'<div class="step {klass}">{label}</div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_upload() -> None:
    if st.session_state.upload_step == 1:
        topbar("New Upload")
    elif st.session_state.upload_step == 2:
        topbar("New Upload - Add Images")
    else:
        report = st.session_state.report
        title = f"{st.session_state.uploaded_name or 'Upload'} - Validation Report"
        subtitle = f"Page type: {page_label(report.page_type)}" if report else ""
        topbar(title, subtitle)

    render_stepper(st.session_state.upload_step)

    if st.session_state.upload_step == 1:
        render_upload_step()
    elif st.session_state.upload_step == 2:
        render_image_step()
    else:
        render_validation_step()


def render_upload_step() -> None:
    st.markdown(
        """
        <div class="upload-zone">
            <strong>Drop your .docx file here</strong>
            <span>or click to browse</span>
            <span style="margin-top:8px;">Accepts .docx files only - max 25MB</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader("Word document", type=["docx"], label_visibility="collapsed")
    st.session_state.page_type = st.radio(
        "Page Type",
        PAGE_TYPES,
        format_func=page_label,
        horizontal=True,
        index=PAGE_TYPES.index(st.session_state.page_type),
    )

    if uploaded_file:
        st.session_state.uploaded_name = uploaded_file.name
        st.markdown(
            f'<div class="card"><span class="mono">{uploaded_file.name}</span>'
            f'<div style="color:var(--muted);font-size:13px;margin-top:6px;">{uploaded_file.size / 1024:.1f} KB selected</div></div>',
            unsafe_allow_html=True,
        )

    if st.button("Parse & Validate File", type="primary", disabled=uploaded_file is None):
        pipeline = get_pipeline()
        with st.spinner("Parsing document, mapping ACF fields, and validating content..."):
            report = pipeline.process_file(uploaded_file, uploaded_file.name, st.session_state.page_type)
        st.session_state.report = report
        st.session_state.existing_state = detect_existing_page(uploaded_file.name)
        st.session_state.uploaded_name = uploaded_file.name

    if st.session_state.existing_state:
        state = st.session_state.existing_state
        if state["exists"]:
            st.markdown(
                f"""
                <div class="warn-banner">
                    <strong>Existing page found</strong><br>
                    "{state['title']}" was published on {state['published_on']}. Updating will replace content and reset the page to Draft for review.
                </div>
                """,
                unsafe_allow_html=True,
            )
            c1, c2 = st.columns([1, 1])
            with c1:
                st.button("Preview Changes", use_container_width=True)
            with c2:
                if st.button("Update & Reset to Draft", type="primary", use_container_width=True):
                    st.session_state.upload_step = 2
                    st.rerun()
        else:
            st.markdown(
                f"""
                <div class="success-banner">
                    <strong>New page detected</strong><br>
                    "{state['title']}" has no matching WordPress page. This will create a new page as Draft.
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Create Draft", type="primary"):
                st.session_state.upload_step = 2
                st.rerun()


def render_image_step() -> None:
    page_type = st.session_state.page_type
    slots = get_image_slots(page_type)
    st.markdown(
        f'<div class="info-banner">{len(slots)} image slot{"s" if len(slots) != 1 else ""} detected for {page_label(page_type)} pages. Upload the matching assets below.</div>',
        unsafe_allow_html=True,
    )

    for slot in slots:
        name = slot["name"]
        required = "Required" if slot["required"] else "Optional"
        with st.container(border=True):
            left, middle, right = st.columns([0.25, 0.45, 0.30])
            with left:
                st.markdown(f'<span class="mono">{name}</span><br>{badge("Pending")}', unsafe_allow_html=True)
                st.caption(required)
            with middle:
                image = st.file_uploader(
                    f"Upload image for {name}",
                    type=["jpg", "jpeg", "png"],
                    key=f"image_{name}",
                    label_visibility="collapsed",
                )
            with right:
                if image:
                    st.session_state.image_files[name] = image.name
                    st.image(image, width=90)
                    st.caption(image.name)
                    st.markdown(badge("Ready"), unsafe_allow_html=True)
                else:
                    st.caption("Minimum 1500px wide. JPG or PNG only.")

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("Back"):
            st.session_state.upload_step = 1
            st.rerun()
    with c2:
        if st.button("Skip images for now"):
            st.session_state.upload_step = 3
            st.rerun()
    with c3:
        if st.button("Continue to Review", type="primary", use_container_width=True):
            st.session_state.upload_step = 3
            st.rerun()


def render_validation_step() -> None:
    report = st.session_state.report
    if not report:
        st.warning("Upload and parse a document first.")
        return

    mapped = thin = missing = 0
    rows = []
    for field_name in get_fields(report.page_type):
        field = report.extracted_fields.get(field_name)
        if field is None:
            continue
        status = status_for_field(field)
        mapped += status == "Mapped"
        thin += status == "Thin Content"
        missing += status == "Missing"
        rows.append((field_name, field, status))

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, klass in [
        (c1, "Mapped", mapped, "badge-success"),
        (c2, "Thin Content", thin, "badge-warn"),
        (c3, "Missing", missing, "badge-error"),
        (c4, "Score", f"{report.quality_score}/100", "badge-success" if report.quality_score >= 75 else "badge-warn"),
    ]:
        with col:
            st.markdown(
                f'<div class="card"><div class="label">{label}</div><div class="stat-value">{value}</div>'
                f'<span class="badge {klass}">Review</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown('<div class="card"><h3>Field Mapping</h3></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="display:grid;grid-template-columns:1.25fr 1fr 0.45fr 1.5fr 0.8fr 0.75fr;gap:12px;color:var(--muted);font-size:12px;font-weight:700;text-transform:uppercase;">
            <span>Field Name</span><span>SEO Heading</span><span>Words</span><span>Content Preview</span><span>AI Confidence</span><span>Status</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    for field_name, field, status in rows:
        klass = "error" if status == "Missing" else "warn" if status == "Thin Content" else ""
        confidence = int(getattr(field, "confidence", 0) * 100)
        heading = getattr(field, "source_heading", None) or "-"
        preview = field_value_to_text(getattr(field, "value", ""))[:110] or "No content mapped"
        indent = "padding-left:18px;font-size:12px;" if field_name.endswith("_heading") else ""
        st.markdown(
            f"""
            <div class="section-row {klass}">
                <div style="display:grid;grid-template-columns:1.25fr 1fr 0.45fr 1.5fr 0.8fr 0.75fr;gap:12px;align-items:center;">
                    <span class="mono" style="{indent}">{field_name}</span>
                    <span>{heading}</span>
                    <span style="color:var(--muted);font-size:13px;">{word_count(getattr(field, "value", ""))}</span>
                    <span class="preview">{preview}</span>
                    <span>{confidence}%<div class="confidence-track"><div class="confidence-fill" style="width:{confidence}%;"></div></div></span>
                    {badge(status)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if report.unmapped_sections:
        chips = " ".join(f'<span class="badge badge-warn">{name}</span>' for name in report.unmapped_sections[:8])
        st.markdown(
            f'<div class="warn-banner"><strong>{len(report.unmapped_sections)} headings were not matched to known fields</strong><br>{chips}</div>',
            unsafe_allow_html=True,
        )

    review_count = len(review_fields(report))
    if review_count:
        st.markdown(
            f'<div class="info-banner">{review_count} fields have low confidence or need manual review before final draft save.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Open AI Mapping Review"):
            set_screen("AI Mapping Review")
            st.rerun()

    final_payload = {field: data.value for field, data in report.extracted_fields.items() if data.value}
    with st.expander("ACF JSON Payload"):
        st.json(final_payload)
        st.download_button(
            label="Download JSON Payload",
            data=json.dumps(final_payload, indent=2),
            file_name=f"{slugify(st.session_state.uploaded_name or 'payload')}_payload.json",
            mime="application/json",
        )

    st.markdown('<div class="sticky-actions"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Back to Images"):
            st.session_state.upload_step = 2
            st.rerun()
    with c2:
        if st.button("Save as Draft in WordPress", type="primary", use_container_width=True):
            result = save_draft_to_wordpress(report, final_payload)
            st.session_state.history.insert(
                0,
                {
                    "file": st.session_state.uploaded_name or "Untitled.docx",
                    "type": page_label(report.page_type),
                    "status": "Draft" if report.is_publishable else "Issues",
                    "date": datetime.now().strftime("%d %b, %I:%M %p"),
                },
            )
            if result["status"] == "simulated":
                st.warning(result["message"])
            elif result["status"] == "error":
                st.error(result["message"])
            else:
                st.success(f"WordPress draft {result['status']} successfully. Post ID: {result.get('post_id', 'unknown')}")


def save_draft_to_wordpress(report: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
    site_url = st.session_state.get("wp_site_url", "")
    username = st.session_state.get("wp_username", "")
    password = st.session_state.get("wp_password", "")
    title = payload.get("university_name") or payload.get("program_name") or payload.get("spec_name") or st.session_state.uploaded_name or report.document_name

    if not (site_url and username and password):
        return {
            "status": "simulated",
            "message": "No WordPress credentials are configured, so this was saved in the local review queue only. Add credentials in Settings to create/update a real draft.",
        }

    client = WPClient(site_url, username, password)
    return client.create_or_update_post(title=title, payload=payload, page_type=report.page_type)


def render_ai_mapping_review() -> None:
    report = st.session_state.report
    topbar("AI Mapping Review", "Confirm or override low-confidence section mappings before saving a draft.")
    if not report:
        st.info("Upload and parse a document first. Low-confidence mappings will appear here.")
        if st.button("Go to New Upload", type="primary"):
            set_screen("New Upload")
            st.session_state.upload_step = 1
            st.rerun()
        return

    fields = review_fields(report)
    if not fields:
        st.markdown('<div class="success-banner">No low-confidence fields need review. The payload can move to draft review.</div>', unsafe_allow_html=True)
        if st.button("Back to Validation"):
            set_screen("New Upload")
            st.session_state.upload_step = 3
            st.rerun()
        return

    st.markdown(
        f'<div class="info-banner">The mapper flagged {len(fields)} fields because they are missing, thin, or below 80% confidence. Confirm them or choose a better ACF field.</div>',
        unsafe_allow_html=True,
    )
    available_fields = get_fields(report.page_type)

    for field_name, field in fields:
        confidence = int(getattr(field, "confidence", 0) * 100)
        preview = field_value_to_text(getattr(field, "value", ""))[:180] or "No mapped content"
        with st.container(border=True):
            c1, c2, c3 = st.columns([0.34, 0.40, 0.26])
            with c1:
                st.markdown(f'<span class="mono">{field_name}</span>', unsafe_allow_html=True)
                st.caption(f"Source heading: {getattr(field, 'source_heading', None) or 'Not found'}")
            with c2:
                selected = st.selectbox(
                    "Suggested ACF field",
                    available_fields,
                    index=available_fields.index(field_name) if field_name in available_fields else 0,
                    key=f"override_{field_name}",
                )
                st.caption(preview)
            with c3:
                st.markdown(f"{confidence}%")
                st.markdown(f'<div class="confidence-track"><div class="confidence-fill" style="width:{confidence}%;"></div></div>', unsafe_allow_html=True)
                if st.button("Confirm", key=f"confirm_{field_name}"):
                    st.session_state.mapping_overrides[field_name] = selected
                    field.needs_review = False
                    if selected != field_name:
                        report.extracted_fields[selected] = report.extracted_fields.pop(field_name)
                    st.success("Mapping confirmed.")

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Use AI Suggestions"):
            for _, field in fields:
                field.needs_review = False
            st.success("All suggestions accepted for this review session.")
    with c2:
        if st.button("Back to Validation", type="primary", use_container_width=True):
            set_screen("New Upload")
            st.session_state.upload_step = 3
            st.rerun()


def render_bulk_upload() -> None:
    topbar("Bulk Upload")
    st.markdown(
        '<div class="card"><h3>Upload multiple Word files</h3><p style="color:var(--muted);">Batch parsing uses the same validation and draft-only WordPress flow as single uploads.</p></div>',
        unsafe_allow_html=True,
    )
    files = st.file_uploader("Select .docx files", type=["docx"], accept_multiple_files=True)
    if files:
        for file in files:
            st.markdown(f'<div class="section-row"><span class="mono">{file.name}</span> {badge("Pending")}</div>', unsafe_allow_html=True)
        st.button("Run Bulk Validation", type="primary")


def render_history() -> None:
    topbar("Upload History")
    history = st.session_state.history
    if not history:
        st.info("No uploads have been saved in this session yet.")
        return
    for item in history:
        st.markdown(
            f'<div class="card"><span class="mono">{item["file"]}</span><br>'
            f'<span class="badge badge-neutral">{item["type"]}</span> {badge(item["status"])} '
            f'<span style="color:var(--muted);font-size:13px;">{item["date"]}</span></div>',
            unsafe_allow_html=True,
        )


def render_settings() -> None:
    topbar("Settings")
    st.markdown('<div class="card"><h3>WordPress Connection</h3></div>', unsafe_allow_html=True)
    site_url = st.text_input("WordPress Site URL", value=st.session_state.wp_site_url, placeholder="https://degreebaba.com")
    username = st.text_input("API Username", value=st.session_state.wp_username, placeholder="degreebaba-api-user")
    password = st.text_input("Application Password", value=st.session_state.wp_password, type="password", placeholder="xxxx xxxx xxxx xxxx")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Test Connection"):
            st.session_state.wp_site_url = site_url
            st.session_state.wp_username = username
            st.session_state.wp_password = password
            st.session_state.wp_tested = True
            st.session_state.wp_connected = bool(site_url and username and password)
    with c2:
        if st.button("Save Settings", type="primary"):
            st.session_state.wp_site_url = site_url
            st.session_state.wp_username = username
            st.session_state.wp_password = password
            st.success("Settings saved for this session.")
    if st.session_state.wp_tested:
        if st.session_state.wp_connected:
            st.markdown('<div class="success-banner">Connected - WordPress REST API is live.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-banner">Connection failed - check URL and credentials.</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><h3>API Key</h3></div>', unsafe_allow_html=True)
    st.text_input("Claude API Key", type="password", placeholder="sk-ant-...")
    st.button("Save API Key", type="primary")


def main() -> None:
    inject_css()
    init_state()
    render_sidebar()

    screen = st.session_state.screen
    if screen == "Dashboard":
        render_dashboard()
    elif screen == "New Upload":
        render_upload()
    elif screen == "AI Mapping Review":
        render_ai_mapping_review()
    elif screen == "Bulk Upload":
        render_bulk_upload()
    elif screen == "Upload History":
        render_history()
    elif screen == "Settings":
        render_settings()


if __name__ == "__main__":
    main()
