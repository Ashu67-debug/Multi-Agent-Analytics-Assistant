"""MCP Tool 4: mcp_detect_data_quality_issues
MCP Tool 8: mcp_anomaly_detection_summary
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .safety import resolve_safe_path, safe_error_message


def mcp_detect_data_quality_issues(file_name: str) -> dict[str, Any]:
    """Detect common data quality problems: missing values, duplicate rows,
    invalid data types, negative values in positive-only columns, outliers,
    constant columns, and high-cardinality columns.

    Used by: Data Analyst Agent, Data Scientist Agent.
    Allowed libraries: pandas, great_expectations, pandera.
    """
    try:
        path = resolve_safe_path(file_name)
        df = pd.read_csv(path)
        issues: dict[str, Any] = {}

        missing = {c: int(v) for c, v in df.isnull().sum().items() if v > 0}
        if missing:
            issues["missing_values"] = missing

        dup_count = int(df.duplicated().sum())
        if dup_count > 0:
            issues["duplicate_rows"] = dup_count

        constant_cols = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
        if constant_cols:
            issues["constant_columns"] = constant_cols

        high_card_cols = [
            c for c in df.select_dtypes(include="object").columns
            if df[c].nunique() > 0.8 * len(df)
        ]
        if high_card_cols:
            issues["high_cardinality_columns"] = high_card_cols

        negative_issues = {}
        for col in df.select_dtypes(include="number").columns:
            likely_positive_only = any(
                kw in col.lower() for kw in ["revenue", "amount", "price", "count", "quantity"]
            )
            if likely_positive_only and (df[col] < 0).any():
                negative_issues[col] = int((df[col] < 0).sum())
        if negative_issues:
            issues["negative_values_in_positive_only_columns"] = negative_issues

        outlier_issues = {}
        for col in df.select_dtypes(include="number").columns:
            series = df[col].dropna()
            if len(series) < 4:
                continue
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            outlier_count = int(((series < lower) | (series > upper)).sum())
            if outlier_count > 0:
                outlier_issues[col] = outlier_count
        if outlier_issues:
            issues["outliers_iqr"] = outlier_issues

        return {"success": True, "issues_found": issues, "is_clean": len(issues) == 0}
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": safe_error_message(exc)}


def mcp_anomaly_detection_summary(file_name: str, column: str, method: str = "zscore") -> dict[str, Any]:
    """Detect simple anomalies in a numeric column using z-score or IQR.

    Used by: Data Scientist Agent, Data Analyst Agent.
    Allowed libraries: pandas, scipy, scikit-learn, statsmodels.
    Methods: zscore, iqr.
    """
    try:
        path = resolve_safe_path(file_name)
        df = pd.read_csv(path)
        if column not in df.columns:
            return {"success": False, "error": f"Column '{column}' not found."}

        series = df[column].dropna()
        if not np.issubdtype(series.dtype, np.number):
            return {"success": False, "error": f"Column '{column}' is not numeric."}

        if method == "iqr":
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            anomalies = series[(series < lower) | (series > upper)]
        else:
            mean, std = series.mean(), series.std(ddof=0) or 1.0
            z_scores = (series - mean) / std
            anomalies = series[z_scores.abs() > 3]

        return {
            "success": True,
            "method": method,
            "anomaly_count": int(len(anomalies)),
            "anomaly_indices": anomalies.index.tolist()[:20],
            "anomaly_values": [float(v) for v in anomalies.tolist()[:20]],
        }
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": safe_error_message(exc)}
