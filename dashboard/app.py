import streamlit as st
import requests
from datetime import datetime

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Data Quality Monitor",
    page_icon="🔍",
    layout="wide"
)

API_BASE = "http://127.0.0.1:8000"

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .main { background-color: #0f1117; }

    /* Metric cards */
    div[data-testid="metric-container"] {
        background-color: #1e2130;
        border: 1px solid #2d3250;
        border-radius: 10px;
        padding: 15px;
    }

    /* Anomaly card */
    .anomaly-card {
        background-color: #1e2130;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
    }

    .anomaly-card-high {
        border-left: 5px solid #ff4b4b;
    }

    .anomaly-card-medium {
        border-left: 5px solid #ffa500;
    }

    .badge-high {
        background-color: #ff4b4b22;
        color: #ff4b4b;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid #ff4b4b;
    }

    .badge-medium {
        background-color: #ffa50022;
        color: #ffa500;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        border: 1px solid #ffa500;
    }

    .badge-check {
        background-color: #4b7bff22;
        color: #4b7bff;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        border: 1px solid #4b7bff;
    }

    .card-title {
        font-size: 18px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 8px;
    }

    .llm-explanation {
        background-color: #12151f;
        border-radius: 8px;
        padding: 14px;
        color: #c8ccd8;
        font-size: 14px;
        line-height: 1.6;
        margin-top: 12px;
    }

    .explanation-label {
        color: #4b7bff;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .divider {
        border: none;
        border-top: 1px solid #2d3250;
        margin: 20px 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161824;
        border-right: 1px solid #2d3250;
    }

    /* Hide default Streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔍 Data Quality Monitor")
    st.markdown("---")
    st.markdown("Automated anomaly detection powered by statistical checks and LLM-generated explanations.")
    st.markdown("---")

    st.markdown("### Pipeline")
    st.markdown("- Olist Brazilian E-commerce")
    st.markdown("- 3 tables monitored")
    st.markdown("- Checks: nulls, duplicates, outliers")
    st.markdown("- LLM: Gemini 3.6 Flash")
    st.markdown("---")

    run_button = st.button("Run Quality Check", type="primary", use_container_width=True)

    st.markdown("---")

    # API health status
    try:
        health = requests.get(f"{API_BASE}/health", timeout=3)
        if health.status_code == 200:
            st.success("API: Online")
            last_run = health.json().get("last_run")
            if last_run:
                st.caption(f"Last run: {last_run[:19].replace('T', ' ')}")
            else:
                st.caption("Last run: Never")
        else:
            st.error("API: Offline")
    except:
        st.error("API: Offline")
        st.caption("Make sure uvicorn is running")


# ── Main content ─────────────────────────────────────────────
st.markdown("# AI Data Quality Monitor")
st.markdown("Real-time anomaly detection with AI-powered explanations")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# run check when button clicked
if run_button:
    with st.spinner("Running quality checks and generating AI explanations..."):
        try:
            response = requests.post(f"{API_BASE}/run-check", timeout=60)
            if response.status_code == 200:
                st.session_state["report"] = response.json()
                st.success("Quality check complete.")
            else:
                st.error(f"API error: {response.status_code}")
        except Exception as e:
            st.error(f"Could not reach API: {e}")

# load latest report if exists and no new run
if "report" not in st.session_state:
    try:
        response = requests.get(f"{API_BASE}/latest-report", timeout=5)
        if response.status_code == 200:
            st.session_state["report"] = response.json()
    except:
        pass

# ── Display report ───────────────────────────────────────────
if "report" in st.session_state:
    data = st.session_state["report"]
    report = data.get("report", [])
    run_time = data.get("run_time", "")

    # metric cards
    high_count = sum(1 for r in report if r.get("severity") == "high")
    medium_count = sum(1 for r in report if r.get("severity") == "medium")
    tables = list(set(r.get("table") for r in report))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Anomalies Found", len(report))
    with col2:
        st.metric("High Severity", high_count)
    with col3:
        st.metric("Medium Severity", medium_count)
    with col4:
        st.metric("Tables Scanned", 3)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("### Anomaly Report")

    if len(report) == 0:
        st.success("No anomalies detected. All checks passed.")
    else:
        for item in report:
            severity = item.get("severity", "medium")
            card_class = f"anomaly-card anomaly-card-{severity}"
            badge_class = f"badge-{severity}"

            st.markdown(f"""
            <div class="{card_class}">
                <div class="card-title">
                    {item.get('table')} &nbsp;/&nbsp; {item.get('column')}
                </div>
                <span class="{badge_class}">{severity.upper()}</span>
                &nbsp;
                <span class="badge-check">{item.get('check_type', '').replace('_', ' ').upper()}</span>
                &nbsp;
                <span style="color:#888; font-size:13px;">Value: {item.get('value')}</span>
                <div class="explanation-label" style="margin-top:14px;">AI Explanation</div>
                <div class="llm-explanation">{item.get('llm_explanation', 'No explanation available.')}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    # empty state
    st.markdown("""
    <div style="text-align:center; padding:60px 0; color:#555;">
        <div style="font-size:48px;">🔍</div>
        <div style="font-size:20px; margin-top:16px; color:#888;">No report yet</div>
        <div style="font-size:14px; margin-top:8px; color:#555;">Click "Run Quality Check" in the sidebar to get started</div>
    </div>
    """, unsafe_allow_html=True)