"""
Local Python function tools for the Supervisor Agent.

These tools do NOT require MCP. They are plain Python functions wrapped
with CrewAI's @tool decorator so the Supervisor Agent can call them
directly for local reasoning (classification, planning, context
management, and response validation).
"""

from __future__ import annotations

import re
from typing import Any

from crewai.tools import tool

# ---------------------------------------------------------------------------
# 1. classify_user_request
# ---------------------------------------------------------------------------

_INTENT_KEYWORDS = {
    "dashboard": ["dashboard", "chart", "visual", "kpi card", "layout"],
    "sql": ["sql", "query", "select", "duckdb", "join"],
    "data_science": [
        "ml", "machine learning", "model", "predict", "classification",
        "regression", "clustering", "forecast", "anomaly", "feature",
    ],
    "data_quality": [
        "data quality", "missing", "duplicate", "null", "outlier", "clean",
    ],
    "architecture": ["architecture", "pipeline", "design", "system", "infra"],
    "analytics": ["kpi", "metric", "revenue", "report", "insight", "trend"],
}


@tool("classify_user_request")
def classify_user_request(user_message: str) -> dict[str, Any]:
    """Classify a user request into an intent category and recommend the
    specialist agent that should handle it.

    Categories: analytics, data_science, sql, dashboard, data_quality,
    architecture, mixed.
    """
    text = user_message.lower()
    hits = {
        intent: sum(1 for kw in kws if kw in text)
        for intent, kws in _INTENT_KEYWORDS.items()
    }
    hits = {k: v for k, v in hits.items() if v > 0}

    # Priority order used to break ties: more specific categories win over
    # the broad "analytics" bucket (e.g. "dashboard" beats "analytics" when
    # both match, since the user asked for something more specific).
    _PRIORITY = ["dashboard", "sql", "data_quality", "architecture", "data_science", "analytics"]

    if not hits:
        intent = "analytics"
    elif len(hits) == 1:
        intent = next(iter(hits))
    else:
        top = max(hits.values())
        top_intents = [k for k, v in hits.items() if v == top]
        if len(top_intents) == 1:
            intent = top_intents[0]
        else:
            ranked = [c for c in _PRIORITY if c in top_intents]
            intent = ranked[0] if ranked else "mixed"

    analyst_intents = {"analytics", "sql", "dashboard", "data_quality", "architecture"}
    scientist_intents = {"data_science"}

    if intent == "mixed":
        recommended_agent = "Data Analyst Agent + Data Scientist Agent"
        reason = "The request spans both business analytics and machine learning concerns."
    elif intent in scientist_intents:
        recommended_agent = "Data Scientist Agent"
        reason = "The user is asking about a machine learning or advanced analytics topic."
    else:
        recommended_agent = "Data Analyst Agent"
        reason = f"The user is asking for {intent.replace('_', ' ')} work."

    return {
        "intent": intent,
        "recommended_agent": recommended_agent,
        "reason": reason,
    }


# ---------------------------------------------------------------------------
# 2. create_agent_work_plan
# ---------------------------------------------------------------------------

_PLAN_TEMPLATES = {
    "analytics": [
        "Ask Data Analyst Agent to profile the dataset.",
        "Ask Data Analyst Agent to suggest KPIs.",
        "Combine outputs into a final answer.",
    ],
    "sql": [
        "Ask Data Analyst Agent to validate the SQL query for safety.",
        "Ask Data Analyst Agent to run the query and explain the result.",
        "Combine outputs into a final answer.",
    ],
    "dashboard": [
        "Ask Data Analyst Agent to profile the dataset.",
        "Ask Data Analyst Agent to suggest KPIs.",
        "Ask Data Analyst Agent to generate a dashboard layout.",
        "Combine outputs into a final answer.",
    ],
    "data_quality": [
        "Ask Data Analyst Agent to profile the dataset.",
        "Ask Data Scientist Agent to detect data quality risks.",
        "Combine outputs into a final answer.",
    ],
    "data_science": [
        "Ask Data Scientist Agent to recommend the ML problem type.",
        "Ask Data Scientist Agent to suggest feature engineering ideas.",
        "Ask Data Scientist Agent to recommend evaluation metrics.",
        "Combine outputs into a final answer.",
    ],
    "architecture": [
        "Ask Data Scientist Agent to create an ML pipeline plan.",
        "Ask Data Analyst Agent to recommend supporting dashboards.",
        "Combine outputs into a final answer.",
    ],
    "mixed": [
        "Ask Data Analyst Agent to profile the dataset.",
        "Ask Data Analyst Agent to suggest dashboard KPIs.",
        "Ask Data Scientist Agent to identify ML use cases.",
        "Ask Data Scientist Agent to suggest feature engineering ideas.",
        "Combine both outputs into a final answer.",
    ],
}


@tool("create_agent_work_plan")
def create_agent_work_plan(intent: str) -> dict[str, Any]:
    """Generate a step-by-step delegation work plan for a given intent
    (as produced by classify_user_request)."""
    steps = _PLAN_TEMPLATES.get(intent, _PLAN_TEMPLATES["mixed"])
    return {"steps": steps}


# ---------------------------------------------------------------------------
# 3. summarize_chat_history
# ---------------------------------------------------------------------------

@tool("summarize_chat_history")
def summarize_chat_history(messages: list[str]) -> str:
    """Compress previous conversation messages into a short summary so the
    context window does not become too large.

    `messages` is a list of prior chat strings (user + assistant turns).
    """
    if not messages:
        return "No prior conversation history."

    joined = " ".join(messages)
    words = joined.split()

    # naive keyword-based summary: pull out capitalized / notable tokens
    keywords = []
    for w in words:
        clean = re.sub(r"[^A-Za-z0-9_]+", "", w)
        if len(clean) > 3 and clean not in keywords:
            keywords.append(clean)
    top_keywords = keywords[:12]

    summary = (
        f"Conversation covered {len(messages)} messages. "
        f"Key topics mentioned: {', '.join(top_keywords) if top_keywords else 'general discussion'}."
    )
    return summary


# ---------------------------------------------------------------------------
# 4. validate_final_response_structure
# ---------------------------------------------------------------------------

REQUIRED_SECTIONS = [
    "Direct Answer",
    "Architecture",
    "Tools Used",
    "Step-by-Step Plan",
    "Risks",
    "Final Recommendation",
]


@tool("validate_final_response_structure")
def validate_final_response_structure(final_response: str) -> dict[str, Any]:
    """Check whether the final response text contains all required sections."""
    missing = [s for s in REQUIRED_SECTIONS if s.lower() not in final_response.lower()]
    return {
        "is_valid": len(missing) == 0,
        "missing_sections": missing,
        "required_sections": REQUIRED_SECTIONS,
    }


# ---------------------------------------------------------------------------
# 5. estimate_context_usage
# ---------------------------------------------------------------------------

@tool("estimate_context_usage")
def estimate_context_usage(text: str, context_window: int = 8192) -> dict[str, Any]:
    """Roughly estimate token usage for a piece of text (approx. 4 chars
    per token) against the model's context window."""
    estimated_input_tokens = max(1, round(len(text) / 4))
    usage_percent = round((estimated_input_tokens / context_window) * 100, 2)
    return {
        "estimated_input_tokens": estimated_input_tokens,
        "context_window": context_window,
        "usage_percent": usage_percent,
    }


SUPERVISOR_TOOLS = [
    classify_user_request,
    create_agent_work_plan,
    summarize_chat_history,
    validate_final_response_structure,
    estimate_context_usage,
]
