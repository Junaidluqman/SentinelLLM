
import os
import re
import json
import joblib
import pandas as pd

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

# -------------------------------------------------
# Application configuration
# -------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(
    BASE_DIR, "sentinellm_model.joblib"
)

REPORT_PATH = os.path.join(
    BASE_DIR, "evaluation.json"
)

app = FastAPI(
    title="SentinelLLM API",
    description="ML-based Prompt Injection Detection API",
    version="1.0.0"
)

# -------------------------------------------------
# Load trained ML model
# -------------------------------------------------

try:
    bundle = joblib.load(MODEL_PATH)

    model = bundle["model"]
    vectorizer = bundle["vectorizer"]
    threshold = float(bundle["threshold"])
    rules = bundle["rules"]

except Exception as exc:
    raise RuntimeError(
        f"Could not load SentinelLLM model: {exc}"
    ) from exc


# -------------------------------------------------
# Request validation
# -------------------------------------------------

class PromptRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=20000,
        description="Prompt to analyze"
    )


# -------------------------------------------------
# Detection engine
# Original detection logic preserved
# -------------------------------------------------

def rule_detector(text: str):
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


def scan_prompt(text: str):

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


# -------------------------------------------------
# API endpoints
# -------------------------------------------------

@app.get("/")
def home():
    return {
        "project": "SentinelLLM",
        "status": "Online",
        "message": "Prompt Injection Detection API",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }


@app.get("/evaluation")
def evaluation():

    if not os.path.exists(REPORT_PATH):
        raise HTTPException(
            status_code=404,
            detail="Evaluation report not found"
        )

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@app.post("/scan")
def scan(request: PromptRequest):

    if not request.text.strip():
        raise HTTPException(
            status_code=400,
            detail="Prompt cannot be empty"
        )

    result = scan_prompt(request.text)

    return {
        "project": "SentinelLLM",
        "input": request.text,
        "classification": (
            "Malicious"
            if result["hybrid_prediction"]
            else "Benign"
        ),
        "ml_classification": (
            "Attack" if result["ml_prediction"] else "Benign"
        ),
        "attack_probability": round(
            result["probability"], 4
        ),
        "rule_classification": (
            "Attack" if result["rule_prediction"] else "Benign"
        ),
        "hybrid_classification": (
            "Attack" if result["hybrid_prediction"] else "Benign"
        ),
        "matched_rules": result["rules"],
        "threshold": threshold
    }


@app.post("/batch")
async def batch_analysis(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are supported"
        )

    try:
        df = pd.read_csv(file.file)

        if "text" not in df.columns:
            raise HTTPException(
                status_code=400,
                detail="CSV must contain a 'text' column"
            )

        if len(df) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5000 prompts per batch"
            )

        records = []

        for prompt in df["text"].fillna("").astype(str):

            result = scan_prompt(prompt)

            records.append({
                "text": prompt,
                "ml_prediction": (
                    "Attack" if result["ml_prediction"] else "Benign"
                ),
                "attack_probability": result["probability"],
                "rule_prediction": (
                    "Attack" if result["rule_prediction"] else "Benign"
                ),
                "hybrid_prediction": (
                    "Attack" if result["hybrid_prediction"] else "Benign"
                ),
                "matched_rules": ", ".join(result["rules"])
            })

        output = pd.DataFrame(records)

        return {
            "total_analyzed": len(output),
            "flagged": int(
                (output["hybrid_prediction"] == "Attack").sum()
            ),
            "benign": int(
                (output["hybrid_prediction"] == "Benign").sum()
            ),
            "results": records
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"CSV processing failed: {str(exc)}"
        )
