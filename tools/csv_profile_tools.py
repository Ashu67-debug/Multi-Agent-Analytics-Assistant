"""MCP Tool 1: mcp_profile_csv"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .safety import resolve_safe_path


def mcp_profile_csv(file_name: str) -> dict[str, Any]:
    """Read a CSV file from the sample_data folder and return profiling
    information: rows, columns, missing values, duplicates, data types,
    and a small sample of rows.

    Used by: Data Analyst Agent, Data Scientist Agent.
    Allowed libraries: pandas, polars, duckdb.
    """
    path = resolve_safe_path(file_name)
    df = pd.read_csv(path)

    return {
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "missing_values": {c: int(v) for c, v in df.isnull().sum().items()},
        "duplicates": int(df.duplicated().sum()),
        "data_types": {c: str(t) for c, t in df.dtypes.items()},
        "sample_rows": df.head(5).fillna("").to_dict(orient="records"),
    }
