import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from function_tools.supervisor_tools import (
    classify_user_request,
    create_agent_work_plan,
    summarize_chat_history,
    validate_final_response_structure,
    estimate_context_usage,
)


def _call(fn, *args, **kwargs):
    """CrewAI @tool wraps functions; use .func if present, else call directly."""
    target = fn.func if hasattr(fn, "func") else fn
    return target(*args, **kwargs)


def test_classify_user_request_dashboard():
    result = _call(classify_user_request, "I want to create a dashboard for revenue and churn.")
    assert result["intent"] == "dashboard"
    assert result["recommended_agent"] == "Data Analyst Agent"


def test_classify_user_request_data_science():
    result = _call(classify_user_request, "Can you recommend an ML model to predict churn?")
    assert result["intent"] == "data_science"
    assert result["recommended_agent"] == "Data Scientist Agent"


def test_create_agent_work_plan_has_steps():
    plan = _call(create_agent_work_plan, "mixed")
    assert "steps" in plan
    assert len(plan["steps"]) > 0


def test_summarize_chat_history_empty():
    summary = _call(summarize_chat_history, [])
    assert "No prior conversation" in summary


def test_validate_final_response_structure_missing_sections():
    result = _call(validate_final_response_structure, "Direct Answer: hello")
    assert result["is_valid"] is False
    assert "Architecture" in result["missing_sections"]


def test_estimate_context_usage():
    result = _call(estimate_context_usage, "hello world", context_window=100)
    assert result["context_window"] == 100
    assert result["estimated_input_tokens"] > 0
