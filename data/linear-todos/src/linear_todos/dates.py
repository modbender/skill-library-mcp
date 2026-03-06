"""Smart date parsing for natural language dates."""

import re
from datetime import datetime, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

import dateparser


class DateParser:
    """Parses natural language dates into ISO format dates."""
    
    # Day name to number mapping (Monday=1, Sunday=7)
    DAY_MAP = {
        "monday": 1,
        "tuesday": 2,
        "wednesday": 3,
        "thursday": 4,
        "friday": 5,
        "saturday": 6,
        "sunday": 7,
    }
    
    @classmethod
    def parse(cls, input_str: str, base_date: Optional[datetime] = None) -> Optional[str]:
        """Parse a natural language date string into YYYY-MM-DD format.
        
        Supports:
        - today, tomorrow
        - in X days/weeks
        - next Monday, next Tuesday, etc.
        - this Monday, this Tuesday, etc.
        - Monday, Tuesday, etc. (next occurrence)
        - ISO dates (2025-04-15)
        
        Args:
            input_str: Natural language date string
            base_date: Base date for relative calculations (default: now)
            
        Returns:
            Date string in YYYY-MM-DD format or None if parsing fails
        """
        if not input_str:
            return None
        
        if base_date is None:
            base_date = datetime.utcnow()
        
        input_lower = input_str.lower().strip()
        today = base_date.date()
        today_weekday = today.isoweekday()  # 1=Monday, 7=Sunday
        
        # Handle "today"
        if input_lower == "today":
            return today.isoformat()
        
        # Handle "tomorrow"
        if input_lower == "tomorrow":
            return (today + timedelta(days=1)).isoformat()
        
        # Handle "in X days/weeks"
        match = re.match(r'^in\s+(\d+)\s+(day|days|week|weeks)$', input_lower)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if unit.startswith("week"):
                num *= 7
            return (today + timedelta(days=num)).isoformat()
        
        # Handle "next Monday", "next Tuesday", etc.
        match = re.match(r'^next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$', input_lower)
        if match:
            target_day = match.group(1)
            target_num = cls.DAY_MAP[target_day]
            # Days until next occurrence (always at least 7 days away for "next X")
            days_until = (7 - today_weekday + target_num)
            if days_until <= 7:
                days_until += 7
            return (today + timedelta(days=days_until)).isoformat()
        
        # Handle "this Monday", "this Tuesday", etc. (current week or next if passed)
        match = re.match(r'^this\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$', input_lower)
        if match:
            target_day = match.group(1)
            target_num = cls.DAY_MAP[target_day]
            # Days until target day
            days_until = target_num - today_weekday
            if days_until <= 0:
                days_until += 7
            return (today + timedelta(days=days_until)).isoformat()
        
        # Handle standalone day names (same as "this X")
        if input_lower in cls.DAY_MAP:
            target_num = cls.DAY_MAP[input_lower]
            days_until = target_num - today_weekday
            if days_until <= 0:
                days_until += 7
            return (today + timedelta(days=days_until)).isoformat()
        
        # Handle "in X weeks on Day" (e.g., "in 2 weeks on Monday")
        match = re.match(r'^in\s+(\d+)\s+weeks?\s+on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)$', input_lower)
        if match:
            weeks = int(match.group(1))
            target_day = match.group(2)
            target_num = cls.DAY_MAP[target_day]
            # Calculate base days from weeks
            base_days = weeks * 7
            days_until = target_num - today_weekday
            if days_until <= 0:
                days_until += 7
            total_days = base_days + days_until
            return (today + timedelta(days=total_days)).isoformat()
        
        # Try ISO date format directly
        try:
            datetime.strptime(input_str, "%Y-%m-%d")
            return input_str
        except ValueError:
            pass
        
        # Try dateparser as fallback
        parsed = dateparser.parse(input_str, settings={
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': base_date,
        })
        if parsed:
            return parsed.date().isoformat()
        
        return None
    
    @classmethod
    def to_iso_datetime(cls, date_str: str, end_of_day: bool = True, tz: Optional[ZoneInfo] = None) -> str:
        """Convert a date string to ISO datetime format for Linear API.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            end_of_day: If True, set time to 23:59:59 in the specified timezone
            tz: Timezone to use for end-of-day calculation (default: UTC)
            
        Returns:
            ISO datetime string in UTC (with Z suffix)
        """
        # Parse the date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        
        if tz is None:
            # Default to UTC behavior for backward compatibility
            if end_of_day:
                return f"{date_str}T23:59:59.000Z"
            return f"{date_str}T00:00:00.000Z"
        
        # Create datetime in the specified timezone
        if end_of_day:
            # End of day is 23:59:59 in local timezone
            local_dt = datetime.combine(date_obj, datetime.strptime("23:59:59", "%H:%M:%S").time())
        else:
            # Start of day is 00:00:00 in local timezone
            local_dt = datetime.combine(date_obj, datetime.min.time())
        
        # Localize to the specified timezone
        local_dt = local_dt.replace(tzinfo=tz)
        
        # Convert to UTC using the imported timezone.utc
        utc_dt = local_dt.astimezone(timezone.utc)
        
        # Format as ISO string with Z suffix
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    @classmethod
    def get_relative_date(cls, when: str, base_date: Optional[datetime] = None) -> Optional[str]:
        """Get a relative date for 'day', 'week', or 'month'.
        
        Args:
            when: One of 'day', 'week', 'month'
            base_date: Base date for calculations (default: now). If timezone-aware,
                      calculations are done in that timezone.
            
        Returns:
            ISO datetime string in UTC or None
        """
        # Extract timezone if base_date is timezone-aware
        tz = None
        if base_date is not None and base_date.tzinfo is not None:
            tz = base_date.tzinfo
        
        if base_date is None:
            base_date = datetime.utcnow()
        
        # Get the date in local timezone (or UTC if no timezone)
        today = base_date.date()
        
        if when == "day":
            # End of today
            date = today
        elif when == "week":
            # 7 days from now
            date = today + timedelta(days=7)
        elif when == "month":
            # 28 days from now
            date = today + timedelta(days=28)
        else:
            return None
        
        return cls.to_iso_datetime(date.isoformat(), end_of_day=True, tz=tz)
    
    @classmethod
    def parse_to_datetime(cls, when: str, base_date: Optional[datetime] = None) -> Optional[str]:
        """Parse a date string to ISO datetime format.
        
        This is a convenience method that parses the date and converts to datetime.
        
        Args:
            when: Natural language date or relative time ('day', 'week', 'month')
            base_date: Base date for calculations. If timezone-aware, the result
                      will be end-of-day in that timezone, converted to UTC.
            
        Returns:
            ISO datetime string in UTC or None
        """
        # Extract timezone if base_date is timezone-aware
        tz = None
        if base_date is not None and base_date.tzinfo is not None:
            tz = base_date.tzinfo
        
        # Handle relative keywords
        if when in ("day", "week", "month"):
            return cls.get_relative_date(when, base_date)
        
        # Parse as natural language date
        date_str = cls.parse(when, base_date)
        if date_str:
            return cls.to_iso_datetime(date_str, end_of_day=True, tz=tz)
        
        return None
