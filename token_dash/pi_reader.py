"""pi-agent session JSONL reader."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .record import Record


PI_SESSIONS_DIR = os.path.expanduser("~/.pi/agent/sessions")


def read_pi_agent_sessions() -> list[Record]:
    """Read all pi-agent session JSONL files and extract token usage records."""
    records: list[Record] = []
    root = Path(PI_SESSIONS_DIR)
    if not root.is_dir():
        import sys
        print(f"[TokenDash] PI sessions dir not found: {PI_SESSIONS_DIR}", file=sys.stderr)
        return records

    for project_dir in root.iterdir():
        if not project_dir.is_dir():
            continue
        for fname in project_dir.iterdir():
            if not fname.suffix == ".jsonl":
                continue
            _parse_jsonl(fname, records)

    return records


def _parse_jsonl(path: Path, records: list[Record]) -> None:
    try:
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") != "message":
                    continue

                msg = entry.get("message", {})
                if msg.get("role") != "assistant":
                    continue

                usage = msg.get("usage", {})
                if not usage:
                    continue

                ts = _parse_timestamp(msg.get("timestamp") or entry.get("timestamp"))
                if ts is None:
                    continue

                model = msg.get("model", "unknown")
                records.append(
                    Record(
                        source="pi-agent",
                        model=model,
                        ts=ts,
                        input_tokens=usage.get("input", 0),
                        output_tokens=usage.get("output", 0),
                        cache_read_tokens=usage.get("cacheRead", 0),
                        cache_write_tokens=usage.get("cacheWrite", 0),
                    )
                )
    except Exception as e:
        import sys
        print(f"[TokenDash] Error reading {path}: {e}", file=sys.stderr)


def _parse_timestamp(val: Any) -> Optional[datetime]:
    if isinstance(val, (int, float)):
        # epoch ms
        return datetime.fromtimestamp(val / 1000, tz=timezone.utc)
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass
    return None
