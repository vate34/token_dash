"""OpenCode SQLite session reader."""

import json
import os
import sqlite3
from datetime import datetime, timezone

from .record import Record

OPENCODE_DB = os.path.expanduser("~/.local/share/opencode/opencode.db")


def read_opencode_sessions() -> list[Record]:
    """Read opencode session data from SQLite database."""
    records: list[Record] = []
    if not os.path.exists(OPENCODE_DB):
        import sys
        print(f"[TokenDash] OpenCode db not found: {OPENCODE_DB}", file=sys.stderr)
        return records

    try:
        conn = sqlite3.connect(OPENCODE_DB)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT model, tokens_input, tokens_output, tokens_reasoning,
                   tokens_cache_read, tokens_cache_write, time_created
            FROM "session"
            WHERE model IS NOT NULL
            """
        ).fetchall()
        conn.close()

        for row in rows:
            model_name = _parse_model(row["model"])
            ts = datetime.fromtimestamp(row["time_created"] / 1000, tz=timezone.utc)
            records.append(
                Record(
                    source="opencode",
                    model=model_name,
                    ts=ts,
                    input_tokens=row["tokens_input"] or 0,
                    output_tokens=(row["tokens_output"] or 0) + (row["tokens_reasoning"] or 0),
                    cache_read_tokens=row["tokens_cache_read"] or 0,
                    cache_write_tokens=row["tokens_cache_write"] or 0,
                )
            )
    except Exception as e:
        import sys
        print(f"[TokenDash] Error reading opencode db: {e}", file=sys.stderr)

    return records


def _parse_model(model_col: str) -> str:
    """Parse model name from JSON column, e.g. '{"id":"deepseek-v4-flash","providerID":"opencode"}'."""
    if not model_col:
        return "unknown"
    try:
        info = json.loads(model_col)
        return info.get("id", "unknown")
    except (json.JSONDecodeError, TypeError):
        return str(model_col)
