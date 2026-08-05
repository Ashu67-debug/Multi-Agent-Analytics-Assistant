"""
Local Python function tools for the Data Analyst Agent.

These are lightweight, dependency-minimal tools (mostly pandas) that the
Data Analyst Agent can call directly, independent of the MCP server.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
from crewai.tools import tool

# ---------------------------------------------------------------------------
# 1. profile_dataframe
# ---------------------------------------------------------------------------

@tool("profile_dataframe")
def profile_dataframe(csv_path: str) -> dict[str, Any]:
    """Profile a local CSV file: row/column counts, dtypes, missing values,
    duplicate rows, and a small sample of records."""
    df = pd.read_csv(csv_path)
    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "column_names": list(df.columns),
        "data_types": {c: str(t) for c, t in df.dtypes.items()},
        "missing_values": {c: int(v) for c, v in df.isnull().sum().items() if v > 0},
        "duplicate_rows": int(df.duplicated().sum()),
        "sample_records": df.head(5).fillna("").to_dict(orient="records"),
    }


# ---------------------------------------------------------------------------
# 2. suggest_kpi_metrics
# ---------------------------------------------------------------------------

_DOMAIN_KPI_LIBRARY = {
    "ecommerce": [
        "Total revenue", "Average order value", "Repeat purchase rate",
        "Order cancellation rate", "Monthly active customers",
    ],
    "saas": [
        "Monthly recurring revenue", "Churn rate", "Net revenue retention",
        "Trial-to-paid conversion rate", "Daily active users",
    ],
    "events": [
        "Event success rate", "Sessions per user", "Average session duration",
        "Failed event ratio", "Daily active sessions",
    ],
    "default": [
        "Total volume", "Growth rate", "Error/failure rate",
        "Active entity count", "Conversion rate",
    ],
}


@tool("suggest_kpi_metrics")
def suggest_kpi_metrics(domain: str, columns: list[str]) -> dict[str, Any]:
    """Suggest KPIs based on a business domain and available dataset columns."""
    base = _DOMAIN_KPI_LIBRARY.get(domain.lower(), _DOMAIN_KPI_LIBRARY["default"])

    extra = []
    lower_cols = [c.lower() for c in columns]
    if any("revenue" in c or "amount" in c for c in lower_cols):
        extra.append("Revenue trend over time")
    if any("date" in c or "time" in c for c in lower_cols):
        extra.append("Daily/weekly/monthly trend")
    if any("status" in c for c in lower_cols):
        extra.append("Status breakdown / failure rate")

    return {"recommended_kpis": base + [k for k in extra if k not in base]}


# ---------------------------------------------------------------------------
# 3. generate_dashboard_layout
# ---------------------------------------------------------------------------

@tool("generate_dashboard_layout")
def generate_dashboard_layout(dashboard_name: str, kpis: list[str]) -> dict[str, Any]:
    """Suggest a dashboard structure (sections, charts, filters, drill-downs)
    given a name and a set of KPIs to display."""
    sections = ["Overview"]
    if any("revenue" in k.lower() or "value" in k.lower() for k in kpis):
        sections.append("Revenue Overview")
    if any("customer" in k.lower() or "user" in k.lower() for k in kpis):
        sections.append("Customer Segments")
    if any("churn" in k.lower() or "retention" in k.lower() for k in kpis):
        sections.append("Churn Indicators")
    sections.append("Detail / Drill-down Table")

    return {
        "dashboard_name": dashboard_name,
        "sections": sections,
        "kpi_cards": kpis,
        "filters": ["Date range", "Segment", "Region/Device"],
        "drill_down_views": ["Row-level detail table", "Time-series breakdown"],
    }


# ---------------------------------------------------------------------------
# 4. validate_sql_safety
# ---------------------------------------------------------------------------

_BLOCKED_KEYWORDS = ["DELETE", "UPDATE", "DROP", "ALTER", "INSERT", "MERGE", "TRUNCATE", "CREATE"]


@tool("validate_sql_safety")
def validate_sql_safety(sql_query: str) -> dict[str, Any]:
    """Check whether a SQL query is safe to run: only SELECT allowed,
    destructive statements blocked, warnings for SELECT * and missing
    date filters."""
    upper = sql_query.upper()
    issues = []
    warnings = []

    if not upper.strip().startswith("SELECT") and not upper.strip().startswith("WITH"):
        issues.append("Query does not start with SELECT (or WITH ... SELECT).")

    for kw in _BLOCKED_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            issues.append(f"Blocked keyword found: {kw}")

    if re.search(r"SELECT\s+\*", upper):
        warnings.append("Query uses SELECT * — consider selecting explicit columns.")

    if not re.search(r"\bWHERE\b.*\bDATE\b|\bWHERE\b.*_DATE|\bWHERE\b.*_TIME", upper):
        warnings.append("No obvious date filter detected — query may scan the full table.")

    return {
        "is_safe": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
    }


# ---------------------------------------------------------------------------
# 5. explain_query_result
# ---------------------------------------------------------------------------

@tool("explain_query_result")
def explain_query_result(metric: str, trend: str, change_percent: float) -> str:
    """Convert a tabular metric/trend/change_percent result into a plain
    business explanation."""
    direction = "increased" if trend.lower() == "increasing" else "decreased" if trend.lower() == "decreasing" else "stayed flat for"
    metric_label = metric.replace("_", " ")

    explanation = f"{metric_label.capitalize()} {direction} by {abs(change_percent)}%. "
    if trend.lower() == "decreasing":
        explanation += (
            "This may indicate lower customer acquisition, reduced repeat purchases, "
            "or seasonal demand drop."
        )
    elif trend.lower() == "increasing":
        explanation += (
            "This may indicate successful campaigns, seasonal demand, or improved "
            "customer retention."
        )
    else:
        explanation += "Performance has been stable over the observed period."
    return explanation


ANALYST_TOOLS = [
    profile_dataframe,
    suggest_kpi_metrics,
    generate_dashboard_layout,
    validate_sql_safety,
    explain_query_result,
]
