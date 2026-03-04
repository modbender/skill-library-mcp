#!/usr/bin/env python3
"""
Calendar module for daily briefing.
Fetches today's events from macOS Calendar.app.
"""

import sys
import subprocess
import json
from datetime import datetime, timedelta


def run_icalbuddy():
    """Try to fetch calendar data using icalBuddy if available."""
    try:
        result = subprocess.run(
            ['icalBuddy', '-nc', '-nrd', '-ea', '-iep', 'title,datetime', '-ps', '| | - |', 'eventsToday'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None


def run_osascript():
    """Fetch calendar data using AppleScript as fallback."""
    script = '''
    tell application "Calendar"
        set today_start to current date
        set time of today_start to 0
        set today_end to today_start + (1 * days) - 1
        
        set event_list to {}
        repeat with cal in calendars
            repeat with evt in (every event of cal whose start date ≥ today_start and start date ≤ today_end)
                set evt_summary to summary of evt
                set evt_start to start date of evt
                set time_string to time string of evt_start
                set end of event_list to (time_string & " - " & evt_summary)
            end repeat
        end repeat
        
        return event_list as string
    end tell
    '''
    
    try:
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode == 0:
            return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return None


def parse_events(data):
    """Parse calendar data into structured events."""
    if not data:
        return []
    
    events = []
    lines = data.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to parse time and title
        # Format variations: "9:00 AM - Event Title" or "• 09:00-10:00 Event Title"
        parts = line.split(' - ', 1)
        if len(parts) == 2:
            time_str, title = parts
            events.append({
                'time': time_str.strip(),
                'title': title.strip()
            })
        else:
            # No clear time separator, treat whole line as title
            events.append({
                'time': '',
                'title': line.strip('• ').strip()
            })
    
    return events


def format_events(events):
    """Format calendar events for output."""
    if not events:
        return "   📭 No events scheduled today"
    
    output = []
    for evt in events[:10]:  # Limit to 10 events
        time_str = evt.get('time', '')
        title = evt.get('title', 'Unknown')
        
        if time_str:
            output.append(f"   {time_str} - {title}")
        else:
            output.append(f"   • {title}")
    
    return '\n'.join(output)


def get_calendar():
    """Get today's calendar events."""
    # Try icalBuddy first
    data = run_icalbuddy()
    
    # Fall back to AppleScript
    if not data:
        data = run_osascript()
    
    if data:
        events = parse_events(data)
        return format_events(events)
    
    return "   📭 Calendar data unavailable (check permissions)"


if __name__ == "__main__":
    print(get_calendar())
