
import streamlit as st
import joblib
import pandas as pd
import json
import re
import os
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="SentinelLLM | AI Security",
    page_icon="🛡️",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR, "sentinellm_model.joblib"
)

REPORT_PATH = os.path.join(
    BASE_DIR, "reports", "evaluation.json"
)

# -------------------------------
# Load model
# -------------------------------

@st.cache_resource
def load_model():

    return joblib.load(MODEL_PATH)

bundle = load_model()

model = bundle["model"]
vectorizer = bundle["vectorizer"]
threshold = bundle["threshold"]
rules = bundle["rules"]

# -------------------------------
# Load evaluation
# -------------------------------

@st.cache_data
def load_evaluation():

    if os.path.exists(REPORT_PATH):

        with open(REPORT_PATH, "r") as file:
            return json.load(file)

    return {}

evaluation = load_evaluation()

# -------------------------------
# Detection functions
# -------------------------------

def rule_detector(text):

    detected = []

    for category, patterns in rules.items():

        for pattern in patterns:

            if re.search(
                pattern,
                str(text),
                flags=re.IGNORECASE
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
        "rules": rule_matches
    }


# -------------------------------
# Sidebar
# -------------------------------

st.sidebar.title("🛡️ SentinelLLM")

st.sidebar.caption(
    "Machine Learning-Based Prompt Injection Detection"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Prompt Scanner",
        "Batch Analysis",
        "Security Evaluation",
        "About"
    ]
)

st.sidebar.divider()

st.sidebar.caption("SentinelLLM v1.0.0")
st.sidebar.caption("AI Security Research Project")

# -------------------------------
# Dashboard
# -------------------------------

if page == "Dashboard":

    st.title("🛡️ SentinelLLM Dashboard")

    st.write(
        "An intelligent framework for detecting "
        "prompt injection attacks and evaluating "
        "LLM security defenses."
    )

    metrics = evaluation.get("metrics", {})

    ml = metrics.get("ML-Based", {})
    hybrid = metrics.get("Hybrid", {})
    rule = metrics.get("Rule-Based", {})

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Test Samples",
        evaluation.get("test_samples", "N/A")
    )

    c2.metric(
        "ML Accuracy",
        f"{ml.get('Accuracy', 0) * 100:.2f}%"
    )

    c3.metric(
        "ML Attack Recall",
        f"{ml.get('Recall', 0) * 100:.2f}%"
    )

    c4.metric(
        "Hybrid F1 Score",
        f"{hybrid.get('F1 Score', 0) * 100:.2f}%"
    )

    st.divider()

    st.subheader("Detection Architecture")

    col1, col2, col3 = st.columns(3)

    col1.info("🤖 ML-Based Detection\n\nTF-IDF + Logistic Regression")

    col2.info("🔍 Rule-Based Detection\n\nSecurity pattern analysis")

    col3.success("🛡️ Hybrid Detection\n\nCombined security decision")

    st.subheader("Detection Performance")

    if metrics:

        comparison = pd.DataFrame(metrics).T

        selected = comparison[
            ["Accuracy", "Precision", "Recall", "F1 Score"]
        ]

        st.bar_chart(selected)

# -------------------------------
# Prompt Scanner
# -------------------------------

elif page == "Prompt Scanner":

    st.title("🔍 Prompt Injection Scanner")

    st.write(
        "Enter a prompt to analyze its potential "
        "prompt-injection behavior."
    )

    prompt = st.text_area(
        "Enter prompt",
        height=180,
        placeholder="Paste a prompt here..."
    )

    if st.button(
        "Analyze Prompt",
        type="primary",
        use_container_width=True
    ):

        if not prompt.strip():

            st.warning("Please enter a prompt.")

        else:

            result = scan_prompt(prompt)

            st.divider()

            if result["hybrid_prediction"] == 1:

                st.error(
                    "⚠️ Potentially Malicious Prompt — Review Required"
                )

            else:

                st.success(
                    "✅ No Attack Detected by Current Detectors"
                )

            a, b, c = st.columns(3)

            a.metric(
                "ML Classification",
                "Attack" if result["ml_prediction"] else "Benign"
            )

            b.metric(
                "ML Attack Probability",
                f"{result['probability'] * 100:.2f}%"
            )

            c.metric(
                "Rule-Based Result",
                "Flagged" if result["rule_prediction"] else "Not Flagged"
            )

            st.subheader("Detection Details")

            st.write(
                "Selected ML threshold:",
                f"{threshold:.2f}"
            )

            st.write(
                "Hybrid result:",
                "Flagged" if result["hybrid_prediction"] else "Not flagged"
            )

            if result["rules"]:

                st.warning("Matched security patterns:")

                for item in result["rules"]:
                    st.write(f"- {item}")

            else:

                st.info(
                    "No predefined rule patterns matched."
                )

            st.caption(
                "A benign result does not guarantee that a prompt "
                "is safe. This tool is a research screening system."
            )

# -------------------------------
# Batch Analysis
# -------------------------------

elif page == "Batch Analysis":

    st.title("📂 Batch Prompt Analysis")

    st.write(
        "Upload a CSV file containing a column named 'text'."
    )

    uploaded = st.file_uploader(
        "Upload CSV",
        type=["csv"]
    )

    if uploaded:

        df = pd.read_csv(uploaded)

        if "text" not in df.columns:

            st.error(
                "CSV must contain a column named 'text'."
            )

        else:

            if st.button("Analyze CSV"):

                records = []

                for text in df["text"].fillna("").astype(str):

                    result = scan_prompt(text)

                    records.append({
                        "text": text,
                        "ml_prediction": (
                            "Attack"
                            if result["ml_prediction"]
                            else "Benign"
                        ),
                        "attack_probability": result["probability"],
                        "rule_prediction": (
                            "Attack"
                            if result["rule_prediction"]
                            else "Benign"
                        ),
                        "hybrid_prediction": (
                            "Attack"
                            if result["hybrid_prediction"]
                            else "Benign"
                        ),
                        "matched_rules": ", ".join(
                            result["rules"]
                        )
                    })

                output = pd.DataFrame(records)

                st.dataframe(
                    output,
                    use_container_width=True
                )

                st.download_button(
                    "Download Analysis CSV",
                    output.to_csv(index=False),
                    file_name="sentinellm_analysis.csv",
                    mime="text/csv"
                )

# -------------------------------
# Security Evaluation
# -------------------------------

elif page == "Security Evaluation":

    st.title("📊 Security Evaluation")

    metrics = evaluation.get("metrics", {})

    if metrics:

        comparison = pd.DataFrame(metrics).T

        st.subheader("Performance Comparison")

        st.dataframe(
            comparison.round(4),
            use_container_width=True
        )

        st.subheader("Detection Metrics")

        st.bar_chart(
            comparison[
                ["Precision", "Recall", "F1 Score"]
            ]
        )

        st.subheader("False Positive Rate")

        st.bar_chart(
            comparison[["False Positive Rate"]]
        )

        st.metric(
            "ML ROC-AUC",
            f"{evaluation.get('roc_auc', 0):.4f}"
        )

        st.metric(
            "Detection Threshold",
            f"{threshold:.2f}"
        )

    else:

        st.warning("Evaluation report not found.")

    matrix_path = os.path.join(
        BASE_DIR,
        "reports",
        "confusion_matrices.png"
    )

    if os.path.exists(matrix_path):

        st.subheader("Confusion Matrices")

        st.image(
            matrix_path,
            use_container_width=True
        )

    family_path = os.path.join(
        BASE_DIR,
        "reports",
        "attack_family_analysis.csv"
    )

    if os.path.exists(family_path):

        st.subheader("Attack Family Analysis")

        family_df = pd.read_csv(family_path)

        st.dataframe(
            family_df,
            use_container_width=True
        )

# -------------------------------
# About
# -------------------------------

elif page == "About":

    st.title("About SentinelLLM")

    st.write("""
    SentinelLLM is a machine learning-based framework
    designed to detect potentially malicious prompts
    targeting Large Language Models.

    The project combines machine learning classification,
    rule-based security checks, and hybrid detection.

    Its primary objective is to study prompt injection
    detection and evaluate the performance of different
    defensive approaches.
    """)

    st.subheader("Technologies")

    st.write("""
    - Python
    - Google Colab
    - Pandas and NumPy
    - Scikit-learn
    - TF-IDF
    - Logistic Regression
    - Streamlit
    """)

    st.subheader("Dataset")

    st.write(
        "Agentic Prompt-Injection Boundary Pairs"
    )

    st.markdown(
        "[Dataset and documentation](https://huggingface.co/datasets/3nesdeniz/agentic-prompt-injection-boundary-pairs)"
    )

    st.write(
        "License: CC BY 4.0. Dataset attribution is required."
    )

    st.caption(
        "Research prototype only. This application is not "
        "a production-grade LLM firewall."
    )
