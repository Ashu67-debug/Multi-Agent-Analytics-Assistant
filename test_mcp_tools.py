import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))

from tools.csv_profile_tools import mcp_profile_csv
from tools.sql_tools import mcp_run_duckdb_query, mcp_validate_sql
from tools.data_quality_tools import mcp_detect_data_quality_issues, mcp_anomaly_detection_summary
from tools.kpi_tools import mcp_generate_kpi_catalog, mcp_create_data_dictionary
from tools.ml_tools import mcp_recommend_ml_use_cases, mcp_feature_engineering_suggestions
from tools.report_tools import mcp_generate_report_markdown
from tools.safety import resolve_safe_path, UnsafePathError, validate_readonly_sql, UnsafeSQLError


def test_mcp_profile_csv():
    result = mcp_profile_csv("events_sample.csv")
    assert result["rows"] > 0
    assert result["columns"] > 0


def test_mcp_run_duckdb_query_select_only():
    result = mcp_run_duckdb_query(
        "SELECT event_type, COUNT(*) as cnt FROM dataset GROUP BY event_type LIMIT 10",
        "events_sample.csv",
    )
    assert result["success"] is True
    assert result["row_count"] > 0


def test_mcp_run_duckdb_query_blocks_delete():
    result = mcp_run_duckdb_query("DELETE FROM dataset", "events_sample.csv")
    assert result["success"] is False


def test_mcp_validate_sql_flags_missing_limit():
    result = mcp_validate_sql("SELECT * FROM dataset")
    assert result["checks"]["has_limit"] is False
    assert result["checks"]["avoids_select_star"] is False


def test_mcp_detect_data_quality_issues():
    result = mcp_detect_data_quality_issues("transactions_sample.csv")
    assert result["success"] is True
    assert "issues_found" in result


def test_mcp_anomaly_detection_summary():
    result = mcp_anomaly_detection_summary("transactions_sample.csv", "revenue", method="iqr")
    assert result["success"] is True


def test_mcp_generate_kpi_catalog():
    result = mcp_generate_kpi_catalog("ecommerce")
    assert len(result["kpis"]) > 0


def test_mcp_create_data_dictionary():
    result = mcp_create_data_dictionary("customers_sample.csv")
    assert result["success"] is True
    assert len(result["columns"]) > 0


def test_mcp_recommend_ml_use_cases():
    result = mcp_recommend_ml_use_cases("customers_sample.csv")
    assert result["success"] is True
    assert len(result["ml_use_cases"]) > 0


def test_mcp_feature_engineering_suggestions():
    result = mcp_feature_engineering_suggestions("event")
    assert len(result["features"]) > 0


def test_mcp_generate_report_markdown():
    result = mcp_generate_report_markdown(dataset_summary="10 rows, 5 columns")
    assert "Dataset Summary" in result["markdown_report"]


def test_resolve_safe_path_blocks_traversal():
    try:
        resolve_safe_path("../../etc/passwd")
        assert False, "Expected UnsafePathError"
    except UnsafePathError:
        pass


def test_validate_readonly_sql_blocks_drop():
    try:
        validate_readonly_sql("DROP TABLE dataset")
        assert False, "Expected UnsafeSQLError"
    except UnsafeSQLError:
        pass
