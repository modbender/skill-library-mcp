#!/usr/bin/env python3
"""
cron_builder — Natural language to openclaw cron command.

Usage: python3 cron_builder.py "<natural language request>"
Output: JSON with success, parsed, command fields.
"""

import json
import os
import re
import shlex
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# --- Pattern dictionaries ---

TIME_PATTERNS = [
    (r'(\d{1,2})[.:](\d{2})\s*(am|pm)', 'ampm_min'),
    (r'(\d{1,2})\s*(am|pm)', 'ampm'),
    (r'(\d{1,2})[.:](\d{2})', '24h'),
]

NAMED_TIMES = {
    'noon': (12, 0),
    'midnight': (0, 0),
}

FREQUENCY_PATTERNS = [
    (r'every\s+(\d+)\s+hours?', 'every_n_hours'),
    (r'every\s+(\d+)\s+minutes?', 'every_n_minutes'),
    (r'(?:in\s+)?(\d+)\s*(?:min|minutes?|m)\b', 'in_minutes'),
    # Day-of-week patterns before generic weekly so "weekly on Mondays" -> monday
    (r'mondays?|every\s*monday', 'monday'),
    (r'tuesdays?|every\s*tuesday', 'tuesday'),
    (r'wednesdays?|every\s*wednesday', 'wednesday'),
    (r'thursdays?|every\s*thursday', 'thursday'),
    (r'fridays?|every\s*friday', 'friday'),
    (r'saturdays?|every\s*saturday', 'saturday'),
    (r'sundays?|every\s*sunday', 'sunday'),
    (r'weekdays?|mon[\s-]*fri|work\s*days?', 'weekdays'),
    (r'daily|every\s*day', 'daily'),
    (r'hourly|every\s*hour', 'hourly'),
    (r'weekly|once\s*a\s*week', 'weekly'),
    (r'monthly|once\s*a\s*month', 'monthly'),
]

DAY_MAP = {
    'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4,
    'friday': 5, 'saturday': 6, 'sunday': 0,
}

CHANNEL_PATTERNS = [
    (r'\bon\s*telegram\b|telegram', 'telegram'),
    (r'\bon\s*whatsapp\b|whatsapp', 'whatsapp'),
    (r'\bon\s*slack\b|slack', 'slack'),
    (r'\bon\s*discord\b|discord', 'discord'),
    (r'\bon\s*signal\b|signal', 'signal'),
]



def _parse_time(text):
    """Extract hour and minute from text. Returns (hour, minute) or None."""
    lower = text.lower()

    for name, (h, m) in NAMED_TIMES.items():
        if name in lower:
            return (h, m)

    for pattern, kind in TIME_PATTERNS:
        match = re.search(pattern, lower)
        if not match:
            continue
        groups = match.groups()
        if kind == 'ampm_min':
            hour, minute, meridian = int(groups[0]), int(groups[1]), groups[2]
            if meridian == 'pm' and hour != 12:
                hour += 12
            elif meridian == 'am' and hour == 12:
                hour = 0
            return (hour, minute)
        elif kind == 'ampm':
            hour, meridian = int(groups[0]), groups[1]
            if meridian == 'pm' and hour != 12:
                hour += 12
            elif meridian == 'am' and hour == 12:
                hour = 0
            return (hour, 0)
        elif kind == '24h':
            return (int(groups[0]), int(groups[1]))

    return None


def _parse_frequency(text):
    """Parse frequency from text. Returns (freq_type, value).

    freq_type is one of: daily, weekdays, hourly, weekly, monthly,
    every_n_hours, every_n_minutes, in_minutes, or a day name.
    value is the numeric value for every_n_* / in_minutes, or None.
    """
    lower = text.lower()
    for pattern, freq_type in FREQUENCY_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            groups = match.groups()
            if freq_type in ('every_n_hours', 'every_n_minutes', 'in_minutes'):
                return (freq_type, int(groups[0]))
            return (freq_type, None)
    return ('default', None)


def _parse_channel(text):
    """Extract channel from text. Falls back to CRON_DEFAULT_CHANNEL env or telegram."""
    lower = text.lower()
    for pattern, channel in CHANNEL_PATTERNS:
        if re.search(pattern, lower):
            return channel
    return os.environ.get('CRON_DEFAULT_CHANNEL', 'telegram')


def _parse_destination(text, channel):
    """Extract destination from text."""
    phone = re.search(r'\+?[\d\s\-()]{10,}', text)
    if phone:
        return phone.group().strip()
    handle = re.search(r'([#@]\w+)', text)
    if handle:
        return handle.group()
    defaults = {
        'telegram': '<TELEGRAM_CHAT_ID>',
        'whatsapp': '<WHATSAPP_PHONE>',
        'slack': '#general',
        'discord': '#general',
        'signal': '<SIGNAL_PHONE>',
    }
    return defaults.get(channel, '<DESTINATION>')


def _parse_message(text):
    """Extract the user's actual message by stripping scheduling noise."""
    msg = re.sub(
        r'^(create|set\s*up|schedule|add|remind\s*me\s*to?|send\s*me)\s+',
        '', text.strip(), flags=re.IGNORECASE,
    )
    # Strip "a/an" article left at the start after prefix removal
    msg = re.sub(r'^(an?\s+)', '', msg, flags=re.IGNORECASE)
    # Strip "in N minutes/min/m" for one-shot
    msg = re.sub(r'\s*\bin\s+\d+\s*(minutes?|min|m)\b', '', msg, flags=re.IGNORECASE)
    # Strip channel references
    msg = re.sub(r'\s+on\s+(telegram|whatsapp|slack|discord|signal)\b', '', msg, flags=re.IGNORECASE)
    # Strip time references
    msg = re.sub(r'\s+at\s+\d{1,2}[.:]\d{2}\s*(am|pm)?', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\s+at\s+\d{1,2}\s*(am|pm)', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\s+at\s+(noon|midnight)', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'^at\s+\d{1,2}[.:]\d{2}\s*(am|pm)?', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'^at\s+\d{1,2}\s*(am|pm)', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'^at\s+(noon|midnight)', '', msg, flags=re.IGNORECASE)
    # Strip frequency words
    msg = re.sub(r'\b(a\s+)?(daily|weekly|monthly|hourly|every\s+\d+\s+(hours?|minutes?|min|m))\s*', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\bevery\s*(day|hour)\b', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\b(mondays?|tuesdays?|wednesdays?|thursdays?|fridays?|saturdays?|sundays?)\b', '', msg, flags=re.IGNORECASE)
    msg = re.sub(r'\bweekdays?\b', '', msg, flags=re.IGNORECASE)
    # Clean up
    msg = msg.strip().strip('"\'').strip()
    return msg if msg else 'Reminder'


def _generate_name(text, freq_type):
    """Generate a short job name from the request."""
    # Strip common prefixes
    name = re.sub(
        r'^(create|set\s*up|schedule|add|remind\s*me\s*to?|send\s*me)\s+',
        '', text.strip(), flags=re.IGNORECASE,
    )
    # Strip "in N minutes/min/m" for one-shot
    name = re.sub(r'\s*\bin\s+\d+\s*(minutes?|min|m)\b', '', name, flags=re.IGNORECASE)
    # Strip channel / time suffixes
    name = re.sub(r'\s+on\s+(telegram|whatsapp|slack|discord|signal)\b', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+at\s+\d{1,2}[.:]\d{2}\s*(am|pm)?', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+at\s+\d{1,2}\s*(am|pm)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+at\s+(noon|midnight)', '', name, flags=re.IGNORECASE)
    # Strip frequency words for cleaner names
    name = re.sub(r'\b(a\s+)?(daily|weekly|monthly|hourly|every\s+\d+\s+hours?)\s*', '', name, flags=re.IGNORECASE)
    # Trim and capitalize
    name = name.strip().strip('"\'').strip()
    if name:
        name = name[0].upper() + name[1:]
    else:
        name = 'Scheduled Reminder'
    # Truncate
    if len(name) > 60:
        name = name[:57] + '...'
    return name


def _is_one_shot(freq_type):
    """Determine if the schedule is one-shot (not repeating)."""
    return freq_type in ('in_minutes', 'at_clock')


def parse(text):
    """Parse natural language into structured scheduling data.

    Returns dict with: time, frequency, channel, destination, message, name,
    one_shot, and the raw freq_type/freq_value.
    """
    time = _parse_time(text)
    freq_type, freq_value = _parse_frequency(text)

    # Resolve the 'default' freq_type (no explicit frequency keyword matched)
    if freq_type == 'default':
        if time is not None:
            freq_type = 'at_clock'
        else:
            freq_type = 'daily'

    channel = _parse_channel(text)
    destination = _parse_destination(text, channel)
    message = _parse_message(text)
    name = _generate_name(text, freq_type)
    one_shot = _is_one_shot(freq_type)

    errors = []
    # Default to 9am when no time specified for cron-based schedules
    if not one_shot and time is None and freq_type not in ('hourly', 'every_n_hours', 'every_n_minutes'):
        time = (9, 0)

    result = {
        'name': name,
        'time': {'hour': time[0], 'minute': time[1]} if time else None,
        'freq_type': freq_type,
        'freq_value': freq_value,
        'channel': channel,
        'destination': destination,
        'message': message,
        'one_shot': one_shot,
    }
    if errors:
        result['errors'] = errors
    return result


def build_command(parsed):
    """Build a complete openclaw cron add command from parsed data.

    Returns the command string. Raises ValueError on missing required fields.
    """
    parts = ['openclaw cron add']
    parts.append(f'--name {shlex.quote(parsed["name"])}')

    freq = parsed['freq_type']
    fval = parsed['freq_value']
    time = parsed.get('time')

    if freq == 'in_minutes':
        parts.append(f'--at "{fval}m"')
    elif freq == 'at_clock':
        # Build ISO timestamp for next occurrence of this clock time
        tz = ZoneInfo('America/New_York')
        now = datetime.now(tz)
        target = now.replace(
            hour=time['hour'], minute=time['minute'], second=0, microsecond=0,
        )
        if target <= now:
            target += timedelta(days=1)
        iso = target.isoformat()
        parts.append(f'--at {shlex.quote(iso)}')
    elif freq == 'every_n_hours':
        parts.append(f'--every "{fval}h"')
    elif freq == 'every_n_minutes':
        parts.append(f'--every "{fval}m"')
    elif freq == 'hourly':
        parts.append('--every "1h"')
    else:
        # Build cron expression
        h = time['hour'] if time else 9
        m = time['minute'] if time else 0
        if freq == 'daily':
            cron = f'{m} {h} * * *'
        elif freq == 'weekdays':
            cron = f'{m} {h} * * 1-5'
        elif freq == 'weekly':
            cron = f'{m} {h} * * 1'
        elif freq == 'monthly':
            cron = f'{m} {h} 1 * *'
        elif freq in DAY_MAP:
            dow = DAY_MAP[freq]
            cron = f'{m} {h} * * {dow}'
        else:
            cron = f'{m} {h} * * *'
        parts.append(f'--cron "{cron}" --tz "America/New_York"')

    parts.append('--session isolated')
    parts.append(f'--message {shlex.quote("Output exactly: " + parsed["message"])}')
    parts.append('--deliver')
    parts.append(f'--channel {shlex.quote(parsed["channel"])}')
    parts.append(f'--to {shlex.quote(parsed["destination"])}')

    if parsed['one_shot']:
        parts.append('--delete-after-run')

    return ' \\\n  '.join(parts)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            'success': False,
            'error': 'No request provided',
            'usage': 'python3 cron_builder.py "Create a daily reminder at 8am"',
        }))
        sys.exit(1)

    text = ' '.join(sys.argv[1:])
    parsed = parse(text)
    has_errors = 'errors' in parsed

    result = {
        'success': not has_errors,
        'parsed': parsed,
    }

    if not has_errors:
        result['command'] = build_command(parsed)
    else:
        result['command'] = None

    print(json.dumps(result, indent=2))
    sys.exit(1 if has_errors else 0)


if __name__ == '__main__':
    main()
