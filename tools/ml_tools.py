"""MCP Tool 6: mcp_recommend_ml_use_cases
MCP Tool 7: mcp_feature_engineering_suggestions
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .safety import resolve_safe_path, safe_error_message


def mcp_recommend_ml_use_cases(file_name: str) -> dict[str, Any]:
    """Recommend ML use cases based on the columns available in a dataset.

    Used by: Data Scientist Agent, Supervisor Agent.
    """
    try:
        path = resolve_safe_path(file_name)
        df = pd.read_csv(path)
        cols = [c.lower() for c in df.columns]
        use_cases = []

        if any("churn" in c for c in cols) or ("customer_id" in cols and any("status" in c for c in cols)):
            use_cases.append({
                "use_case": "churn prediction",
                "problem_type": "classification",
                "required_columns": [c for c in df.columns if "id" in c.lower() or "churn" in c.lower() or "status" in c.lower()],
                "business_value": "Reduce customer loss by proactively targeting at-risk customers.",
            })

        if any("revenue" in c or "amount" in c for c in cols) and any("date" in c or "time" in c for c in cols):
            use_cases.append({
                "use_case": "revenue forecasting",
                "problem_type": "forecasting",
                "required_columns": [c for c in df.columns if "revenue" in c.lower() or "amount" in c.lower() or "date" in c.lower()],
                "business_value": "Improve financial planning and inventory decisions.",
            })

        if any("event_type" in c or "success" in c for c in cols):
            use_cases.append({
                "use_case": "anomaly / failure detection",
                "problem_type": "anomaly_detection",
                "required_columns": [c for c in df.columns if "success" in c.lower() or "event" in c.lower()],
                "business_value": "Detect unusual failure spikes before they impact customers.",
            })

        if any("segment" in c for c in cols):
            use_cases.append({
                "use_case": "customer segmentation",
                "problem_type": "clustering",
                "required_columns": [c for c in df.columns if "segment" in c.lower() or "id" in c.lower()],
                "business_value": "Enable targeted marketing and personalized offers.",
            })

        if not use_cases:
            use_cases.append({
                "use_case": "general exploratory analysis",
                "problem_type": "classification",
                "required_columns": list(df.columns)[:3],
                "business_value": "Establish a baseline before pursuing a specific ML use case.",
            })

        return {"success": True, "ml_use_cases": use_cases}
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": safe_error_message(exc)}


def mcp_feature_engineering_suggestions(data_type: str = "event") -> dict[str, Any]:
    """Suggest feature engineering ideas for event, customer, transaction,
    or time-series data.

    Used by: Data Scientist Agent.
    """
    library = {
        "event": [
            "events_per_user_last_1_hour",
            "failed_event_ratio_last_24_hours",
            "session_count_last_30_days",
            "average_session_duration",
        ],
        "transaction": [
            "days_since_last_purchase",
            "rolling_7_day_revenue",
            "average_transaction_amount",
            "refund_rate_last_90_days",
        ],
        "customer": [
            "customer_tenure_days",
            "support_ticket_count",
            "segment_tier_encoded",
            "engagement_score",
        ],
    }
    features = library.get(data_type.lower(), library["event"])
    return {"data_type": data_type, "features": features}
