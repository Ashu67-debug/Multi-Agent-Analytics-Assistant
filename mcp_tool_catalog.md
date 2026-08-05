# MCP Tool Catalog — `analytics_mcp_server`

All tools live under `mcp_server/tools/` and are registered in `mcp_server/server.py`.
Every tool that touches the filesystem resolves paths through `tools/safety.resolve_safe_path`,
which sandboxes access to `mcp_server/sample_data/` only.

| # | Tool | Used by | Purpose |
|---|---|---|---|
| 1 | `mcp_profile_csv` | Data Analyst, Data Scientist | Row/column counts, dtypes, missing values, duplicates, sample rows |
| 2 | `mcp_run_duckdb_query` | Data Analyst | Run a read-only SQL query against a CSV via DuckDB |
| 3 | `mcp_validate_sql` | Supervisor, Data Analyst | Validate SQL safety: read-only, has LIMIT, avoids `SELECT *`, has date filter |
| 4 | `mcp_detect_data_quality_issues` | Data Analyst, Data Scientist | Missing values, duplicates, constant/high-cardinality columns, outliers, negative values |
| 5 | `mcp_generate_kpi_catalog` | Data Analyst, Supervisor | Domain-specific KPI catalog (name, formula, grain, business use) |
| 6 | `mcp_recommend_ml_use_cases` | Data Scientist, Supervisor | Suggest ML use cases from dataset columns |
| 7 | `mcp_feature_engineering_suggestions` | Data Scientist | Feature ideas for event/transaction/customer data |
| 8 | `mcp_anomaly_detection_summary` | Data Scientist, Data Analyst | Z-score / IQR based anomaly detection on a numeric column |
| 9 | `mcp_create_data_dictionary` | Data Analyst, Supervisor | Column-level data dictionary with inferred meaning and sample values |
| 10 | `mcp_generate_report_markdown` | Supervisor | Combine tool outputs into a final markdown report |

## Running the server standalone

```bash
cd level_2_multi_agent_mcp_project
python mcp_server/server.py
```

Or inspect it interactively with the MCP dev tools:

```bash
mcp dev mcp_server/server.py
```

## How the app actually connects to it

`mcp_server/client_tools.py` launches the script above as a stdio subprocess
via `crewai_tools.MCPServerAdapter`, lists its 10 tools, and filters them down
per agent role:

| Role | Tools it's given |
|---|---|
| Supervisor | `mcp_validate_sql`, `mcp_generate_kpi_catalog`, `mcp_recommend_ml_use_cases`, `mcp_create_data_dictionary`, `mcp_generate_report_markdown` |
| Data Analyst | `mcp_profile_csv`, `mcp_run_duckdb_query`, `mcp_validate_sql`, `mcp_detect_data_quality_issues`, `mcp_generate_kpi_catalog`, `mcp_create_data_dictionary`, `mcp_anomaly_detection_summary` |
| Data Scientist | `mcp_profile_csv`, `mcp_detect_data_quality_issues`, `mcp_recommend_ml_use_cases`, `mcp_feature_engineering_suggestions`, `mcp_anomaly_detection_summary` |

Each `agents/*.py` builder calls the matching `get_*_mcp_tools()` helper and
appends the result to that agent's local function tools automatically — no
extra wiring is needed in `app.py`.

Requires the `mcpadapt` package (in `requirements.txt`) in addition to `mcp`
and `crewai-tools`.

## Safety guardrails (`mcp_server/tools/safety.py`)

- `resolve_safe_path` — blocks absolute paths, `..` traversal, disallowed extensions (only `.csv`/`.parquet`), and files over 20 MB; always resolves relative to `sample_data/`.
- `validate_readonly_sql` — only `SELECT` / `WITH ... SELECT` allowed; blocks `DELETE, UPDATE, DROP, ALTER, INSERT, MERGE, TRUNCATE, CREATE, ATTACH, COPY`.
- `safe_error_message` — converts exceptions into a short, stack-trace-free string for safe display in the UI.
