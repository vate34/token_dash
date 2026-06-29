"""Token count formatting."""

from typing import Optional


def fmt(n: Optional[int]) -> str:
    """Format token count for display.
    < 1,000   → direct ("847")
    1K - 1M   → K with 1 decimal ("12.3K")
    >= 1M     → M with 1 decimal ("2.5M")
    """
    if n is None or n == 0:
        return "0"
    if n < 1000:
        return str(n)
    if n < 1_000_000:
        return f"{n / 1000:.1f}K"
    return f"{n / 1_000_000:.1f}M"
