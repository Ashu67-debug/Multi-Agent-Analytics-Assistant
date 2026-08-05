"""MCP Tool 2: mcp_run_duckdb_query
MCP Tool 3: mcp_validate_sql
"""

from __future__ import annotations

import re
from typing import Any

import duckdb

from .safety import SAMPLE_DATA_DIR, resolve_safe_path, validate_readonly_sql, safe_error_message

try:
    import sqlglot
    _HAS_SQLGLOT = True
except ImportError:  # pragma: no cover
    _HAS_SQLGLOT = False


def mcp_run_duckdb_query(sql_query: str, file_name: str) -> dict[str, Any]:
    """Run a safe, read-only SQL query against a local CSV/Parquet file
    using DuckDB.

    Used by: Data Analyst Agent.
    Allowed libraries: duckdb, pandas, polars.
    Safety: only SELECT/WITH queries allowed; DELETE/UPDATE/DROP/ALTER/
    INSERT/MERGE/TRUNCATE/CREATE are blocked.
    """
    try:
        validate_readonly_sql(sql_query)
        path = resolve_safe_path(file_name)

        con = duckdb.connect(database=":memory:")
        con.execute(f"CREATE VIEW dataset AS SELECT * FROM read_csv_auto('{path}')")
        result_df = con.execute(sql_query.replace(file_name, "dataset")).fetchdf()
        con.close()

        return {
            "success": True,
            "row_count": int(len(result_df)),
            "columns": list(result_df.columns),
            "rows": result_df.head(50).fillna("").to_dict(orient="records"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": safe_error_message(exc)}


def mcp_validate_sql(sql_query: str) -> dict[str, Any]:
    """Validate SQL query safety before execution: read-only, has a LIMIT,
    avoids SELECT *, has a date filter for event-style data, and uses a
    partition column when available.

    Used by: Supervisor Agent, Data Analyst Agent.
    Allowed libraries: sqlglot, sqlparse, re.
    """
    upper = sql_query.upper()
    checks = {
        "is_read_only": True,
        "has_limit": bool(re.search(r"\bLIMIT\b", upper)),
        "avoids_select_star": not bool(re.search(r"SELECT\s+\*", upper)),
        "has_date_filter": bool(re.search(r"\bWHERE\b.*(DATE|TIME)", upper, re.DOTALL)),
        "uses_partition_column": bool(re.search(r"\bPARTITION\b|\bYEAR\b|\bMONTH\b", upper)),
    }

    try:
        validate_readonly_sql(sql_query)
    except Exception:
        checks["is_read_only"] = False

    syntax_valid = True
    syntax_error = None
    if _HAS_SQLGLOT:
        try:
            sqlglot.parse_one(sql_query)
        except Exception as exc:  # noqa: BLE001
            syntax_valid = False
            syntax_error = str(exc)

    passed = sum(1 for v in checks.values() if v)
    return {
        "syntax_valid": syntax_valid,
        "syntax_error": syntax_error,
        "checks": checks,
        "score": f"{passed}/{len(checks)}",
        "is_safe_to_run": checks["is_read_only"] and syntax_valid,
    }
