"""
mcp_server.client_tools
========================

Bridges the standalone `analytics_mcp_server` (mcp_server/server.py) into
CrewAI by launching it as a stdio subprocess and wrapping its 10 tools as
CrewAI-compatible tool objects.

Without this module, `analytics_mcp_server` is just a script that can be
poked at with `mcp dev mcp_server/server.py` — nothing in the Streamlit app
would actually be *using* it. This module is what turns it into tools each
agent can call during a crew run.

Each `get_*_mcp_tools()` function returns only the subset of the 10 tools
that role is meant to use, per the "Used by" notes documented on each tool
in docs/mcp_tool_catalog.md.
"""

from __future__ import annotations

import os

from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

_SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "server.py")

_SERVER_PARAMS = StdioServerParameters(
    command="python",
    args=[_SERVER_SCRIPT],
)

# Which of the 10 analytics_mcp_server tools each agent role may call.
SUPERVISOR_ALLOWED_TOOLS = {
    "mcp_validate_sql",
    "mcp_generate_kpi_catalog",
    "mcp_recommend_ml_use_cases",
    "mcp_create_data_dictionary",
    "mcp_generate_report_markdown",
}

ANALYST_ALLOWED_TOOLS = {
    "mcp_profile_csv",
    "mcp_run_duckdb_query",
    "mcp_validate_sql",
    "mcp_detect_data_quality_issues",
    "mcp_generate_kpi_catalog",
    "mcp_create_data_dictionary",
    "mcp_anomaly_detection_summary",
}

SCIENTIST_ALLOWED_TOOLS = {
    "mcp_profile_csv",
    "mcp_detect_data_quality_issues",
    "mcp_recommend_ml_use_cases",
    "mcp_feature_engineering_suggestions",
    "mcp_anomaly_detection_summary",
}


def _connect_and_filter(allowed_tool_names: set[str]) -> list:
    """Open a stdio connection to analytics_mcp_server and keep only the
    tools this role is allowed to call.

    Note: `MCPServerAdapter` owns the subprocess it spawns. The tool
    objects it returns stay usable for as long as that adapter/subprocess
    is alive, which in this app is the lifetime of a single crew run
    (see app.py — a fresh set of agents, and therefore a fresh MCP
    connection, is built for every user message).
    """
    adapter = MCPServerAdapter(_SERVER_PARAMS)
    return [t for t in adapter.tools if t.name in allowed_tool_names]


def get_supervisor_mcp_tools() -> list:
    """MCP tools the Supervisor Agent may call directly (validation and
    report assembly — it otherwise prefers to delegate)."""
    return _connect_and_filter(SUPERVISOR_ALLOWED_TOOLS)


def get_analyst_mcp_tools() -> list:
    """MCP tools available to the Data Analyst Agent (profiling, SQL,
    data quality, KPIs, data dictionary, anomaly checks)."""
    return _connect_and_filter(ANALYST_ALLOWED_TOOLS)


def get_scientist_mcp_tools() -> list:
    """MCP tools available to the Data Scientist Agent (profiling, data
    quality, ML use cases, feature engineering, anomaly detection)."""
    return _connect_and_filter(SCIENTIST_ALLOWED_TOOLS)
