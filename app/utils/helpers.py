"""Small helper functions for templates and routes."""

from datetime import datetime


def format_datetime(value: datetime) -> str:
    """Format datetimes for display."""
    if not value:
        return "-"
    return value.strftime("%d %b %Y, %H:%M")
