# Architecture

## Overview

```
User
 ↓
Streamlit Chat UI  (app.py)
 ↓
CrewAI Hierarchical Crew (Process.hierarchical)
 ↓
Supervisor Agent  (manager_agent)
 ↓
Delegates to:
 ├── Data Analyst Agent
 └── Data Scientist Agent
 ↓
Agents use:
 ├── Local Function Tools   (function_tools/*.py)
 └── Local MCP Server Tools (mcp_server/server.py, fetched via mcp_server/client_tools.py)
 ↓
Final Answer in Streamlit
```

## Components

| Layer | Location | Responsibility |
|---|---|---|
| UI | `app.py` | Chat window, activity timeline, sidebar (agents, tools, context usage, delegation trace) |
| Orchestration | `agents/*.py`, `config/agents.yaml`, `config/tasks.yaml` | CrewAI agent + task definitions, hierarchical process with Supervisor as manager |
| Local reasoning tools | `function_tools/*.py` | Fast, dependency-light Python tools called directly by each agent (no MCP round trip) |
| Reusable analytics tools | `mcp_server/` | A standalone MCP server (`analytics_mcp_server`) exposing 10 tools over stdio via the `mcp` Python SDK (FastMCP) |
| Safety layer | `mcp_server/tools/safety.py` | Path sandboxing to `sample_data/`, SQL statement allow-listing, file size/extension checks |
| Sample data | `mcp_server/sample_data/` | `events_sample.csv`, `transactions_sample.csv`, `customers_sample.csv` |

## Why both Function Tools and an MCP Server?

- **Function tools** are private to each agent, fast to call, and don't require inter-process communication. They're used for planning, classification, and lightweight local logic (e.g. `classify_user_request`, `validate_sql_safety`).
- **MCP tools** are reusable across agents and processes — any MCP-compatible client (not just this CrewAI app) could reuse `analytics_mcp_server`. They also enforce a stronger sandboxing boundary (`safety.py`) since they touch the filesystem and run SQL.

## How agents actually get the MCP tools (`mcp_server/client_tools.py`)

`analytics_mcp_server` (`mcp_server/server.py`) is a standalone script — on its
own it doesn't hand anything to CrewAI. `mcp_server/client_tools.py` is the
adapter that closes that gap:

1. It launches `mcp_server/server.py` as a stdio subprocess via
   `crewai_tools.MCPServerAdapter` + `mcp.StdioServerParameters`.
2. It lists all 10 registered tools over that connection.
3. It filters them down to the subset each role is meant to use
   (`SUPERVISOR_ALLOWED_TOOLS`, `ANALYST_ALLOWED_TOOLS`,
   `SCIENTIST_ALLOWED_TOOLS`), matching the "Used by" notes in
   `docs/mcp_tool_catalog.md`.

Each `agents/*.py` builder function calls the matching `get_*_mcp_tools()`
helper and appends the result to that agent's local function tools, so by
the time `Agent(...)` is constructed it already holds both tool types. A
fresh MCP connection (and therefore a fresh `python mcp_server/server.py`
subprocess) is opened every time an agent is built — in this app that's once
per user message, since `app.py` builds new agents on every `run_crew` call.

## Delegation flow (native CrewAI delegation, single manager task)

`config/tasks.yaml` defines one task — `analytics_manager_task` — assigned to the
Supervisor Agent. Because `allow_delegation: true` for the Supervisor
(`config/agents.yaml`) and the Data Scientist and Data Analyst agents are also
members of the Crew, CrewAI automatically equips the Supervisor with
delegation tools ("Delegate work to co-worker" / "Ask question to co-worker").

1. The Supervisor reads `{chat_history}` and `{user_prompt}` (interpolated into
   the task description at `crew.kickoff(inputs=...)`).
2. It decides whether the request needs the **Data Scientist Agent** (ML, AI,
   statistics, forecasting, GenAI/RAG/LLM, real-time processing architecture),
   the **Data Analyst Agent** (SQL, dashboards, KPIs, EDA, BigQuery table
   analysis), or both — and delegates accordingly.
3. It combines the specialist response(s) into one final answer containing all
   8 required sections: Direct Recommendation, Production Architecture,
   Real-Time Processing Strategy, BigQuery Deep Analysis Automation,
   Scalability For 1 TB/Day, Monitoring And Governance, Implementation
   Roadmap, Agent Work Summary.

`Crew(process=Process.sequential, tasks=[manager_task])` is used (not
`Process.hierarchical`) since the Supervisor's own native delegation — not a
separate manager process — is what fans work out to the specialists here.

## Resilience

`app.py` wraps the CrewAI hierarchical run in a try/except. If Ollama or the MCP server are not reachable in a given environment, it falls back to a deterministic pipeline built only from local function tools (`_fallback_pipeline`), so the UI is always demonstrable end-to-end without exposing raw stack traces to the user.
