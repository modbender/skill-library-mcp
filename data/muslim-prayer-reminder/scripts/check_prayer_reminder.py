#!/usr/bin/env python3
"""
Check if it's time to send a prayer reminder
Designed to run periodically (every 5-10 minutes via cron)
Returns exit code 1 if reminder needed, 0 if not
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def get_local_time(timezone_offset):
    """Get current local time with timezone offset"""
    utc_now = datetime.utcnow()
    return utc_now + timedelta(hours=timezone_offset)

def load_prayer_times(prayer_times_file):
    """Load today's prayer times from JSON file"""
    if not prayer_times_file.exists():
        print(f"❌ Prayer times file not found: {prayer_times_file}", file=sys.stderr)
        return None
    
    try:
        with open(prayer_times_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('prayers', {})
    except Exception as e:
        print(f"❌ Error reading prayer times: {e}", file=sys.stderr)
        return None

def parse_time(time_str, current_time):
    """Parse prayer time string (HH:MM) to datetime"""
    hour, minute = map(int, time_str.split(':'))
    return current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

def check_prayer_reminder(prayers, timezone_offset):
    """
    Check if we should send a prayer reminder
    
    Returns dict with reminder info or None
    """
    local_now = get_local_time(timezone_offset)
    
    # Only check the 5 main prayers (skip Sunrise)
    main_prayers = {
        "Fajr": prayers.get("Fajr"),
        "Dhuhr": prayers.get("Dhuhr"),
        "Asr": prayers.get("Asr"),
        "Maghrib": prayers.get("Maghrib"),
        "Isha": prayers.get("Isha")
    }
    
    for prayer_name, prayer_time_str in main_prayers.items():
        if not prayer_time_str:
            continue
            
        prayer_time = parse_time(prayer_time_str, local_now)
        
        # Calculate time difference in minutes
        diff_minutes = (prayer_time - local_now).total_seconds() / 60
        
        # 10 minutes before (9-11 min window to avoid missing it)
        if 9 <= diff_minutes <= 11:
            return {
                "type": "before",
                "prayer": prayer_name,
                "time": prayer_time_str,
                "minutes_until": int(diff_minutes),
                "message": f"🕌 Salat approaching: {prayer_name} in {int(diff_minutes)} minutes ({prayer_time_str})"
            }
        
        # During prayer time (0 to 2 minutes after start)
        elif -1 <= diff_minutes <= 2:
            return {
                "type": "now",
                "prayer": prayer_name,
                "time": prayer_time_str,
                "message": f"🕌 Salat First: {prayer_name} time is now ({prayer_time_str})"
            }
        
        # 5 minutes after start (4-6 min window for missed reminder)
        elif -6 <= diff_minutes <= -4:
            return {
                "type": "after",
                "prayer": prayer_name,
                "time": prayer_time_str,
                "minutes_ago": int(abs(diff_minutes)),
                "message": f"🕌 Salat reminder: {prayer_name} started {int(abs(diff_minutes))} minutes ago ({prayer_time_str})"
            }
    
    return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Check if it\'s time for prayer reminder')
    parser.add_argument('--prayer-times', required=True, help='Path to prayer_times.json file')
    parser.add_argument('--timezone', type=int, required=True, help='Timezone offset from UTC (e.g., 1 for GMT+1)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Load prayer times
    prayer_times_file = Path(args.prayer_times)
    prayers = load_prayer_times(prayer_times_file)
    
    if not prayers:
        sys.exit(2)  # Exit code 2 = error loading prayer times
    
    # Check for reminder
    reminder = check_prayer_reminder(prayers, args.timezone)
    
    if reminder:
        if args.json:
            print(json.dumps(reminder, ensure_ascii=False, indent=2))
        else:
            print(reminder['message'])
        sys.exit(1)  # Exit code 1 = reminder needed
    else:
        if not args.json:
            print("HEARTBEAT_OK")
        sys.exit(0)  # Exit code 0 = no reminder needed
