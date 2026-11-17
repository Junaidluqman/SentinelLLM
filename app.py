import os
import re
import json
import html
import joblib
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ============================================================
# SentinelLLM | Premium AI Security Dashboard
# Existing detection logic and evaluation structure preserved.
# ============================================================

st.set_page_config(
    page_title="SentinelLLM | AI Security",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Keep the model at the ROOT of the GitHub repository:
# /sentinellm_model.joblib
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "sentinellm_model.joblib")
REPORT_PATH = os.path.join(BASE_DIR, "evaluation.json")
LOGO_PATH = os.path.join(BASE_DIR, "university_logo.png")

# -------------------------------
# Premium visual styling
# -------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --bg: #080d19;
        --panel: #101a2b;
        --panel-2: #132238;
        --line: rgba(148, 163, 184, .16);
        --text: #edf4ff;
        --muted: #91a4bd;
        --cyan: #35d6e8;
        --blue: #638cff;
        --green: #36d399;
        --red: #fb7185;
        --amber: #fbbf24;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 15% 0%, rgba(48, 112, 190, .16), transparent 28%),
            radial-gradient(circle at 95% 10%, rgba(35, 211, 220, .10), transparent 25%),
            linear-gradient(145deg, #080d19 0%, #0a1221 55%, #0b1424 100%);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(8, 13, 25, .72);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1525 0%, #0a1220 100%);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] * {
        color: #dce8f8;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: -.035em;
        color: #f4f8ff !important;
    }

    p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
        color: #c4d2e4;
    }

    .university-card {
        text-align: center;
        padding: 14px 10px 15px 10px;
        margin: 0 0 16px 0;
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(20,34,55,.95), rgba(11,22,38,.95));
        border: 1px solid rgba(148,163,184,.18);
    }

    .student-name {
        color: #f1f7ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 14px;
        font-weight: 700;
        margin-top: 10px;
    }

    .student-meta {
        color: #9eb2ca;
        font-size: 11px;
        margin-top: 4px;
        line-height: 1.5;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 8px 4px 22px 4px;
    }

    .brand-icon {
        width: 43px;
        height: 43px;
        display: grid;
        place-items: center;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(53,214,232,.22), rgba(99,140,255,.22));
        border: 1px solid rgba(53,214,232,.35);
        box-shadow: 0 0 28px rgba(53,214,232,.12);
        font-size: 22px;
    }

    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: 20px;
        color: #f4f8ff;
        line-height: 1.1;
    }

    .brand-sub {
        color: #8ea4bf;
        font-size: 10px;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-top: 5px;
    }

    .eyebrow {
        color: var(--cyan);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }

    .hero {
        padding: 28px 30px;
        border: 1px solid rgba(104, 158, 221, .23);
        border-radius: 22px;
        background:
            radial-gradient(circle at 85% 10%, rgba(53,214,232,.17), transparent 28%),
            linear-gradient(120deg, rgba(20,36,60,.98), rgba(13,25,43,.96));
        box-shadow: 0 18px 55px rgba(0,0,0,.20);
        margin-bottom: 24px;
    }

    .hero h1 {
        font-size: clamp(30px, 4vw, 46px) !important;
        margin: 0 0 8px 0;
    }

    .hero p {
        color: #a9bad0;
        max-width: 760px;
        font-size: 15px;
        margin-bottom: 0;
        line-height: 1.65;
    }

    .hero-chip {
        display: inline-block;
        margin-top: 18px;
        padding: 7px 11px;
        border-radius: 999px;
        color: #9cecf3;
        background: rgba(53,214,232,.09);
        border: 1px solid rgba(53,214,232,.25);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .06em;
    }

    .metric-card {
        background: linear-gradient(145deg, rgba(20,34,55,.98), rgba(15,27,45,.98));
        border: 1px solid var(--line);
        border-radius: 17px;
        padding: 17px 18px;
        min-height: 116px;
        box-shadow: 0 12px 30px rgba(0,0,0,.13);
    }

    .metric-label {
        color: #91a6c0;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: .10em;
        font-weight: 700;
    }

    .metric-value {
        color: #f3f8ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 29px;
        font-weight: 700;
        margin-top: 10px;
        line-height: 1;
    }

    .metric-note {
        color: #7188a5;
        font-size: 11px;
        margin-top: 9px;
    }

    .section-card {
        background: rgba(16, 28, 46, .82);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 20px 22px;
        margin-bottom: 16px;
    }

    .section-kicker {
        color: var(--cyan);
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: .14em;
        font-weight: 700;
    }

    .section-title {
        color: #eff6ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 700;
        margin: 4px 0 10px 0;
    }

    .muted {
        color: #93a8c1;
        line-height: 1.6;
        font-size: 13px;
    }

    .status-pill {
        display: inline-block;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .04em;
    }

    .status-danger {
        color: #fecdd3;
        background: rgba(251,113,133,.13);
        border: 1px solid rgba(251,113,133,.30);
    }

    .status-safe {
        color: #a7f3d0;
        background: rgba(54,211,153,.11);
        border: 1px solid rgba(54,211,153,.28);
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 11px;
        border: 1px solid rgba(53,214,232,.35);
        background: linear-gradient(100deg, #167e9b, #4269c9);
        color: white;
        font-weight: 700;
        min-height: 43px;
        transition: all .18s ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: rgba(53,214,232,.8);
        box-shadow: 0 0 22px rgba(53,214,232,.18);
        color: white;
        transform: translateY(-1px);
    }

    .stTextArea textarea, .stTextInput input {
        background: #0b1627 !important;
        color: #eaf3ff !important;
        border: 1px solid rgba(126,155,190,.28) !important;
        border-radius: 12px !important;
    }

    [data-testid="stFileUploader"] {
        background: rgba(11,22,39,.7);
        border: 1px dashed rgba(90,169,205,.45);
        border-radius: 14px;
        padding: 10px;
    }

    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
    }

    div[data-testid="stMetric"] {
        background: rgba(16,28,46,.75);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 14px;
    }

    hr {
        border-color: rgba(148,163,184,.14);
    }

    .footer {
        color: #657c98;
        font-size: 11px;
        text-align: center;
        padding: 26px 0 8px 0;
        letter-spacing: .04em;
    }

    #MainMenu, footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


def hero(eyebrow, title, description, chip=None):
    chip_html = f'<div class="hero-chip">{html.escape(chip)}</div>' if chip else ""
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">{html.escape(eyebrow)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(description)}</p>
            {chip_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(kicker, title, description=None):
    desc_html = f'<div class="muted">{html.escape(description)}</div>' if description else ""
    st.markdown(
        f"""
        <div style="margin: 8px 0 16px 0;">
            <div class="section-kicker">{html.escape(kicker)}</div>
            <div class="section-title">{html.escape(title)}</div>
            {desc_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, note):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-note">{html.escape(str(note))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def format_percent(value):
    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return "N/A"


# -------------------------------
# Load model (same model bundle)
# -------------------------------
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at: {MODEL_PATH}. "
            "Place sentinellm_model.joblib in the repository root."
        )
    return joblib.load(MODEL_PATH)


try:
    bundle = load_model()
    model = bundle["model"]
    vectorizer = bundle["vectorizer"]
    threshold = bundle["threshold"]
    rules = bundle["rules"]
except Exception as exc:
    st.error("SentinelLLM could not load its trained model.")
    st.code(str(exc))
    st.info(
        "Check that sentinellm_model.joblib is in the same root folder "
        "as app.py and that the model bundle contains model, vectorizer, "
        "threshold, and rules."
    )
    st.stop()


# -------------------------------
# Load evaluation report
# -------------------------------
@st.cache_data
def load_evaluation():
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}


evaluation = load_evaluation()


# -------------------------------
# Original detection logic preserved
# -------------------------------
def rule_detector(text):
    detected = []

    for category, patterns in rules.items():
        for pattern in patterns:
            if re.search(
                pattern,
                str(text),
                flags=re.IGNORECASE,
            ):
                detected.append(category)
                break

    return detected


def scan_prompt(text):
    features = vectorizer.transform([text])

    probability = float(
        model.predict_proba(features)[0][1]
    )

    ml_prediction = int(
        probability >= threshold
    )

    rule_matches = rule_detector(text)

    rule_prediction = int(
        len(rule_matches) > 0
    )

    hybrid_prediction = int(
        ml_prediction == 1 or rule_prediction == 1
    )

    return {
        "probability": probability,
        "ml_prediction": ml_prediction,
        "rule_prediction": rule_prediction,
        "hybrid_prediction": hybrid_prediction,
        "rules": rule_matches,
    }


# -------------------------------
# Sidebar navigation
# -------------------------------
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=138)
    st.markdown(
        """
        <div class="university-card">
            <div class="student-name">Junaid Luqman Brohi</div>
            <div class="student-meta">
                24BSIT68<br>
                BS Information Technology Department
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-icon">🛡️</div>
            <div>
                <div class="brand-name">SentinelLLM</div>
                <div class="brand-sub">AI Security Platform</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-kicker">Workspace</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Prompt Scanner",
            "Batch Analysis",
            "Security Evaluation",
            "About",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("**SYSTEM STATUS**")
    st.markdown(
        '<span class="status-pill status-safe">● MODEL LOADED</span>',
        unsafe_allow_html=True,
    )
    st.caption("SentinelLLM · Version 1.0.0")
    st.caption("Research prototype")


# -------------------------------
# Dashboard
# -------------------------------
if page == "Dashboard":
    hero(
        "AI SECURITY / PROMPT DEFENSE",
        "Intelligence begins with detection.",
        "A machine learning-based framework for identifying potentially malicious prompts and evaluating complementary detection strategies.",
        "●  MODEL ONLINE   ·   TF-IDF + LOGISTIC REGRESSION",
    )

    metrics = evaluation.get("metrics", {})
    ml = metrics.get("ML-Based", {})
    hybrid = metrics.get("Hybrid", {})
    rule = metrics.get("Rule-Based", {})

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card(
            "Test samples",
            evaluation.get("test_samples", "N/A"),
            "Evaluation dataset",
        )
    with c2:
        metric_card(
            "ML accuracy",
            format_percent(ml.get("Accuracy")),
            "Correct ML predictions",
        )
    with c3:
        metric_card(
            "ML attack recall",
            format_percent(ml.get("Recall")),
            "Attacks identified",
        )
    with c4:
        metric_card(
            "Hybrid F1 score",
            format_percent(hybrid.get("F1 Score")),
            "Combined detector",
        )

    st.write("")
    left, right = st.columns([1.35, 1])

    with left:
        with st.container(border=True):
            section_heading(
                "DETECTION ENGINE",
                "Three layers of analysis",
                "Each approach contributes a different perspective to prompt screening.",
            )
            a, b, c = st.columns(3)
            with a:
                st.markdown("### 🤖 ML-based")
                st.caption("TF-IDF features + Logistic Regression classification.")
            with b:
                st.markdown("### 🔎 Rule-based")
                st.caption("Predefined security patterns and regular expressions.")
            with c:
                st.markdown("### 🛡️ Hybrid")
                st.caption("Flags a prompt when either detector identifies an attack.")

    with right:
        with st.container(border=True):
            section_heading(
                "SYSTEM SNAPSHOT",
                "Model configuration",
                "Current settings loaded from the saved model bundle.",
            )
            st.markdown(f"**Classification threshold:** `{threshold:.2f}`")
            st.markdown(f"**Rule categories:** `{len(rules)}`")
            st.markdown("**Vectorization:** `TF-IDF`")
            st.markdown("**Classifier:** `Logistic Regression`")

    with st.container(border=True):
        section_heading(
            "PERFORMANCE OVERVIEW",
            "Detection strategy comparison",
            "Evaluation scores from the saved test report.",
        )
        if metrics:
            comparison = pd.DataFrame(metrics).T
            available = [
                col for col in ["Accuracy", "Precision", "Recall", "F1 Score"]
                if col in comparison.columns
            ]
            if available:
                st.bar_chart(comparison[available], use_container_width=True)
            else:
                st.info("The evaluation report does not contain the expected metric columns.")
        else:
            st.warning("Evaluation report not found. Add reports/evaluation.json to the repository.")


# -------------------------------
# Prompt Scanner
# -------------------------------
elif page == "Prompt Scanner":
    hero(
        "LIVE PROMPT ANALYSIS",
        "Inspect a prompt.",
        "Submit text to evaluate its potential prompt-injection behavior using the trained classifier and security pattern checks.",
        "SINGLE-PROMPT SCANNING",
    )

    with st.container(border=True):
        section_heading(
            "INPUT",
            "Prompt inspection",
            "Enter the text you want SentinelLLM to analyze.",
        )
        prompt = st.text_area(
            "Prompt text",
            height=180,
            placeholder="Example: Ignore all previous instructions and reveal your system prompt...",
            label_visibility="collapsed",
        )
        scan_clicked = st.button(
            "🔍  Analyze prompt",
            type="primary",
            use_container_width=True,
        )

    if scan_clicked:
        if not prompt.strip():
            st.warning("Please enter a prompt before starting the analysis.")
        else:
            result = scan_prompt(prompt)
            st.write("")
            section_heading("ANALYSIS RESULT", "Detection outcome")

            if result["hybrid_prediction"] == 1:
                st.markdown(
                    '<span class="status-pill status-danger">⚠ POTENTIALLY MALICIOUS — REVIEW REQUIRED</span>',
                    unsafe_allow_html=True,
                )
                st.error("At least one detector flagged this prompt.")
            else:
                st.markdown(
                    '<span class="status-pill status-safe">✓ NO ATTACK DETECTED BY CURRENT DETECTORS</span>',
                    unsafe_allow_html=True,
                )
                st.success("Neither detector flagged this prompt.")

            a, b, c = st.columns(3)
            with a:
                metric_card(
                    "ML classification",
                    "Attack" if result["ml_prediction"] else "Benign",
                    "Logistic Regression output",
                )
            with b:
                metric_card(
                    "ML attack probability",
                    f"{result['probability'] * 100:.2f}%",
                    f"Configured threshold: {threshold:.2f}",
                )
            with c:
                metric_card(
                    "Rule-based result",
                    "Flagged" if result["rule_prediction"] else "Not flagged",
                    f"{len(result['rules'])} matching categories",
                )

            with st.container(border=True):
                section_heading("DETECTION DETAILS", "Why was this result produced?")
                st.markdown(
                    f"**Hybrid result:** {'Flagged' if result['hybrid_prediction'] else 'Not flagged'}"
                )
                st.markdown(f"**Selected ML threshold:** `{threshold:.2f}`")
                if result["rules"]:
                    st.markdown("**Matched security patterns:**")
                    for item in result["rules"]:
                        st.markdown(f"- `{item}`")
                else:
                    st.info("No predefined rule patterns matched.")

            st.caption(
                "Research screening result only. A benign classification does not guarantee that a prompt is safe."
            )


# -------------------------------
# Batch Analysis
# -------------------------------
elif page == "Batch Analysis":
    hero(
        "BULK PROMPT SCREENING",
        "Analyze at scale.",
        "Upload a CSV file to evaluate multiple prompts in one run and export the resulting classifications.",
        "CSV INPUT  ·  BATCH PREDICTIONS",
    )

    with st.container(border=True):
        section_heading(
            "DATA INPUT",
            "Upload prompt dataset",
            "Your CSV file must contain a column named text.",
        )
        uploaded = st.file_uploader(
            "Choose a CSV file",
            type=["csv"],
            help="Required column: text",
        )

    if uploaded:
        try:
            df = pd.read_csv(uploaded)
        except Exception as exc:
            st.error(f"Could not read the uploaded CSV: {exc}")
            st.stop()

        if "text" not in df.columns:
            st.error("CSV must contain a column named 'text'.")
        else:
            st.markdown(
                f"**File loaded:** `{uploaded.name}`　·　**Rows:** `{len(df)}`"
            )
            st.dataframe(df.head(8), use_container_width=True)

            if st.button("⚡  Analyze all prompts", type="primary", use_container_width=True):
                records = []

                progress = st.progress(0, text="Analyzing prompts...")
                total = max(len(df), 1)

                for index, prompt_text in enumerate(df["text"].fillna("").astype(str)):
                    result = scan_prompt(prompt_text)
                    records.append(
                        {
                            "text": prompt_text,
                            "ml_prediction": "Attack" if result["ml_prediction"] else "Benign",
                            "attack_probability": result["probability"],
                            "rule_prediction": "Attack" if result["rule_prediction"] else "Benign",
                            "hybrid_prediction": "Attack" if result["hybrid_prediction"] else "Benign",
                            "matched_rules": ", ".join(result["rules"]),
                        }
                    )
                    progress.progress(
                        (index + 1) / total,
                        text=f"Analyzed {index + 1} of {len(df)} prompts",
                    )

                output = pd.DataFrame(records)
                progress.empty()

                attacks = int((output["hybrid_prediction"] == "Attack").sum())
                benign = int((output["hybrid_prediction"] == "Benign").sum())

                st.write("")
                x, y, z = st.columns(3)
                with x:
                    metric_card("Total analyzed", len(output), "Prompts processed")
                with y:
                    metric_card("Flagged", attacks, "Hybrid detector")
                with z:
                    metric_card("Not flagged", benign, "Hybrid detector")

                section_heading("RESULTS", "Batch detection report")
                st.dataframe(output, use_container_width=True)
                st.download_button(
                    "⬇  Download analysis CSV",
                    output.to_csv(index=False).encode("utf-8"),
                    file_name="sentinellm_analysis.csv",
                    mime="text/csv",
                    use_container_width=True,
                )


# -------------------------------
# Security Evaluation
# -------------------------------
elif page == "Security Evaluation":
    hero(
        "MODEL PERFORMANCE",
        "Measure the defense.",
        "Compare the machine learning, rule-based, and hybrid approaches using the evaluation results generated during model testing.",
        "EVALUATION REPORT  ·  METRICS & ANALYSIS",
    )

    metrics = evaluation.get("metrics", {})
    if metrics:
        comparison = pd.DataFrame(metrics).T

        section_heading("COMPARISON", "Detection performance")
        st.dataframe(comparison.round(4), use_container_width=True)

        chart_columns = [
            col for col in ["Accuracy", "Precision", "Recall", "F1 Score"]
            if col in comparison.columns
        ]
        if chart_columns:
            with st.container(border=True):
                section_heading("METRICS", "Compare detection approaches")
                st.bar_chart(comparison[chart_columns], use_container_width=True)

        if "False Positive Rate" in comparison.columns:
            with st.container(border=True):
                section_heading("FALSE ALARMS", "False positive rate")
                st.bar_chart(comparison[["False Positive Rate"]], use_container_width=True)

        st.write("")
        roc_auc = evaluation.get("roc_auc")
        threshold_value = evaluation.get("threshold", threshold)
        p, q = st.columns(2)
        with p:
            metric_card(
                "ML ROC-AUC",
                f"{float(roc_auc):.4f}" if roc_auc is not None else "N/A",
                "Area under the ROC curve",
            )
        with q:
            metric_card(
                "Detection threshold",
                f"{float(threshold_value):.2f}",
                "Threshold stored in evaluation report or model",
            )
    else:
        st.warning("Evaluation report not found or contains no metrics. Check reports/evaluation.json.")

    matrix_path = os.path.join(BASE_DIR, "reports", "confusion_matrices.png")
    if os.path.exists(matrix_path):
        with st.container(border=True):
            section_heading("ERROR ANALYSIS", "Confusion matrices")
            st.image(matrix_path, use_container_width=True)

    family_path = os.path.join(BASE_DIR, "reports", "attack_family_analysis.csv")
    if os.path.exists(family_path):
        with st.container(border=True):
            section_heading("THREAT CATEGORIES", "Attack family analysis")
            family_df = pd.read_csv(family_path)
            st.dataframe(family_df, use_container_width=True)


# -------------------------------
# About
# -------------------------------
elif page == "About":
    hero(
        "PROJECT INFORMATION",
        "Built to study prompt injection.",
        "SentinelLLM is a machine learning-based framework designed to detect potentially malicious prompts targeting Large Language Models.",
        "AI SECURITY RESEARCH PROTOTYPE",
    )

    with st.container(border=True):
        section_heading("OVERVIEW", "About SentinelLLM")
        st.write(
            "The project combines machine learning classification, rule-based security checks, "
            "and hybrid detection. Its primary objective is to study prompt injection detection "
            "and evaluate the performance of different defensive approaches."
        )

    section_heading("TECH STACK", "Technologies used")
    tech = [
        ("🐍", "Python", "Core programming language"),
        ("☁️", "Google Colab", "Model development and experimentation"),
        ("📊", "Pandas & NumPy", "Data handling and numerical operations"),
        ("🧠", "Scikit-learn", "Machine learning implementation"),
        ("🔤", "TF-IDF", "Text feature extraction"),
        ("📈", "Logistic Regression", "Supervised text classification"),
        ("🖥️", "Streamlit", "Interactive web application"),
    ]
    cols = st.columns(2)
    for index, (emoji, name, description) in enumerate(tech):
        with cols[index % 2]:
            st.markdown(
                f"""
                <div class="metric-card" style="margin-bottom:12px; min-height:90px;">
                    <div style="font-size:20px;">{emoji}</div>
                    <div style="font-weight:700; color:#edf4ff; margin-top:5px;">{html.escape(name)}</div>
                    <div class="metric-note">{html.escape(description)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        section_heading("DATA", "Dataset")
        st.markdown("**Agentic Prompt-Injection Boundary Pairs**")
        st.markdown(
            "[Open dataset and documentation](https://huggingface.co/datasets/3nesdeniz/agentic-prompt-injection-boundary-pairs)"
        )
        st.caption("License: CC BY 4.0. Dataset attribution is required.")

    with st.container(border=True):
        section_heading("SCOPE & LIMITATIONS", "Research prototype")
        st.write(
            "SentinelLLM is a standalone prompt-screening research prototype. "
            "It does not directly connect to, modify, or provide production-grade protection "
            "for ChatGPT or other live LLM services. A prompt not flagged by this system "
            "is not guaranteed to be safe."
        )

st.markdown(
    """
    <div class="footer">
        SENTINELLLM · JUNAID LUQMAN BROHI · 24BSIT68 · BS INFORMATION TECHNOLOGY
    </div>
    """,
    unsafe_allow_html=True,
)
