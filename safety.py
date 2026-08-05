"""
Shared safety helpers used across all MCP server tools.

Implements the guardrails required in Section 14 of the project spec:
- No arbitrary file access outside the sample_data folder
- No shell command execution from user input
- File size limits
- File extension validation
- SQL statement safety checks
"""

from __future__ import annotations

import os
import re

# sample_data lives one directory above this file: mcp_server/sample_data
SAMPLE_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "sample_data")
)

ALLOWED_EXTENSIONS = {".csv", ".parquet"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

BLOCKED_SQL_KEYWORDS = [
    "DELETE", "UPDATE", "DROP", "ALTER", "INSERT",
    "MERGE", "TRUNCATE", "CREATE", "ATTACH", "COPY",
]


class UnsafePathError(Exception):
    pass


class UnsafeSQLError(Exception):
    pass


def resolve_safe_path(file_name: str) -> str:
    """Resolve a file name to an absolute path, guaranteeing it stays
    inside SAMPLE_DATA_DIR. Blocks path traversal, absolute paths, and
    disallowed extensions/sizes."""
    if os.path.isabs(file_name) or ".." in file_name.split(os.sep):
        raise UnsafePathError(f"Access outside sample_data folder is not allowed: {file_name}")

    candidate = os.path.abspath(os.path.join(SAMPLE_DATA_DIR, file_name))

    if not candidate.startswith(SAMPLE_DATA_DIR + os.sep) and candidate != SAMPLE_DATA_DIR:
        raise UnsafePathError(f"Access outside sample_data folder is not allowed: {file_name}")

    ext = os.path.splitext(candidate)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UnsafePathError(f"File extension not allowed: {ext}")

    if not os.path.exists(candidate):
        raise FileNotFoundError(f"File not found in sample_data: {file_name}")

    if os.path.getsize(candidate) > MAX_FILE_SIZE_BYTES:
        raise UnsafePathError(f"File exceeds max allowed size ({MAX_FILE_SIZE_BYTES} bytes): {file_name}")

    return candidate


def validate_readonly_sql(sql_query: str) -> None:
    """Raise UnsafeSQLError if the query contains any destructive/DDL
    statement. Only read-only SELECT/WITH queries are allowed."""
    upper = sql_query.upper()

    stripped = upper.strip()
    if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
        raise UnsafeSQLError("Only read-only SELECT (or WITH ... SELECT) queries are allowed.")

    for kw in BLOCKED_SQL_KEYWORDS:
        if re.search(rf"\b{kw}\b", upper):
            raise UnsafeSQLError(f"Blocked SQL keyword detected: {kw}")


def safe_error_message(exc: Exception) -> str:
    """Return a safe, non-stack-trace error message suitable for display
    to end users (Section 14: do not expose raw stack traces)."""
    return f"{type(exc).__name__}: {str(exc)}"
