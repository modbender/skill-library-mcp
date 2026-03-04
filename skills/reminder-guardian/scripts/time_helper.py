#!/usr/bin/env python3
import sys
from datetime import datetime, timedelta

def get_time(offset_str=None):
    now = datetime.now()
    
    if not offset_str:
        return now.isoformat(timespec='seconds')
    
    try:
        # Parse formats like "+10m", "+2h", "+1d"
        if offset_str.startswith('+'):
            value = int(offset_str[1:-1])
            unit = offset_str[-1].lower()
            
            if unit == 'm':
                delta = timedelta(minutes=value)
            elif unit == 'h':
                delta = timedelta(hours=value)
            elif unit == 'd':
                delta = timedelta(days=value)
            else:
                return "Error: Invalid unit (use m, h, or d)"
            
            target_time = now + delta
            return target_time.isoformat(timespec='seconds')
        else:
            return "Error: Offset must start with '+' (e.g., +10m)"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    print(get_time(arg))
