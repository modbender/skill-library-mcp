#!/usr/bin/env python3
"""
Query parser for natural language filter expressions.

Converts user queries like "last_seen > 30 days" or "os_version = 14.%"
into client-side filter functions that operate on device data.
"""

import re
from typing import Callable, Any, List, Dict
from datetime import datetime, timedelta, timezone

class QueryFilter:
    """Represents a single filter condition."""
    
    def __init__(self, field: str, operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value
    
    def matches(self, device: Dict[str, Any]) -> bool:
        """Check if device matches this filter."""
        if self.field not in device:
            return False
        
        device_value = device[self.field]
        
        if self.operator == "=":
            return device_value == self.value
        elif self.operator == "!=":
            return device_value != self.value
        elif self.operator == ">":
            return self._compare(device_value, self.value, lambda a, b: a > b)
        elif self.operator == "<":
            return self._compare(device_value, self.value, lambda a, b: a < b)
        elif self.operator == ">=":
            return self._compare(device_value, self.value, lambda a, b: a >= b)
        elif self.operator == "<=":
            return self._compare(device_value, self.value, lambda a, b: a <= b)
        elif self.operator == "contains":
            return str(self.value).lower() in str(device_value).lower()
        elif self.operator == "like":
            # Simple glob pattern matching
            pattern = self.value.replace("%", ".*").replace("?", ".")
            return re.match(f"^{pattern}$", str(device_value)) is not None
        else:
            return False
    
    def _compare(self, val1: Any, val2: Any, op: Callable) -> bool:
        """Numeric or date comparison."""
        try:
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                return op(val1, val2)
            # Try numeric conversion
            return op(float(val1), float(val2))
        except (ValueError, TypeError):
            return False
    
    def __repr__(self):
        return f"QueryFilter({self.field} {self.operator} {self.value})"


class QueryParser:
    """Parse natural language query expressions."""
    
    # Time unit multipliers (in days)
    TIME_UNITS = {
        "day": 1,
        "days": 1,
        "week": 7,
        "weeks": 7,
        "month": 30,
        "months": 30,
        "year": 365,
        "years": 365,
    }
    
    def parse(self, expression: str) -> List[QueryFilter]:
        """Parse a filter expression into QueryFilter objects.
        
        Examples:
            "os_version = 14.5" → [QueryFilter('os_version', '=', '14.5')]
            "last_seen > 30 days" → [QueryFilter('last_seen', '>', <30_days_ago>)]
            "platform = macOS AND status = active" → Multiple filters
        """
        filters = []
        
        # Split on AND/OR (for now, treat as AND)
        conditions = re.split(r'\s+(AND|OR)\s+', expression, flags=re.IGNORECASE)
        
        for i, condition in enumerate(conditions):
            if condition.upper() in ('AND', 'OR'):
                continue
            
            condition = condition.strip()
            if not condition:
                continue
            
            filter_obj = self._parse_condition(condition)
            if filter_obj:
                filters.append(filter_obj)
        
        return filters
    
    def _parse_condition(self, condition: str) -> QueryFilter:
        """Parse a single condition: field operator value"""
        
        # Try various operator patterns
        patterns = [
            (r"(\w+)\s*(>=|<=|!=|=|>|<)\s*(.+)", self._parse_comparison),
            (r"(\w+)\s+contains\s+(.+)", lambda m: QueryFilter(m.group(1), "contains", m.group(2))),
            (r"(\w+)\s+like\s+(.+)", lambda m: QueryFilter(m.group(1), "like", m.group(2))),
        ]
        
        for pattern, handler in patterns:
            match = re.match(pattern, condition, re.IGNORECASE)
            if match:
                if handler == self._parse_comparison:
                    return handler(match)
                else:
                    return handler(match)
        
        return None
    
    def _parse_comparison(self, match) -> QueryFilter:
        """Parse comparison with potential unit conversion."""
        field = match.group(1)
        operator = match.group(2)
        value_str = match.group(3).strip()
        
        # Try to parse time-based values
        value = self._parse_value(value_str, field)
        
        return QueryFilter(field, operator, value)
    
    def _parse_value(self, value_str: str, field: str) -> Any:
        """Convert value string to appropriate type.
        
        Handles:
        - "30 days" → datetime 30 days ago
        - "14.5" → "14.5" (string)
        - "true/false" → boolean
        """
        value_str = value_str.strip().lower()
        
        # Check for time-based values (for last_seen, enrolled_date, etc.)
        if "day" in value_str or "week" in value_str or "month" in value_str or "year" in value_str:
            return self._parse_time_offset(value_str)
        
        # Boolean
        if value_str in ('true', 'false'):
            return value_str == 'true'
        
        # Try numeric
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
        
        # Return as string
        return value_str
    
    def _parse_time_offset(self, time_str: str) -> datetime:
        """Parse 'N days/weeks/months/years' into a datetime N units ago.
        
        Example: "30 days" → datetime 30 days in the past
        """
        match = re.match(r"(\d+)\s+(\w+)", time_str)
        if not match:
            return None
        
        count = int(match.group(1))
        unit = match.group(2).lower()
        
        if unit not in self.TIME_UNITS:
            return None
        
        days = count * self.TIME_UNITS[unit]
        return datetime.now(timezone.utc) - timedelta(days=days)


class DeviceFilter:
    """Apply filters to a list of devices."""
    
    def __init__(self, filters: List[QueryFilter]):
        self.filters = filters
    
    def filter_devices(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return devices matching all filters."""
        result = []
        for device in devices:
            if all(f.matches(device) for f in self.filters):
                result.append(device)
        return result
    
    def group_by(self, field: str, devices: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group devices by a field value."""
        groups = {}
        for device in devices:
            key = device.get(field, "unknown")
            if key not in groups:
                groups[key] = []
            groups[key].append(device)
        return groups
    
    def count_by(self, field: str, devices: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count devices grouped by a field."""
        counts = {}
        for device in devices:
            key = device.get(field, "unknown")
            counts[key] = counts.get(key, 0) + 1
        return counts


# Example usage
if __name__ == "__main__":
    parser = QueryParser()
    
    # Test parsing
    tests = [
        "os_version = 14.5",
        "last_seen > 30 days",
        "platform = macOS AND status = active",
        "device_name contains MacBook",
    ]
    
    for test in tests:
        print(f"\nParsing: {test}")
        filters = parser.parse(test)
        for f in filters:
            print(f"  → {f}")
    
    # Test filtering
    print("\n\nTesting with sample devices:")
    devices = [
        {"device_name": "MacBook-1", "os_version": "14.5", "status": "active"},
        {"device_name": "iPhone-1", "os_version": "17.2", "status": "active"},
        {"device_name": "MacBook-2", "os_version": "13.6", "status": "inactive"},
    ]
    
    device_filter = DeviceFilter(parser.parse("device_name contains MacBook"))
    result = device_filter.filter_devices(devices)
    print(f"Devices matching 'device_name contains MacBook': {len(result)}")
    for d in result:
        print(f"  • {d['device_name']}")
