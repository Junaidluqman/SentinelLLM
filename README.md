
# SentinelLLM

An ML-Based Framework for Detecting Prompt Injection
Attacks and Evaluating LLM Security Defenses.

## Overview

SentinelLLM combines machine learning, rule-based
detection, and hybrid classification to identify
potentially malicious prompts.

## Technologies

- Python
- Google Colab
- Pandas
- NumPy
- Scikit-learn
- TF-IDF
- Logistic Regression
- Streamlit

## Dataset

Agentic Prompt-Injection Boundary Pairs

https://huggingface.co/datasets/3nesdeniz/agentic-prompt-injection-boundary-pairs

License: CC BY 4.0

Dataset attribution:
Enes Deniz, Agentic Prompt-Injection Boundary Pairs,
2026, https://doi.org/10.5281/zenodo.21378693

## Run the Application

Install dependencies:

pip install -r requirements.txt

Start Streamlit:

streamlit run app.py

## Limitations

This is a research prototype. It does not guarantee
the detection of every prompt injection attack.
