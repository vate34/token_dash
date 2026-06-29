"""Aggregate token records by time bucket and model."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional

from .record import ModelStats, Record


def aggregate(records: list[Record], now: Optional[datetime] = None) -> dict:
    """Aggregate records into {today, week, month} × {model → ModelStats}.
    
    Returns:
        {
            "source": {                       # "pi-agent" or "opencode"
                "today":  {"models": {model: ModelStats, ...}},
                "week":   {"models": {model: ModelStats, ...}},
                "month":  {"models": {model: ModelStats, ...}},
            }
        }
    """
    if now is None:
        now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=6)
    month_start = today_start - timedelta(days=29)

    result: dict = defaultdict(lambda: _make_buckets())

    for rec in records:
        buckets = result[rec.source]
        ts = rec.ts

        for bname, start in [
            ("today", today_start),
            ("week", week_start),
            ("month", month_start),
        ]:
            if ts >= start:
                models = buckets[bname]["models"]
                if rec.model not in models:
                    models[rec.model] = ModelStats()
                m = models[rec.model]
                m.input += rec.input_tokens
                m.output += rec.output_tokens
                m.cache_read += rec.cache_read_tokens
    return dict(result)


def _make_buckets() -> dict:
    return {
        "today": {"models": {}},
        "week": {"models": {}},
        "month": {"models": {}},
    }
