"""MCP Tool 5: mcp_generate_kpi_catalog
MCP Tool 9: mcp_create_data_dictionary
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .safety import resolve_safe_path, safe_error_message

_KPI_CATALOG_LIBRARY = {
    "ecommerce": [
        {"name": "Conversion Rate", "formula": "orders / sessions", "grain": "daily", "business_use": "Tracks funnel effectiveness"},
        {"name": "Average Order Value", "formula": "revenue / orders", "grain": "daily", "business_use": "Tracks basket size trends"},
        {"name": "Cancellation Rate", "formula": "cancelled_orders / orders", "grain": "daily", "business_use": "Flags fulfillment or pricing issues"},
        {"name": "Repeat Purchase Rate", "formula": "customers_with_2plus_orders / total_customers", "grain": "monthly", "business_use": "Tracks loyalty"},
    ],
    "events": [
        {"name": "Event Success Rate", "formula": "successful_events / total_events", "grain": "hourly", "business_use": "Tracks system reliability"},
        {"name": "Sessions per User", "formula": "sessions / distinct_users", "grain": "daily", "business_use": "Tracks engagement depth"},
        {"name": "Failed Event Ratio", "formula": "failed_events / total_events", "grain": "hourly", "business_use": "Flags technical issues"},
    ],
    "default": [
        {"name": "Total Volume", "formula": "count(*)", "grain": "daily", "business_use": "Tracks overall activity"},
        {"name": "Growth Rate", "formula": "(current_period - prior_period) / prior_period", "grain": "monthly", "business_use": "Tracks trend direction"},
    ],
}


def mcp_generate_kpi_catalog(domain: str) -> dict[str, Any]:
    """Generate a KPI catalog (name, formula, grain, business use) for a
    given business domain.

    Used by: Data Analyst Agent, Supervisor Agent.
    """
    kpis = _KPI_CATALOG_LIBRARY.get(domain.lower(), _KPI_CATALOG_LIBRARY["default"])
    return {"domain": domain, "kpis": kpis}


_MEANING_HINTS = {
    "id": "Unique identifier",
    "date": "Date the record occurred",
    "time": "Timestamp of the event/record",
    "amount": "Monetary value associated with the record",
    "revenue": "Monetary value generated",
    "status": "Categorical state of the record",
    "count": "Numeric count/aggregate value",
    "type": "Category / classification label",
}


def mcp_create_data_dictionary(file_name: str) -> dict[str, Any]:
    """Generate a simple data dictionary from a dataset: column name,
    inferred type, possible meaning, and sample values.

    Used by: Data Analyst Agent, Supervisor Agent.
    """
    try:
        path = resolve_safe_path(file_name)
        df = pd.read_csv(path)

        columns = []
        for col in df.columns:
            meaning = "General attribute"
            for hint, desc in _MEANING_HINTS.items():
                if hint in col.lower():
                    meaning = desc
                    break

            sample_values = df[col].dropna().astype(str).unique().tolist()[:3]
            columns.append({
                "name": col,
                "type": str(df[col].dtype),
                "possible_meaning": meaning,
                "sample_values": sample_values,
            })

        return {"success": True, "columns": columns}
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": safe_error_message(exc)}
