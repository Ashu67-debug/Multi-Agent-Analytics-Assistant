# Demo Script

## 1. Setup

```bash
cd level_2_multi_agent_mcp_project
python -m venv .venv && source .venv/bin/activate      # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# Pull a local model for Ollama (once, outside this repo)
ollama pull llama3.1
ollama serve   # if not already running
```

## 2. (Optional) Run the MCP server standalone to sanity-check it

```bash
mcp dev mcp_server/server.py
```

You should see all 10 tools listed (`mcp_profile_csv`, `mcp_run_duckdb_query`, …).

## 3. Launch the Streamlit app

```bash
streamlit run app.py
```

## 4. Demo prompt

Paste this into the chat box:

```
Design a real-time analytics platform on BigQuery that ingests 1 TB/day of
event data, keeps data quality high, and stays cost-efficient at scale.
```

## 5. Expected behavior to narrate during the demo

1. **Activity timeline** shows: `Thinking → Reasoning → Delegating → Calling function tool → Calling MCP tool → Tool result received → Final answer generated`.
2. **Sidebar → Delegation Trace** shows the Supervisor considering both `Data Scientist Agent` (real-time processing, forecasting, MLOps) and `Data Analyst Agent` (BigQuery table analysis, KPIs).
3. **Data Scientist Agent** contributes the real-time processing / production architecture / scalability reasoning.
4. **Data Analyst Agent** contributes the BigQuery table analysis, KPI, and reporting reasoning.
5. **Supervisor Agent** combines everything into one final answer containing all 8 required sections from `config/tasks.yaml`'s `analytics_manager_task`:
   Direct Recommendation, Production Architecture, Real-Time Processing Strategy, BigQuery Deep Analysis Automation, Scalability For 1 TB/Day, Monitoring And Governance, Implementation Roadmap, Agent Work Summary.

## 6. Fallback demo (no Ollama available)

If Ollama isn't reachable, `app.py` automatically falls back to a deterministic,
local-function-tools-only pipeline (`_fallback_pipeline`) so the same demo
prompt still produces a complete answer with all 8 sections — useful for
grading environments without local LLM access.

## 7. Second demo prompt (SQL/dashboard-only request)

```
Suggest KPIs and a dashboard layout for our events data, and validate this
query: SELECT * FROM events
```

Expected: the Supervisor delegates only to the Data Analyst Agent (no ML/AI
signal in the request), which flags `SELECT *` and a missing date filter via
`validate_sql_safety` / `mcp_validate_sql`.

## 8. Run the automated tests

```bash
pytest tests/ -v
```

31 tests across supervisor tools, analyst tools, scientist tools, and MCP server tools should pass.
