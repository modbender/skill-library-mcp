"""Time parsing utilities for tokenmeter CLI."""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple
import re


def parse_time_input(input_str: str) -> datetime:
    """
    Parse natural language time input into datetime.
    
    Supports:
    - "9am", "2pm" -> today at that hour
    - "yesterday" -> yesterday at 00:00
    - "last week" -> 7 days ago at 00:00
    - ISO timestamps: "2026-02-06 09:00", "2026-02-06T09:00:00"
    - Relative: "1h ago", "2d ago"
    """
    input_str = input_str.strip().lower()
    
    # Handle "Xam" / "Xpm" (e.g., "9am", "2pm")
    if match := re.match(r'(\d{1,2})(am|pm)$', input_str):
        hour = int(match.group(1))
        if match.group(2) == 'pm' and hour != 12:
            hour += 12
        elif match.group(2) == 'am' and hour == 12:
            hour = 0
        return datetime.combine(date.today(), datetime.min.time()).replace(hour=hour)
    
    # Handle "yesterday"
    if input_str == 'yesterday':
        return datetime.combine(date.today() - timedelta(days=1), datetime.min.time())
    
    # Handle "last week"
    if input_str == 'last week':
        return datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
    
    # Handle "Xh ago", "Xd ago"
    if match := re.match(r'(\d+)(h|d|m)\s*ago$', input_str):
        amount = int(match.group(1))
        unit = match.group(2)
        if unit == 'h':
            return datetime.now() - timedelta(hours=amount)
        elif unit == 'd':
            return datetime.now() - timedelta(days=amount)
        elif unit == 'm':
            return datetime.now() - timedelta(minutes=amount)
    
    # Try ISO format parsing
    try:
        # Handle "2026-02-06 09:00" or "2026-02-06T09:00:00"
        if 'T' in input_str or ' ' in input_str:
            return datetime.fromisoformat(input_str)
        # Handle "2026-02-06" (assume 00:00)
        return datetime.combine(date.fromisoformat(input_str), datetime.min.time())
    except ValueError:
        pass
    
    raise ValueError(f"Could not parse time input: '{input_str}'")


def resolve_time_range(
    period: Optional[str] = None,
    since: Optional[str] = None,
    after: Optional[str] = None,
    between: Optional[Tuple[str, str]] = None,
) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    Resolve time range from CLI arguments.
    
    Returns (start, end) datetimes.
    Priority: between > since/after > period
    """
    # Handle --between start end
    if between:
        start_str, end_str = between
        start = parse_time_input(start_str)
        end = parse_time_input(end_str)
        return (start, end)
    
    # Handle --since / --after (alias)
    time_input = since or after
    if time_input:
        start = parse_time_input(time_input)
        return (start, None)  # No end limit
    
    # Handle --period (legacy, default behavior)
    if period:
        now = datetime.now()
        if period == 'day':
            start = datetime.combine(date.today(), datetime.min.time())
        elif period == 'week':
            start = datetime.combine(date.today() - timedelta(days=7), datetime.min.time())
        elif period == 'month':
            start = datetime.combine(date.today() - timedelta(days=30), datetime.min.time())
        else:
            raise ValueError(f"Unknown period: {period}")
        return (start, None)
    
    # Default: today
    return (datetime.combine(date.today(), datetime.min.time()), None)
