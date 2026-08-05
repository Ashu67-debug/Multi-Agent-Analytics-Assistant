"""
Supervisor Agent — manages the conversation, reviews chat history,
delegates to specialist agents via CrewAI's native delegation, validates
their output, and returns one final answer to the user.
"""

from __future__ import annotations

import os

import yaml
from crewai import Agent

from function_tools.supervisor_tools import SUPERVISOR_TOOLS
from mcp_server.client_tools import get_supervisor_mcp_tools

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "agents.yaml")

# config/agents.yaml no longer specifies an `llm:` field per agent, so the
# model is configured once here (override with the OLLAMA_MODEL env var).
DEFAULT_LLM = os.environ.get("OLLAMA_MODEL", "ollama/llama3.1")


def _load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_supervisor_agent(llm: str | None = None, include_mcp_tools: bool = True) -> Agent:
    """Build the Supervisor Agent (Analytics Team Supervisor) using
    config/agents.yaml, its 5 local function tools, and (by default) its
    slice of the analytics_mcp_server tools via mcp_server/client_tools.py.

    allow_delegation is True for this agent — when it's the sole agent
    assigned a Task inside a Crew that also includes the Data Scientist
    and Data Analyst agents, CrewAI automatically gives it delegation
    tools to hand off work to them and ask them questions.

    Set include_mcp_tools=False to skip connecting to the MCP server
    (e.g. in unit tests, or if the server isn't available).
    """
    cfg = _load_config()["supervisor_agent"]
    tools = list(SUPERVISOR_TOOLS)
    if include_mcp_tools:
        tools += get_supervisor_mcp_tools()

    return Agent(
        role=cfg["role"],
        goal=cfg["goal"],
        backstory=cfg["backstory"],
        allow_delegation=cfg.get("allow_delegation", True),
        verbose=cfg.get("verbose", True),
        max_iter=cfg.get("max_iter", 8),
        max_retry_limit=cfg.get("max_retry_limit", 2),
        tools=tools,
        llm=llm or DEFAULT_LLM,
    )
