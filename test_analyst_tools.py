import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from function_tools.analyst_tools import (
    profile_dataframe,
    suggest_kpi_metrics,
    generate_dashboard_layout,
    validate_sql_safety,
    explain_query_result,
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "sample_data")


def _call(fn, *args, **kwargs):
    target = fn.func if hasattr(fn, "func") else fn
    return target(*args, **kwargs)


def test_profile_dataframe():
    result = _call(profile_dataframe, os.path.join(SAMPLE_DIR, "transactions_sample.csv"))
    assert result["row_count"] > 0
    assert "order_id" in result["column_names"]


def test_suggest_kpi_metrics():
    result = _call(suggest_kpi_metrics, "ecommerce", ["order_id", "revenue", "order_date"])
    assert "Total revenue" in result["recommended_kpis"]


def test_generate_dashboard_layout():
    result = _call(generate_dashboard_layout, "Revenue Dashboard", ["Total revenue", "Churn rate"])
    assert result["dashboard_name"] == "Revenue Dashboard"
    assert "Churn Indicators" in result["sections"]


def test_validate_sql_safety_blocks_delete():
    result = _call(validate_sql_safety, "DELETE FROM orders WHERE id = 1")
    assert result["is_safe"] is False
    assert any("DELETE" in issue for issue in result["issues"])


def test_validate_sql_safety_allows_select():
    result = _call(validate_sql_safety, "SELECT id, revenue FROM orders WHERE order_date > '2024-01-01'")
    assert result["is_safe"] is True


def test_explain_query_result_decreasing():
    text = _call(explain_query_result, "monthly_revenue", "decreasing", -12.5)
    assert "decreased" in text
    assert "12.5" in text
