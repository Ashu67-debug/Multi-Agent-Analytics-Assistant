"""MCP Tool 10: mcp_generate_report_markdown"""

from __future__ import annotations

from typing import Any


def mcp_generate_report_markdown(
    dataset_summary: str = "",
    data_quality_findings: str = "",
    recommended_kpis: str = "",
    ml_use_cases: str = "",
    risks: str = "",
    next_steps: str = "",
) -> dict[str, Any]:
    """Combine tool outputs into a single final markdown report with
    required sections: Dataset Summary, Data Quality Findings,
    Recommended KPIs, ML Use Cases, Risks, Next Steps.

    Used by: Supervisor Agent.
    """
    report = f"""# Analytics Report

## Dataset Summary
{dataset_summary or "N/A"}

## Data Quality Findings
{data_quality_findings or "N/A"}

## Recommended KPIs
{recommended_kpis or "N/A"}

## ML Use Cases
{ml_use_cases or "N/A"}

## Risks
{risks or "N/A"}

## Next Steps
{next_steps or "N/A"}
"""
    return {"markdown_report": report}
