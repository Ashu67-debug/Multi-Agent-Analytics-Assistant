"""
Local Python function tools for the Data Scientist Agent.

These tools handle ML problem framing, feature engineering suggestions,
risk detection, evaluation metric recommendation, and pipeline planning.
They are local (no MCP dependency).
"""

from __future__ import annotations

from typing import Any

import pandas as pd
from crewai.tools import tool

# ---------------------------------------------------------------------------
# 1. recommend_ml_problem_type
# ---------------------------------------------------------------------------

_PROBLEM_PATTERNS = [
    (["churn", "will buy", "fraud", "default", "yes/no", "binary"], "classification", "The goal is to predict a yes/no or categorical outcome."),
    (["forecast", "next month", "predict revenue", "predict sales", "time series"], "forecasting", "The goal is to predict future values over time."),
    (["segment", "group customers", "cluster"], "clustering", "The goal is to group similar records without labeled outcomes."),
    (["anomaly", "fraud detection", "unusual", "outlier detection"], "anomaly_detection", "The goal is to flag unusual or rare events."),
    (["recommend", "suggest products", "personalize"], "recommendation", "The goal is to suggest relevant items to users."),
    (["rank", "order by relevance", "top n"], "ranking", "The goal is to order items by relevance or priority."),
    (["predict price", "predict amount", "predict value", "estimate"], "regression", "The goal is to predict a continuous numeric value."),
]


@tool("recommend_ml_problem_type")
def recommend_ml_problem_type(use_case_description: str, target_variable: str = "") -> dict[str, Any]:
    """Classify a natural-language ML use case into a problem type
    (classification, regression, clustering, forecasting, anomaly_detection,
    recommendation, ranking)."""
    text = use_case_description.lower()
    for keywords, problem_type, reason in _PROBLEM_PATTERNS:
        if any(k in text for k in keywords):
            return {
                "problem_type": problem_type,
                "target_variable": target_variable or "unspecified",
                "reason": reason,
            }

    return {
        "problem_type": "classification",
        "target_variable": target_variable or "unspecified",
        "reason": "No strong signal detected; classification is the most common default for decision-style questions.",
    }


# ---------------------------------------------------------------------------
# 2. suggest_feature_engineering
# ---------------------------------------------------------------------------

_FEATURE_LIBRARY = {
    "event": [
        "user_activity_last_5_minutes",
        "user_activity_last_1_hour",
        "failed_event_ratio",
        "session_duration",
        "events_per_session",
    ],
    "transaction": [
        "average_transaction_amount",
        "days_since_last_purchase",
        "transaction_count_last_30_days",
        "refund_ratio",
        "order_cancellation_rate",
    ],
    "customer": [
        "customer tenure (days since signup)",
        "number of support tickets",
        "segment / plan tier",
        "engagement score",
    ],
}


@tool("suggest_feature_engineering")
def suggest_feature_engineering(data_type: str = "event") -> dict[str, Any]:
    """Suggest feature engineering ideas for event, transaction, or customer
    data."""
    key = data_type.lower()
    features: list[str] = []
    if key in _FEATURE_LIBRARY:
        features = _FEATURE_LIBRARY[key]
    else:
        for v in _FEATURE_LIBRARY.values():
            features.extend(v)
        features = list(dict.fromkeys(features))[:8]

    return {"features": features}


# ---------------------------------------------------------------------------
# 3. detect_ml_data_risks
# ---------------------------------------------------------------------------

@tool("detect_ml_data_risks")
def detect_ml_data_risks(csv_path: str, target_column: str = "") -> dict[str, Any]:
    """Identify common ML data risks before model training: missing target,
    class imbalance, duplicates, high-cardinality columns, outliers."""
    df = pd.read_csv(csv_path)
    risks = []

    if target_column and target_column not in df.columns:
        risks.append(f"Missing target column: '{target_column}' not found in dataset.")

    if target_column and target_column in df.columns:
        counts = df[target_column].value_counts(normalize=True)
        if len(counts) > 1 and counts.iloc[0] > 0.9:
            risks.append("Potential class imbalance: dominant class exceeds 90% of records.")

    dup_count = int(df.duplicated().sum())
    if dup_count > 0:
        risks.append(f"Duplicate records found: {dup_count} rows.")

    for col in df.select_dtypes(include="object").columns:
        cardinality = df[col].nunique()
        if cardinality > 0.8 * len(df):
            risks.append(f"High-cardinality column detected: '{col}' ({cardinality} unique values).")

    for col in df.select_dtypes(include="number").columns:
        if df[col].isnull().sum() > 0:
            risks.append(f"Missing numeric values in column '{col}'.")

    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
    if date_cols:
        risks.append(f"Time-based split likely required due to date column(s): {date_cols}.")

    if not risks:
        risks.append("No major risks detected in a quick pass — recommend deeper validation before training.")

    return {"risks": risks}


# ---------------------------------------------------------------------------
# 4. recommend_evaluation_metrics
# ---------------------------------------------------------------------------

_METRIC_LIBRARY = {
    "classification": (
        ["precision", "recall", "F1-score", "ROC-AUC", "PR-AUC"],
        "Use recall when missing positive cases is costly; use precision when false positives are costly.",
    ),
    "regression": (
        ["MAE", "RMSE", "R2", "MAPE"],
        "Use MAPE for business-friendly percentage error reporting.",
    ),
    "clustering": (
        ["silhouette score", "Davies-Bouldin index", "inertia"],
        "Use silhouette score to assess cluster separation quality.",
    ),
    "forecasting": (
        ["MAE", "RMSE", "MAPE", "SMAPE"],
        "Use MAPE/SMAPE for interpretable forecast accuracy across scales.",
    ),
    "anomaly_detection": (
        ["precision", "recall", "F1-score", "AUC-PR"],
        "Prioritize recall when missing anomalies (e.g. fraud) is very costly.",
    ),
    "recommendation": (
        ["precision@k", "recall@k", "NDCG", "hit rate"],
        "Use NDCG when the order of recommendations matters, not just presence.",
    ),
    "ranking": (
        ["NDCG", "MAP", "MRR"],
        "Use MRR when only the first correct result matters most to the user.",
    ),
}


@tool("recommend_evaluation_metrics")
def recommend_evaluation_metrics(problem_type: str) -> dict[str, Any]:
    """Suggest evaluation metrics based on the ML problem type."""
    metrics, note = _METRIC_LIBRARY.get(
        problem_type.lower(), (["accuracy"], "Default metric set — refine once the problem type is confirmed.")
    )
    return {
        "problem_type": problem_type,
        "metrics": metrics,
        "business_note": note,
    }


# ---------------------------------------------------------------------------
# 5. create_ml_pipeline_plan
# ---------------------------------------------------------------------------

@tool("create_ml_pipeline_plan")
def create_ml_pipeline_plan(problem_type: str = "classification") -> dict[str, Any]:
    """Create an end-to-end ML pipeline plan covering ingestion through
    monitoring and retraining."""
    return {
        "problem_type": problem_type,
        "pipeline": {
            "data_ingestion": "Load data from CSV/Parquet sources via DuckDB/pandas.",
            "data_validation": "Run mcp_detect_data_quality_issues and schema checks (pandera).",
            "feature_engineering": "Apply suggest_feature_engineering outputs; build feature table.",
            "train_test_split": "Time-based split if time-series/event data, else stratified split.",
            "model_training": f"Train baseline + candidate models appropriate for {problem_type}.",
            "model_evaluation": "Evaluate using recommend_evaluation_metrics outputs.",
            "model_registry": "Track model version, metrics, and artifacts locally (or MLflow if available).",
            "inference": "Support batch inference initially; real-time via API if required.",
            "monitoring": "Track prediction drift, input distribution drift, and error rates.",
            "retraining": "Schedule periodic retraining triggered by drift or performance decay.",
        },
    }


SCIENTIST_TOOLS = [
    recommend_ml_problem_type,
    suggest_feature_engineering,
    detect_ml_data_risks,
    recommend_evaluation_metrics,
    create_ml_pipeline_plan,
]
