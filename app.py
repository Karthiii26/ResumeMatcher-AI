import streamlit as st
import os
from matcher import analyze_resume_and_jd

st.set_page_config(
    page_title="ResumeMatch AI",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global reset to white/light ── */
    html, body,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMain"],
    [data-testid="stHeader"],
    .stApp {
        background-color: #F9FAFB !important;
        color: #111827 !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Typography ── */
    p, li, span, div, label {
        font-family: 'Inter', sans-serif !important;
        color: #374151 !important;
    }
    h1, h2, h3, h4 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        color: #111827 !important;
    }

    /* ── Hide Streamlit chrome ── */
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Page header block ── */
    .page-header {
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 20px;
        margin-bottom: 32px;
    }
    .page-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #111827 !important;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .page-sub {
        font-size: 0.9rem;
        color: #6B7280 !important;
        margin-top: 4px;
    }

    /* ── Form labels ── */
    .stTextArea label,
    .stFileUploader label {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* ── Textarea ── */
    .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.08) !important;
    }
    .stTextArea textarea::placeholder {
        color: #9CA3AF !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background-color: #FFFFFF !important;
        border: 1px dashed #D1D5DB !important;
        border-radius: 8px !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #6B7280 !important;
        font-size: 0.88rem !important;
    }

    /* ── Primary button ── */
    .stButton > button {
        background-color: #1D4ED8 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1.4rem !important;
        letter-spacing: 0.01em !important;
        transition: background-color 0.15s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stButton > button:hover {
        background-color: #1E40AF !important;
    }

    /* ── Alerts ── */
    [data-testid="stSuccess"] {
        background-color: #F0FDF4 !important;
        border: 1px solid #BBF7D0 !important;
        border-radius: 8px !important;
        color: #166534 !important;
    }
    [data-testid="stSuccess"] p { color: #166534 !important; }

    [data-testid="stError"] {
        background-color: #FEF2F2 !important;
        border: 1px solid #FECACA !important;
        border-radius: 8px !important;
        color: #991B1B !important;
    }
    [data-testid="stError"] p { color: #991B1B !important; }

    [data-testid="stInfo"] {
        background-color: #EFF6FF !important;
        border: 1px solid #BFDBFE !important;
        border-radius: 8px !important;
    }
    [data-testid="stInfo"] p { color: #1E40AF !important; }

    /* ── Spinner ── */
    [data-testid="stSpinner"] > div { border-top-color: #1D4ED8 !important; }

    /* ── Score card ── */
    .score-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 28px 24px;
        text-align: center;
    }
    .score-number {
        font-size: 3.5rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.04em;
        line-height: 1;
    }
    .score-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 6px;
    }

    /* ── Metric row ── */
    .metrics-row {
        display: flex;
        gap: 12px;
        margin-top: 0;
    }
    .metric-box {
        flex: 1;
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 16px 12px;
        text-align: center;
    }
    .metric-box .m-num {
        font-size: 2rem;
        font-weight: 700;
        font-family: 'Inter', sans-serif;
        color: #111827 !important;
        line-height: 1.1;
    }
    .metric-box .m-label {
        font-size: 0.78rem;
        font-weight: 500;
        color: #6B7280 !important;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .metric-box .m-sub {
        font-size: 0.72rem;
        color: #9CA3AF !important;
        margin-top: 1px;
    }

    /* ── Tabs ── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: #F3F4F6 !important;
        border-radius: 8px !important;
        padding: 4px !important;
        gap: 2px !important;
        border: 1px solid #E5E7EB !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        background-color: transparent !important;
        color: #6B7280 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        padding: 6px 14px !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        font-weight: 600 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-panel"] {
        background-color: #F9FAFB !important;
        padding-top: 20px !important;
    }

    /* ── Expanders ── */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 8px !important;
        margin-bottom: 6px !important;
    }
    [data-testid="stExpander"] summary {
        color: #374151 !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #1D4ED8 !important;
    }

    /* ── Divider ── */
    hr { border-color: #E5E7EB !important; }

    /* ── Status pill ── */
    .pill {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        margin-bottom: 10px;
    }
    .pill-green  { background: #DCFCE7; color: #166534 !important; border: 1px solid #BBF7D0; }
    .pill-yellow { background: #FEF9C3; color: #854D0E !important; border: 1px solid #FDE68A; }
    .pill-red    { background: #FEE2E2; color: #991B1B !important; border: 1px solid #FECACA; }

    /* ── Snippet ── */
    .snippet {
        background: #F9FAFB;
        border-left: 3px solid #2563EB;
        padding: 10px 14px;
        font-size: 0.87rem;
        color: #374151 !important;
        border-radius: 0 6px 6px 0;
        margin-top: 10px;
        font-style: italic;
    }
    .snippet code {
        font-size: 0.75rem;
        color: #2563EB !important;
        font-style: normal;
        margin-left: 6px;
        background: #EFF6FF;
        padding: 1px 5px;
        border-radius: 4px;
    }

    /* ── Section label ── */
    .section-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #6B7280 !important;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ── Page header ────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <p class="page-title">ResumeMatch AI</p>
  <p class="page-sub">Upload your resume and a job description to receive a semantic compatibility analysis.</p>
</div>
""", unsafe_allow_html=True)

# ── Inputs ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2, gap="large")

with col_left:
    uploaded_file = st.file_uploader(
        "Resume",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=False,
        help="PDF, DOCX, or plain-text formats accepted."
    )

with col_right:
    jd_text = st.text_area(
        "Job Description",
        height=200,
        placeholder="Paste the job description here — requirements, responsibilities, preferred qualifications…",
    )

st.write("")
_, btn_col, _ = st.columns([0.35, 0.3, 0.35])
with btn_col:
    analyze_button = st.button("Analyze", use_container_width=True)

# ── Analysis ────────────────────────────────────────────────────────────────
if analyze_button:
    if not uploaded_file:
        st.error("Please upload a resume file to continue.")
    elif not jd_text or not jd_text.strip():
        st.error("Please paste a job description to match against.")
    else:
        with st.spinner("Analyzing…"):
            try:
                results = analyze_resume_and_jd(
                    resume_file=uploaded_file,
                    filename=uploaded_file.name,
                    jd_text=jd_text
                )

                st.divider()

                # ── Score row ─────────────────────────────────────────────
                score = results["overall_score"]
                n_s   = len(results["strong_matches"])
                n_p   = len(results["partial_matches"])
                n_m   = len(results["missing_matches"])

                if score >= 70:
                    score_color, score_tag = "#16A34A", "Strong Match"
                elif score >= 45:
                    score_color, score_tag = "#D97706", "Moderate Match"
                else:
                    score_color, score_tag = "#DC2626", "Weak Match"

                col_score, col_metrics = st.columns([0.28, 0.72], gap="large")

                with col_score:
                    st.markdown(f"""
                    <div class="score-card">
                      <div class="score-number" style="color:{score_color};">{score}%</div>
                      <div class="score-label" style="color:{score_color};">{score_tag}</div>
                      <div style="font-size:0.78rem;color:#9CA3AF;margin-top:10px;">Overall compatibility</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col_metrics:
                    st.markdown(f"""
                    <div class="metrics-row">
                      <div class="metric-box">
                        <div class="m-num" style="color:#16A34A;">{n_s}</div>
                        <div class="m-label">Strong</div>
                        <div class="m-sub">matched requirements</div>
                      </div>
                      <div class="metric-box">
                        <div class="m-num" style="color:#D97706;">{n_p}</div>
                        <div class="m-label">Partial</div>
                        <div class="m-sub">related but implicit</div>
                      </div>
                      <div class="metric-box">
                        <div class="m-num" style="color:#DC2626;">{n_m}</div>
                        <div class="m-label">Missing</div>
                        <div class="m-sub">not found in resume</div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.write("")

                # ── Tabs ──────────────────────────────────────────────────
                tab_s, tab_p, tab_m, tab_sug = st.tabs([
                    f"Strong ({n_s})",
                    f"Partial ({n_p})",
                    f"Missing ({n_m})",
                    "Suggestions"
                ])

                with tab_s:
                    if not results["strong_matches"]:
                        st.info("No strong matches found. Consider aligning your resume language more closely with the job description.")
                    for m in results["strong_matches"]:
                        with st.expander(m["jd_requirement"][:100]):
                            st.markdown(f"**Requirement:** {m['jd_requirement']}")
                            st.markdown(f"<span class='pill pill-green'>{m['similarity_score']}% match &nbsp;·&nbsp; {m['category']}</span>", unsafe_allow_html=True)
                            st.markdown("**Matched from your resume:**")
                            st.markdown(f"<div class='snippet'>{m['best_match_text']}<code>{m['best_match_section']}</code></div>", unsafe_allow_html=True)

                with tab_p:
                    if not results["partial_matches"]:
                        st.info("No partial matches.")
                    for m in results["partial_matches"]:
                        with st.expander(m["jd_requirement"][:100]):
                            st.markdown(f"**Requirement:** {m['jd_requirement']}")
                            st.markdown(f"<span class='pill pill-yellow'>{m['similarity_score']}% match &nbsp;·&nbsp; {m['category']}</span>", unsafe_allow_html=True)
                            st.markdown("**Closest resume content:**")
                            st.markdown(f"<div class='snippet'>{m['best_match_text']}<code>{m['best_match_section']}</code></div>", unsafe_allow_html=True)

                with tab_m:
                    if not results["missing_matches"]:
                        st.success("No missing requirements — your resume covers this role well.")
                    for m in results["missing_matches"]:
                        with st.expander(m["jd_requirement"][:100]):
                            st.markdown(f"**Requirement:** {m['jd_requirement']}")
                            st.markdown(f"<span class='pill pill-red'>{m['similarity_score']}% match &nbsp;·&nbsp; {m['category']}</span>", unsafe_allow_html=True)

                with tab_sug:
                    if not results["suggestions"]:
                        st.success("No improvements needed — your resume is well-aligned.")
                    for sug in results["suggestions"]:
                        st.markdown(sug)
                        st.divider()

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)
