# TPER Hellobus Skill

This skill enables Claude to query real-time and scheduled bus arrival times for TPER buses in Bologna and Ferrara, Italy.

## Installation

To use this skill, you'll need to enable it in your Claude environment. The skill requires network access to be enabled to query the TPER Hellobus API.

## Important Requirements

### Network Access
This skill requires **network access to be enabled** in your Claude settings. Without it, the API calls will fail.

To enable network access:
1. Go to your Claude settings
2. Navigate to Network settings
3. Enable network access for the domains you want to allow

### Domain Whitelist
The skill needs access to:
- `hellobuswsweb.tper.it`

## How to Use

Once installed, you can ask Claude questions like:

**Real-time arrivals:**
- "When is the next bus 11 arriving at stop 4476?"
- "TPER line 27 stop 8001 real-time"
- "What's the next 11 at 4476?"

**Scheduled arrivals:**
- "Check bus 11 at stop 4476 for 6:30 PM"
- "Bus schedule for line 27 at stop 8001 at 3:15 PM"
- "Line 11 at 4476 tomorrow at 9am"

## Features

- ✅ Real-time GPS tracking (when no specific time is mentioned)
- ✅ Scheduled timetable lookups (when a specific time is provided)
- ✅ Automatic time format conversion (6:30 PM → 1830)
- ✅ Europe/Rome timezone handling
- ✅ Clear, formatted output with bullet points
- ✅ Error handling for invalid stops/lines

## API Details

The skill queries:
```
https://hellobuswsweb.tper.it/web-services/hellobus.asmx/QueryHellobus
```

With parameters:
- `fermata`: Stop code (numeric, e.g., "4476")
- `linea`: Line number (numeric, e.g., "11")
- `oraHHMM`: Optional time in HHmm format (empty = real-time, provided = scheduled)

## Testing

Test with these known working values:
- Stop: 4476
- Line: 11

Try queries like:
- "When is the next bus 11 at stop 4476?"
- "Bus 11 at 4476 for 18:30"

## Limitations

- Requires numeric stop codes (not stop names)
- Requires numeric line numbers
- Requires network access to be enabled
- API may have rate limits or availability constraints

## Troubleshooting

**If queries aren't working:**
1. Verify network access is enabled in Claude settings
2. Check that `hellobuswsweb.tper.it` is allowed
3. Verify the stop code and line number are valid for TPER
4. Try a simpler query format with just the line and stop numbers

**Common errors:**
- "Could not resolve host" → Network access is disabled
- "No buses found" → Invalid stop/line combination or no service at that time
- Time format issues → Ensure times are being converted to HHmm format
