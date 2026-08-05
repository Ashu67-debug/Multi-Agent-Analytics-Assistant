"""
Data Scientist Agent (Senior Data Scientist) — ML, AI, statistics,
experimentation, forecasting, GenAI/RAG/LLM, and production ML/MLOps
strategy. Receives delegated work from the Supervisor Agent.
"""

from __future__ import annotations

import os

import yaml
from crewai import Agent

from function_tools.scientist_tools import SCIENTIST_TOOLS
from mcp_server.client_tools import get_scientist_mcp_tools

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "agents.yaml")

DEFAULT_LLM = os.environ.get("OLLAMA_MODEL", "ollama/llama3.1")


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_data_scientist_agent(llm: str | None = None, include_mcp_tools: bool = True) -> Agent:
    """Build the Data Scientist Agent using config/agents.yaml, its 5 local
    function tools, and (by default) its slice of the analytics_mcp_server
    tools via mcp_server/client_tools.py.

    Set include_mcp_tools=False to skip connecting to the MCP server
    (e.g. in unit tests, or if the server isn't available).
    """
    cfg = _load_config()["data_scientist_agent"]
    tools = list(SCIENTIST_TOOLS)
    if include_mcp_tools:
        tools += get_scientist_mcp_tools()

    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        allow_delegation=cfg.get("allow_delegation", False),
        verbose=cfg.get("verbose", True),
        max_iter=cfg.get("max_iter", 5),
        max_retry_limit=cfg.get("max_retry_limit", 2),
        tools=tools,
        llm=llm or DEFAULT_LLM,
    )
