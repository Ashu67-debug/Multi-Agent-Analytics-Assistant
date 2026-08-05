import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from function_tools.scientist_tools import (
    recommend_ml_problem_type,
    suggest_feature_engineering,
    detect_ml_data_risks,
    recommend_evaluation_metrics,
    create_ml_pipeline_plan,
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "mcp_server", "sample_data")


def _call(fn, *args, **kwargs):
    target = fn.func if hasattr(fn, "func") else fn
    return target(*args, **kwargs)


def test_recommend_ml_problem_type_classification():
    result = _call(recommend_ml_problem_type, "Predict whether a customer will churn.", "churn")
    assert result["problem_type"] == "classification"


def test_recommend_ml_problem_type_forecasting():
    result = _call(recommend_ml_problem_type, "Forecast next month's revenue.")
    assert result["problem_type"] == "forecasting"


def test_suggest_feature_engineering():
    result = _call(suggest_feature_engineering, "transaction")
    assert "days_since_last_purchase" in result["features"]


def test_detect_ml_data_risks_duplicates_and_missing():
    result = _call(detect_ml_data_risks, os.path.join(SAMPLE_DIR, "transactions_sample.csv"), "status")
    assert isinstance(result["risks"], list)
    assert len(result["risks"]) > 0


def test_recommend_evaluation_metrics_classification():
    result = _call(recommend_evaluation_metrics, "classification")
    assert "F1-score" in result["metrics"]


def test_create_ml_pipeline_plan_has_all_sections():
    result = _call(create_ml_pipeline_plan, "classification")
    required = [
        "data_ingestion", "data_validation", "feature_engineering",
        "train_test_split", "model_training", "model_evaluation",
        "model_registry", "inference", "monitoring", "retraining",
    ]
    for key in required:
        assert key in result["pipeline"]
