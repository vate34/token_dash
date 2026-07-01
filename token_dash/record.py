"""Shared types for token records."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Record:
    source: str  # "pi-agent" | "opencode"
    model: str
    ts: datetime
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int


@dataclass
class ModelStats:
    input: int = 0
    output: int = 0
    cache_read: int = 0
