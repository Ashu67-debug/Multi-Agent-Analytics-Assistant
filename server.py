"""
analytics_mcp_server
=====================

Local MCP server exposing reusable, open-source analytics tools to the
CrewAI agents (Supervisor, Data Analyst, Data Scientist).

Run with:
    python mcp_server/server.py

This uses the official `mcp` Python SDK (FastMCP) over stdio, so it can
be registered as a local MCP server in agent configuration or invoked
directly for testing via `mcp dev mcp_server/server.py`.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from tools.csv_profile_tools import mcp_profile_csv
from tools.sql_tools import mcp_run_duckdb_query, mcp_validate_sql
from tools.data_quality_tools import mcp_detect_data_quality_issues, mcp_anomaly_detection_summary
from tools.kpi_tools import mcp_generate_kpi_catalog, mcp_create_data_dictionary
from tools.ml_tools import mcp_recommend_ml_use_cases, mcp_feature_engineering_suggestions
from tools.report_tools import mcp_generate_report_markdown

mcp = FastMCP("analytics_mcp_server")

# ---------------------------------------------------------------------------
# Register all 10 tools
# ---------------------------------------------------------------------------

mcp.tool(name="mcp_profile_csv")(mcp_profile_csv)
mcp.tool(name="mcp_run_duckdb_query")(mcp_run_duckdb_query)
mcp.tool(name="mcp_validate_sql")(mcp_validate_sql)
mcp.tool(name="mcp_detect_data_quality_issues")(mcp_detect_data_quality_issues)
mcp.tool(name="mcp_generate_kpi_catalog")(mcp_generate_kpi_catalog)
mcp.tool(name="mcp_recommend_ml_use_cases")(mcp_recommend_ml_use_cases)
mcp.tool(name="mcp_feature_engineering_suggestions")(mcp_feature_engineering_suggestions)
mcp.tool(name="mcp_anomaly_detection_summary")(mcp_anomaly_detection_summary)
mcp.tool(name="mcp_create_data_dictionary")(mcp_create_data_dictionary)
mcp.tool(name="mcp_generate_report_markdown")(mcp_generate_report_markdown)


if __name__ == "__main__":
    mcp.run(transport="stdio")
