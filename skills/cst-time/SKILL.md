---
name: cst-time
description: "Provides methods and tools for obtaining local host CST (China Standard Time). Invoke when user needs to get current CST time, convert time zones, or work with China Standard Time in scripts and applications."
---
# CST Time (China Standard Time)

## Overview

This skill provides comprehensive guidance for obtaining and working with China Standard Time (CST), which is UTC+8 and used throughout mainland China. It covers various methods for getting local CST time, time zone conversions, and integration with different programming languages and systems.

## Purpose

CST Time skill helps in:

- Getting current CST time from local system
- Converting between different time zones and CST
- Integrating CST time handling in applications
- Scheduling tasks based on CST
- Displaying and formatting CST time correctly
- Handling daylight saving time considerations (CST doesn't observe DST)

## CST Time Zone Information

**Time Zone Details:**

- **Name**: China Standard Time (CST)
- **UTC Offset**: UTC+8
- **Daylight Saving Time**: Not observed
- **Region**: Mainland China
- **IANA Time Zone ID**: Asia/Shanghai

**Important Notes:**

- CST is 8 hours ahead of Coordinated Universal Time (UTC)
- China does not observe daylight saving time
- CST is used consistently year-round
- Time zone ID for programming: Asia/Shanghai

## Getting CST Time

### 1. Using System Commands

#### Windows (PowerShell)

**Get current system time (assumed to be CST):**

```powershell
Get-Date
```

**Get CST time with explicit time zone:**

```powershell
[System.TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTime]::UtcNow, "China Standard Time")
```

**Format CST time:**

```powershell
Get-Date -Format "yyyy-MM-dd HH:mm:ss"
```

#### Linux/Unix (Bash)

**Get current system time:**

```bash
date
```

**Get CST time explicitly:**

```bash
TZ='Asia/Shanghai' date
```

**Format CST time:**

```bash
date +"%Y-%m-%d %H:%M:%S"
```

#### macOS (Bash)

**Get current system time:**

```bash
date
```

**Get CST time explicitly:**

```bash
TZ='Asia/Shanghai' date
```

### 2. Using Programming Languages

#### Python

**Get current CST time:**

```python
from datetime import datetime
import pytz

# Get current CST time
cst_tz = pytz.timezone('Asia/Shanghai')
cst_time = datetime.now(cst_tz)

print(f"Current CST time: {cst_time}")
print(f"Formatted: {cst_time.strftime('%Y-%m-%d %H:%M:%S')}")
```

**Convert UTC to CST:**

```python
from datetime import datetime
import pytz

# Get UTC time
utc_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

# Convert to CST
cst_time = utc_time.astimezone(pytz.timezone('Asia/Shanghai'))

print(f"UTC: {utc_time}")
print(f"CST: {cst_time}")
```

**Convert any timezone to CST:**

```python
from datetime import datetime
import pytz

# Example: Convert New York time to CST
ny_tz = pytz.timezone('America/New_York')
cst_tz = pytz.timezone('Asia/Shanghai')

ny_time = datetime.now(ny_tz)
cst_time = ny_time.astimezone(cst_tz)

print(f"New York: {ny_time}")
print(f"CST: {cst_time}")
```

#### JavaScript/Node.js

**Get current CST time:**

```javascript
// Using Intl API
const cstTime = new Date().toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    hour12: false
});
console.log('Current CST time:', cstTime);

// Using moment-timezone (recommended)
const moment = require('moment-timezone');
const cstTime = moment().tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss');
console.log('Current CST time:', cstTime);
```

**Convert UTC to CST:**

```javascript
const moment = require('moment-timezone');
const utcTime = moment().utc();
const cstTime = utcTime.tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss');
console.log('UTC:', utcTime.format());
console.log('CST:', cstTime);
```

#### Java

**Get current CST time:**

```java
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

// Get current CST time
ZonedDateTime cstTime = ZonedDateTime.now(ZoneId.of("Asia/Shanghai"));
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

System.out.println("Current CST time: " + cstTime.format(formatter));
```

**Convert UTC to CST:**

```java
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.Instant;

// Get UTC time and convert to CST
Instant utcTime = Instant.now();
ZonedDateTime cstTime = utcTime.atZone(ZoneId.of("Asia/Shanghai"));

System.out.println("UTC: " + utcTime);
System.out.println("CST: " + cstTime);
```

#### Go

**Get current CST time:**

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    // Get current CST time
    cstTime := time.Now().In(time.FixedZone("CST", int(8*3600)))
    fmt.Println("Current CST time:", cstTime.Format("2006-01-02 15:04:05"))
}
```

#### C#

**Get current CST time:**

```csharp
using System;

// Get current CST time
TimeZoneInfo cstZone = TimeZoneInfo.FindSystemTimeZoneById("China Standard Time");
DateTime cstTime = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, cstZone);

Console.WriteLine($"Current CST time: {cstTime:yyyy-MM-dd HH:mm:ss}");
```

### 3. Using Online APIs

**World Time API:**

```bash
curl "http://worldtimeapi.org/api/timezone/Asia/Shanghai"
```

**TimezoneDB API:**

```bash
curl "http://api.timezonedb.com/v1/get-time-zone?key=YOUR_API_KEY&by=zone&zone=Asia/Shanghai"
```

**Google Maps Time Zone API:**

```bash
curl "https://maps.googleapis.com/maps/api/timezone/json?location=39.9042,116.4074&timestamp=1331161200&key=YOUR_API_KEY"
```

## Time Zone Conversions

### 1. UTC to CST

**Formula:**

```
CST = UTC + 8 hours
```

**Python Example:**

```python
from datetime import datetime, timedelta

# UTC to CST
utc_time = datetime.utcnow()
cst_time = utc_time + timedelta(hours=8)

print(f"UTC: {utc_time}")
print(f"CST: {cst_time}")
```

### 2. CST to UTC

**Formula:**

```
UTC = CST - 8 hours
```

**Python Example:**

```python
from datetime import datetime, timedelta

# CST to UTC
cst_time = datetime.now()
utc_time = cst_time - timedelta(hours=8)

print(f"CST: {cst_time}")
print(f"UTC: {utc_time}")
```

### 3. Other Time Zones to CST

**Common conversions:**

| Time Zone        | UTC Offset | CST Offset | Conversion     |
| ---------------- | ---------- | ---------- | -------------- |
| EST (Eastern)    | UTC-5      | +13 hours  | EST + 13 = CST |
| PST (Pacific)    | UTC-8      | +16 hours  | PST + 16 = CST |
| GMT (Greenwich)  | UTC+0      | +8 hours   | GMT + 8 = CST  |
| JST (Japan)      | UTC+9      | -1 hour    | JST - 1 = CST  |
| AEST (Australia) | UTC+10     | -2 hours   | AEST - 2 = CST |

## Formatting CST Time

### Common Format Patterns

**ISO 8601 Format:**

```
2026-02-10T21:30:45+08:00
```

**Standard Format:**

```
2026-02-10 21:30:45
```

**Chinese Format:**

```
2026年2月10日 21:30:45
```

**Time Only:**

```
21:30:45
```

**Date Only:**

```
2026-02-10
```

### Programming Language Formatting

**Python:**

```python
from datetime import datetime

cst_time = datetime.now()
formats = {
    'ISO 8601': cst_time.isoformat(),
    'Standard': cst_time.strftime('%Y-%m-%d %H:%M:%S'),
    'Chinese': cst_time.strftime('%Y年%m月%d日 %H:%M:%S'),
    'Time only': cst_time.strftime('%H:%M:%S'),
    'Date only': cst_time.strftime('%Y-%m-%d')
}

for name, formatted in formats.items():
    print(f"{name}: {formatted}")
```

**JavaScript:**

```javascript
const moment = require('moment-timezone');
const cstTime = moment().tz('Asia/Shanghai');

const formats = {
    'ISO 8601': cstTime.format(),
    'Standard': cstTime.format('YYYY-MM-DD HH:mm:ss'),
    'Chinese': cstTime.format('YYYY年MM月DD日 HH:mm:ss'),
    'Time only': cstTime.format('HH:mm:ss'),
    'Date only': cstTime.format('YYYY-MM-DD')
};

for (const [name, formatted] of Object.entries(formats)) {
    console.log(`${name}: ${formatted}`);
}
```

## Best Practices

### 1. Time Zone Handling

**Recommendations:**

- Always store times in UTC and convert to CST for display
- Use IANA time zone IDs (e.g., Asia/Shanghai) instead of offsets
- Handle daylight saving time properly (CST doesn't observe DST)
- Test time zone conversions thoroughly
- Document time zone assumptions in code

### 2. Time Display

**Recommendations:**

- Display time in user's preferred format
- Include time zone information when displaying CST
- Use relative time (e.g., "2 hours ago") for recent events
- Consider cultural preferences for time formatting
- Provide options for 12-hour and 24-hour formats

### 3. Time Storage

**Recommendations:**

- Store timestamps in UTC in databases
- Include time zone information in data models
- Use appropriate data types for timestamps (e.g., TIMESTAMP)
- Consider time zone changes in historical data
- Document time zone handling in data schemas

### 4. Error Handling

**Recommendations:**

- Validate time inputs
- Handle invalid time zone IDs gracefully
- Provide clear error messages for time-related failures
- Test edge cases (leap years, time zone transitions)
- Log time-related errors for debugging

## Common Use Cases

### 1. Scheduling Tasks

**Example: Schedule a task at specific CST time:**

```python
from datetime import datetime, timedelta
import pytz

# Target CST time
target_cst = datetime(2026, 2, 10, 22, 0, 0, tzinfo=pytz.timezone('Asia/Shanghai'))

# Calculate time until task
now = datetime.now(pytz.timezone('Asia/Shanghai'))
time_until = target_cst - now

print(f"Task scheduled for: {target_cst}")
print(f"Time until task: {time_until}")
```

### 2. Logging with CST Time

**Example: Log events with CST timestamps:**

```python
import logging
from datetime import datetime
import pytz

# Configure logging with CST time
cst_tz = pytz.timezone('Asia/Shanghai')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Log event
logging.info("Event occurred at CST time")
```

### 3. Displaying CST Time in Web Applications

**Example: Display current CST time on a webpage:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>CST Time Display</title>
</head>
<body>
    <div id="cst-time">Loading...</div>
  
    <script>
        function updateCSTTime() {
            const options = {
                timeZone: 'Asia/Shanghai',
                hour12: false,
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            };
            const cstTime = new Date().toLocaleString('zh-CN', options);
            document.getElementById('cst-time').textContent = 'CST: ' + cstTime;
        }
    
        // Update every second
        setInterval(updateCSTTime, 1000);
        updateCSTTime();
    </script>
</body>
</html>
```

### 4. Converting User Input to CST

**Example: Convert user-provided time to CST:**

```python
from datetime import datetime
import pytz
from dateutil import parser

# User input time (could be any format)
user_input = "2026-02-10 14:30:00"

# Parse user input
user_time = parser.parse(user_input)

# Assume user time is in their local timezone
user_tz = pytz.timezone('America/New_York')
user_time = user_tz.localize(user_time)

# Convert to CST
cst_tz = pytz.timezone('Asia/Shanghai')
cst_time = user_time.astimezone(cst_tz)

print(f"User time: {user_time}")
print(f"CST time: {cst_time}")
```

## Troubleshooting

### Common Issues

| Issue                  | Possible Cause                  | Solution                                 |
| ---------------------- | ------------------------------- | ---------------------------------------- |
| Wrong time displayed   | System time zone not set to CST | Change system time zone to Asia/Shanghai |
| Time off by 1 hour     | Daylight saving time confusion  | Remember CST doesn't observe DST         |
| Time conversion errors | Incorrect time zone ID          | Use Asia/Shanghai instead of CST         |
| Time not updating      | Caching or stale data           | Clear cache and refresh                  |
| Time display issues    | Format string errors            | Verify format string syntax              |

### Debugging Tips

1. **Verify system time zone:**

   - Windows: Check Date & Time settings
   - Linux: Check /etc/timezone or timedatectl
   - macOS: Check System Preferences > Date & Time
2. **Test time zone conversions:**

   - Use known reference times
   - Verify conversions with multiple tools
   - Check for daylight saving time issues
3. **Monitor time-related logs:**

   - Look for time zone warnings
   - Check for conversion errors
   - Verify timestamp consistency

## Conclusion

Working with CST (China Standard Time) requires understanding of time zone handling, proper conversion methods, and careful attention to formatting and display. By following the guidance in this skill, you can:

- Accurately obtain and display CST time
- Convert between different time zones and CST
- Integrate CST time handling in applications
- Schedule tasks based on CST
- Handle time-related operations correctly and consistently

Remember that CST is UTC+8 year-round and does not observe daylight saving time, which simplifies time handling compared to many other time zones. Always test time-related functionality thoroughly and handle edge cases appropriately.
