"""Reusable validation helpers."""


def is_safe_percentage(value: float) -> bool:
    """Return True when value is a valid percentage."""
    return 0 <= value <= 100
