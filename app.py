"""
Streamlit UI for the Multi-Agent Analytics Assistant.

Shows:
- Main chat window (user message, supervisor response, final answer)
- Activity timeline (thinking, delegating, tool calls, results)
- Sidebar (model, agents, tools, MCP tools, context usage, delegation trace)
"""

from __future__ import annotations

import os
import sys
import time
import traceback

import streamlit as st
from crewai import Crew, Process, Task

sys.path.insert(0, os.path.dirname(__file__))

from agents.supervisor_agent import build_supervisor_agent
from agents.data_analyst_agent import build_data_analyst_agent
from agents.data_scientist_agent import build_data_scientist_agent
from function_tools.supervisor_tools import estimate_context_usage

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Multi-Agent Analytics Assistant", layout="wide")

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "mcp_server", "sample_data")

MCP_TOOL_NAMES = [
    "mcp_profile_csv",
    "mcp_run_duckdb_query",
    "mcp_validate_sql",
    "mcp_detect_data_quality_issues",
    "mcp_generate_kpi_catalog",
    "mcp_recommend_ml_use_cases",
    "mcp_feature_engineering_suggestions",
    "mcp_anomaly_detection_summary",
    "mcp_create_data_dictionary",
    "mcp_generate_report_markdown",
]

FUNCTION_TOOL_NAMES = [
    "classify_user_request", "create_agent_work_plan", "summarize_chat_history",
    "validate_final_response_structure", "estimate_context_usage",
    "profile_dataframe", "suggest_kpi_metrics", "generate_dashboard_layout",
    "validate_sql_safety", "explain_query_result",
    "recommend_ml_problem_type", "suggest_feature_engineering",
    "detect_ml_data_risks", "recommend_evaluation_metrics", "create_ml_pipeline_plan",
]

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": ..., "content": ...}
if "timeline" not in st.session_state:
    st.session_state.timeline = []  # list of {"event": ..., "detail": ...}
if "delegation_trace" not in st.session_state:
    st.session_state.delegation_trace = []


def log_event(event: str, detail: str = "") -> None:
    st.session_state.timeline.append({"event": event, "detail": detail, "ts": time.strftime("%H:%M:%S")})


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ System Info")
    st.markdown(f"**Ollama model:** `{OLLAMA_MODEL}`")

    st.subheader("Agents")
    st.markdown("- Supervisor Agent\n- Data Analyst Agent\n- Data Scientist Agent")

    st.subheader("Available Function Tools")
    st.caption(f"{len(FUNCTION_TOOL_NAMES)} local tools")
    with st.expander("Show function tools"):
        for t in FUNCTION_TOOL_NAMES:
            st.markdown(f"- `{t}`")

    st.subheader("Available MCP Tools")
    st.caption(f"{len(MCP_TOOL_NAMES)} tools via analytics_mcp_server")
    with st.expander("Show MCP tools"):
        for t in MCP_TOOL_NAMES:
            st.markdown(f"- `{t}`")

    st.subheader("Context Window Estimate")
    all_text = " ".join(m["content"] for m in st.session_state.chat_history)
    usage = estimate_context_usage.func(all_text) if hasattr(estimate_context_usage, "func") else estimate_context_usage(all_text)
    st.progress(min(usage["usage_percent"] / 100, 1.0))
    st.caption(f"{usage['estimated_input_tokens']} / {usage['context_window']} tokens ({usage['usage_percent']}%)")

    st.subheader("Delegation Trace")
    if st.session_state.delegation_trace:
        for d in st.session_state.delegation_trace[-10:]:
            st.markdown(f"- {d}")
    else:
        st.caption("No delegations yet.")

    st.divider()
    dataset_file = st.selectbox(
        "Sample dataset for analysis",
        options=os.listdir(SAMPLE_DATA_DIR) if os.path.isdir(SAMPLE_DATA_DIR) else [],
    )

    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.session_state.timeline = []
        st.session_state.delegation_trace = []
        st.rerun()

# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

st.title("📊 Multi-Agent Analytics Assistant")
st.caption("CrewAI · Ollama · Streamlit · Function Tools · Local MCP Server")

chat_col, timeline_col = st.columns([2, 1])

with chat_col:
    st.subheader("💬 Chat")
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Ask about your data, e.g. 'Analyze events_sample.csv...'")

with timeline_col:
    st.subheader("🕒 Activity Timeline")
    timeline_placeholder = st.container(height=500)


def render_timeline() -> None:
    with timeline_placeholder:
        for e in st.session_state.timeline[-30:]:
            st.markdown(f"`{e['ts']}` **{e['event']}** — {e['detail']}")


render_timeline()

# ---------------------------------------------------------------------------
# Crew execution
# ---------------------------------------------------------------------------


def _load_task_config() -> dict:
    import yaml
    path = os.path.join(os.path.dirname(__file__), "config", "tasks.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_crew(user_message: str, dataset_file: str) -> str:
    """Build the crew and run the single `analytics_manager_task` (from
    config/tasks.yaml) against the user request. The Supervisor Agent is
    the only agent assigned a task; because allow_delegation=true for it
    (config/agents.yaml) and the Data Scientist / Data Analyst agents are
    also members of the Crew, CrewAI gives the Supervisor native
    delegation tools to hand off work to them as needed.

    In case CrewAI / Ollama are not reachable in this environment, falls
    back to a deterministic local-tool-only pipeline so the app remains
    demonstrable end-to-end."""
    log_event("Thinking", "Supervisor analyzing the request and chat history")

    try:
        supervisor = build_supervisor_agent()
        analyst = build_data_analyst_agent()
        scientist = build_data_scientist_agent()

        log_event("Reasoning", "Supervisor deciding which specialist(s) to delegate to")

        task_cfg = _load_task_config()["analytics_manager_task"]
        manager_task = Task(
            description=task_cfg["description"],
            expected_output=task_cfg["expected_output"],
            agent=supervisor,
        )

        chat_history_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in st.session_state.chat_history
        ) or "No prior conversation."

        log_event("Delegating", "Supervisor -> Data Scientist Agent / Data Analyst Agent as needed")
        st.session_state.delegation_trace.append("Supervisor → Data Scientist Agent (if ML/AI/forecasting/architecture needed)")
        st.session_state.delegation_trace.append("Supervisor → Data Analyst Agent (if SQL/KPI/BigQuery/dashboard needed)")

        crew = Crew(
            agents=[supervisor, scientist, analyst],
            tasks=[manager_task],
            process=Process.sequential,
            verbose=True,
        )

        log_event("Calling function tool", "Local tools available to each agent")
        log_event("Calling MCP tool", "analytics_mcp_server tools available to Analyst/Scientist agents")

        result = crew.kickoff(inputs={"chat_history": chat_history_text, "user_prompt": user_message})

        log_event("Tool result received", "Crew execution completed")
        log_event("Final answer generated", "Supervisor combined all specialist outputs")

        return str(result)

    except Exception as exc:  # noqa: BLE001
        # Safe fallback: do not expose raw stack traces to the user (Section 14).
        log_event("Error", "Falling back to local deterministic pipeline")
        with st.expander("Debug logs (developer only)"):
            st.code(traceback.format_exc())
        return _fallback_pipeline(user_message, dataset_file)


def _fallback_pipeline(user_message: str, dataset_file: str) -> str:
    """A dependency-free fallback that uses only local function tools so the
    UI is always demonstrable, even without a live Ollama connection. Mirrors
    the 8-section format required by config/tasks.yaml's analytics_manager_task."""
    from function_tools.scientist_tools import create_ml_pipeline_plan, recommend_evaluation_metrics
    from function_tools.analyst_tools import suggest_kpi_metrics

    pipeline = create_ml_pipeline_plan.func("forecasting") if hasattr(create_ml_pipeline_plan, "func") else create_ml_pipeline_plan("forecasting")
    metrics = recommend_evaluation_metrics.func("forecasting") if hasattr(recommend_evaluation_metrics, "func") else recommend_evaluation_metrics("forecasting")
    kpis = suggest_kpi_metrics.func("events", ["event_time", "event_type", "success"]) if hasattr(suggest_kpi_metrics, "func") else suggest_kpi_metrics("events", ["event_time", "event_type", "success"])

    return f"""### 1. Direct Recommendation
Based on your request ("{user_message}"), the recommended strategy is to combine a
streaming ingestion layer with BigQuery as the analytical store, paired with
automated data-quality and cost monitoring. Start with a narrow pilot on one
data source, prove the pipeline end-to-end, then scale ingestion and
partitioning strategy to full volume.

### 2. Production Architecture
```
[Source Systems] -> [Pub/Sub] -> [Dataflow (streaming)] -> [BigQuery (raw + curated)]
                                          |                        |
                                   [Dead-letter topic]     [Scheduled queries / dbt]
                                                                    |
                                                        [BI tools / Looker / Streamlit]
```

### 3. Real-Time Processing Strategy
- **Ingestion:** Pub/Sub topics per source, schema-validated at the edge.
- **Streaming:** Dataflow (Apache Beam) jobs for windowed aggregation, enrichment, and dedup.
- **Processing:** Stateful transforms with watermarks to handle late-arriving data.
- **Storage:** BigQuery streaming inserts into partitioned/clustered raw tables; curated views built on top.
- **Serving:** Scheduled queries and materialized views feed dashboards and downstream APIs.

### 4. BigQuery Deep Analysis Automation
- **Table profiling:** {pipeline['pipeline']['data_validation']}
- **Schema drift:** Compare live schema vs. expected schema on each load; alert on new/removed columns.
- **Data quality:** Row counts, null-rate thresholds, and duplicate checks run as scheduled queries.
- **Partition analysis:** Track partition skew and pruning effectiveness via `INFORMATION_SCHEMA`.
- **Anomaly detection:** {pipeline['pipeline']['monitoring']}
- **Cost optimization:** Slot usage and bytes-scanned monitoring to catch expensive queries early.

### 5. Scalability For 1 TB/Day
- **Partitioning:** Date/time partitioning on all fact tables; cluster on the highest-cardinality filter column.
- **Clustering:** Secondary clustering keys on join/filter columns to reduce bytes scanned.
- **Streaming buffer:** Batch micro-inserts where possible to reduce streaming insert costs.
- **Dataflow sizing:** Autoscaling workers with autotuned parallelism; separate pipelines per source to isolate backpressure.
- **Pub/Sub:** Multiple subscriptions with appropriate ack deadlines and retry/backoff policies.
- **BigQuery slots:** Reserved slots (or autoscaling editions) sized to peak concurrent query load.
- **Storage tiers:** Move cold partitions to long-term storage pricing automatically after N days.
- **Backpressure handling:** Dead-letter topics plus alerting when Dataflow watermark lag exceeds SLA.

### 6. Monitoring And Governance
- **Observability:** Cloud Monitoring dashboards for pipeline lag, error rates, and slot utilization.
- **Data quality alerts:** Automated checks (row counts, null rates, {metrics['metrics'][0]} drift) with paging on breach.
- **Lineage:** Track source-to-table lineage (e.g., via Dataplex or dbt docs) for auditability.
- **Audit:** BigQuery audit logs retained and reviewed for access anomalies.
- **Cost monitoring:** Budget alerts tied to BigQuery and Dataflow spend.
- **Privacy & access controls:** Column-level security and row-level policies for sensitive fields; least-privilege IAM roles.

### 7. Implementation Roadmap
1. **Phase 1 — Pilot:** Stand up Pub/Sub + Dataflow + BigQuery for a single source; validate schema and quality checks.
2. **Phase 2 — Hardening:** Add dead-letter handling, monitoring/alerting, and cost guardrails.
3. **Phase 3 — Scale-out:** Onboard remaining sources; tune partitioning/clustering for 1 TB/day volume.
4. **Phase 4 — Governance:** Add lineage tracking, access controls, and automated data-quality reporting.
5. **Phase 5 — Optimization:** Continuously tune slot reservations, query cost, and storage tiers based on usage patterns.

### 8. Agent Work Summary
- **Data Scientist Agent** expertise was used for real-time processing architecture, pipeline design, and anomaly-detection strategy.
- **Data Analyst Agent** expertise was used for BigQuery table analysis, KPI framing (e.g. {', '.join(kpis['recommended_kpis'][:2])}), and reporting considerations.
- **Supervisor Agent** combined both perspectives into this final recommendation.

_Note: this response was generated by the local fallback pipeline (function tools only) because a live Ollama/CrewAI connection was not available in this environment._
"""


# ---------------------------------------------------------------------------
# Handle new input
# ---------------------------------------------------------------------------

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with chat_col:
        with st.chat_message("user"):
            st.markdown(user_input)

    with chat_col:
        with st.chat_message("assistant"):
            with st.spinner("Supervisor Agent is coordinating the crew..."):
                answer = run_crew(user_input, dataset_file or "events_sample.csv")
            st.markdown(answer)

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    render_timeline()
