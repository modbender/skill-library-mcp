---
name: tper-hellobus
description: Get real-time and scheduled bus arrival times for TPER buses in Bologna and Ferrara, Italy. Use this skill whenever the user mentions TPER, bus stop codes (numeric like 4476), bus line numbers (like 11 or 27), or asks about bus arrivals in Bologna or Ferrara. Trigger for queries about when buses arrive, checking bus schedules, or real-time bus tracking.
---

# TPER Hellobus: Bologna & Ferrara Bus Times

This skill provides real-time and scheduled arrival information for TPER buses in Bologna and Ferrara by querying the official Hellobus API.

## When to Use This Skill

Use this skill when the user:
- Asks about bus arrivals at a specific stop in Bologna or Ferrara
- Mentions TPER, bus line numbers, or stop codes
- Wants to know when the next bus is coming
- Requests scheduled arrival times for a specific time
- Asks about real-time bus tracking

## How It Works

The skill queries the TPER Hellobus API with three parameters:

1. **fermata** (required): Numeric stop code (e.g., "4476", "8001")
2. **linea** (required): Bus line number (e.g., "11", "27", "101")
3. **oraHHMM** (optional): Time in HHmm format (e.g., "1830" for 6:30 PM)

**Critical Logic:**
- If `oraHHMM` is **omitted or empty**, the API returns **real-time GPS tracking** data
- If `oraHHMM` is **provided**, the API returns **scheduled arrivals** for that time

## API Endpoint

```
GET https://hellobuswsweb.tper.it/web-services/hellobus.asmx/QueryHellobus
```

### Parameters:
- `fermata`: Stop code (string, numeric)
- `linea`: Line number (string, numeric)
- `oraHHMM`: Time in HHmm format (string, optional - leave empty for real-time)

### Example API Calls:

**Real-time tracking (GPS):**
```
https://hellobuswsweb.tper.it/web-services/hellobus.asmx/QueryHellobus?fermata=4476&linea=11&oraHHMM=
```

**Scheduled times:**
```
https://hellobuswsweb.tper.it/web-services/hellobus.asmx/QueryHellobus?fermata=4476&linea=11&oraHHMM=1830
```

## Response Format

The API returns a response like:
```
TperHellobus: 11B DaSatellite 18:02 (Bus1634 CON PEDANA), 11B DaSatellite 18:18 (Bus5504 CON PEDANA)
```

Components:
- **11B**: Line number with variant
- **DaSatellite**: Real-time GPS data indicator (or scheduled time indicator)
- **18:02**: Arrival time
- **Bus1634**: Bus identifier
- **CON PEDANA**: Wheelchair accessible platform indicator

## Implementation Steps

### 1. Parse User Input

Extract from the user's query:
- **Stop code**: Numeric identifier (e.g., 4476)
- **Line number**: Numeric line (e.g., 11)
- **Time** (optional): If user mentions a specific time like "6:30 PM", "18:30", "at 3pm"

### 2. Convert Time Format

If the user provides a time:
- Parse the time from natural language (e.g., "6:30 PM", "18:30", "3pm")
- Convert to HHmm format (e.g., "1830", "1500")
- Use Europe/Rome timezone for any timezone-related conversions

**Time conversion examples:**
- "6:30 PM" → "1830"
- "3:00 PM" → "1500"
- "9:15 AM" → "0915"
- "18:30" → "1830"

### 3. Make API Request

Use the `bash_tool` with `curl` to call the API (web_fetch has URL restrictions):

```bash
# For real-time (no time specified):
curl "https://hellobuswsweb.tper.it/web-services/hellobus.asmx/QueryHellobus?fermata={stop_code}&linea={line_number}&oraHHMM="

# For scheduled time:
curl "https://hellobuswsweb.tper.it/web-services/hellobus.asmx/QueryHellobus?fermata={stop_code}&linea={line_number}&oraHHMM={time_hhmm}"
```

**Important:** Ensure proper URL encoding and handle the XML/text response from the API.

### 4. Parse and Format Response

The API response is plain text. Parse it and format as a bullet list:

**Input:** `TperHellobus: 11B DaSatellite 18:02 (Bus1634 CON PEDANA), 11B DaSatellite 18:18 (Bus5504 CON PEDANA)`

**Output format:**
```
Bus arrivals for line 11 at stop 4476:
• 11B DaSatellite 18:02 (Bus1634 CON PEDANA)
• 11B DaSatellite 18:18 (Bus5504 CON PEDANA)
```

Split on commas and present each arrival as a bullet point.

### 5. Error Handling

If the API returns an error or unexpected response:
- Report the error clearly to the user
- Include the original API response if helpful for debugging
- Suggest checking the stop code and line number

Common errors might include:
- Invalid stop code
- Line doesn't serve that stop
- No buses found for the specified time
- API connection issues

## User Interaction Examples

**Example 1: Real-time tracking**
```
User: "When is the next bus 11 arriving at stop 4476?"
Claude: [Queries API with oraHHMM empty]
Response: 
Bus arrivals for line 11 at stop 4476 (real-time):
• 11B DaSatellite 18:02 (Bus1634 CON PEDANA)
• 11B DaSatellite 18:18 (Bus5504 CON PEDANA)
```

**Example 2: Scheduled time**
```
User: "Check the schedule for bus 27 at stop 8001 for 6:30 PM"
Claude: [Queries API with oraHHMM=1830]
Response:
Bus arrivals for line 27 at stop 8001 at 18:30:
• 27 Orario 18:35 (Bus2045)
• 27 Orario 18:50 (Bus3012)
```

**Example 3: Error handling**
```
User: "Bus 99 at stop 1234"
Claude: [Queries API, receives error]
Response: "I couldn't find bus 99 at stop 1234. Please verify the stop code and line number are correct for the TPER network."
```

## Important Notes

- **Stop codes are numeric only** (not stop names)
- **Line numbers are numeric only** (e.g., "11", not "11B" - the API adds variants)
- **Empty oraHHMM = real-time GPS tracking**
- **Provided oraHHMM = scheduled arrivals**
- Always use Europe/Rome timezone for time conversions
- Format times as HHmm (24-hour format, no colon)

## Testing

Test cases to verify the skill works:
- Line 11, Stop 4476 (real-time)
- Line 11, Stop 4476, Time 18:30 (scheduled)
- Invalid stop code (error handling)
- Time format conversion (various user inputs)
