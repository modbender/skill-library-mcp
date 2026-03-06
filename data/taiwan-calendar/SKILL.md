---
name: taiwan-calendar
description: Taiwan calendar query for accurate working day/holiday information. Use when user asks about Taiwan dates, working days, holidays, make-up workdays, or needs date calculations. Solves Claude's knowledge cutoff issues with Taiwan's administrative calendar.
allowed-tools: Bash
metadata:
  short-description: Query Taiwan government calendar for working days and holidays
  version: "0.0.1"
license: MIT
---

# Taiwan Calendar Skill

Provides accurate Taiwan working day and holiday information by querying government open data APIs in real-time.

## Why This Skill Exists

Claude Code frequently makes errors with Taiwan date-related queries due to knowledge cutoff:

- Gets weekdays wrong (e.g., saying Tuesday when it's Wednesday)
- Doesn't know current year's national holidays
- Unaware of make-up workdays (補班日)

This skill queries Taiwan's government administrative calendar API to provide accurate, up-to-date information.

---

## When to Use

**Trigger actively when user asks about:**

- **Date queries**: "今天是幾號?", "What's today's date?", "現在台灣幾點?"
- **Working day queries**: "今天是工作日嗎?", "Is tomorrow a working day?", "下週一要上班嗎?"
- **Holiday queries**: "1/1 是假日嗎?", "國慶日是哪天?", "下一個連假什麼時候?"
- **Date calculations**: "5 個工作日後是哪天?", "這個月有幾個工作日?", "deadline 是五個工作天"
- **Make-up workdays**: "有沒有補班?", "這週六要上班嗎?"

**Also use for:**

- Schedule/timeline planning that requires working day awareness
- Deadline calculations mentioning "工作日/工作天"
- Any Taiwan calendar-related questions

---

## Commands

All commands use: `uv run --managed-python scripts/taiwan_calendar.py <command>`

### Basic Queries

#### `today` - Today's date and status

```bash
uv run --managed-python scripts/taiwan_calendar.py today
```

**Output example:**

```
2025-01-06 (週一) 是工作日。
```

#### `check <date>` - Check specific date

```bash
uv run --managed-python scripts/taiwan_calendar.py check 2025-01-01
uv run --managed-python scripts/taiwan_calendar.py check 01/01
```

**Output example:**

```
2025-01-01 (週三) 是非工作日 - 元旦。
```

**Date formats supported:**

- `YYYY-MM-DD` (e.g., 2025-01-01)
- `YYYY/MM/DD` (e.g., 2025/01/01)
- `MM/DD` (assumes current year, e.g., 01/01)

### Range Queries

#### `range <start> <end>` - Count working days in range

```bash
uv run --managed-python scripts/taiwan_calendar.py range 2025-01-01 2025-01-31
```

**Output example:**

```
2025-01-01 到 2025-01-31 共有 23 個工作日。

期間假日：
  - 2025-01-01 (週三) - 元旦
  - 2025-01-29 (週三) - 春節
```

### Advanced Calculations

#### `add-days [date] <n>` - Calculate N working days later

```bash
# From today
uv run --managed-python scripts/taiwan_calendar.py add-days 5

# From specific date
uv run --managed-python scripts/taiwan_calendar.py add-days 2025-01-06 5
```

**Output example:**

```
從 2025-01-06 算起 5 個工作日後是 2025-01-13 (週一)。
```

#### `next-working [date]` - Find next working day

```bash
# From today
uv run --managed-python scripts/taiwan_calendar.py next-working

# From specific date
uv run --managed-python scripts/taiwan_calendar.py next-working 2025-01-03
```

**Output example:**

```
下一個工作日是 2025-01-06 (週一)。
```

#### `next-holiday [date]` - Find next holiday

```bash
# From today
uv run --managed-python scripts/taiwan_calendar.py next-holiday

# From specific date
uv run --managed-python scripts/taiwan_calendar.py next-holiday 2025-01-06
```

**Output example:**

```
下一個假日是 2025-01-29 (週三) - 春節。
```

---

## Usage Examples

### Example 1: Simple Date Query

```
User: "今天是幾號？"

Response:
[Run: uv run --managed-python scripts/taiwan_calendar.py today]
Output: 2025-01-06 (週一) 是工作日。

"今天是 2025 年 1 月 6 日（週一），是工作日。"
```

### Example 2: Holiday Check

```
User: "元旦是放假嗎？"

Response:
[Run: uv run --managed-python scripts/taiwan_calendar.py check 01/01]
Output: 2025-01-01 (週三) 是非工作日 - 元旦。

"是的，元旦（1/1）是國定假日。"
```

### Example 3: Working Day Calculation

```
User: "報告要 5 個工作天內交，今天開始算那是哪天？"

Response:
[Run: uv run --managed-python scripts/taiwan_calendar.py add-days 5]
Output: 從 2025-01-06 算起 5 個工作日後是 2025-01-13 (週一)。

"從今天算起 5 個工作日後是 1 月 13 日（週一）。"
```

### Example 4: This Month's Working Days

```
User: "這個月有幾個工作日？"

Response:
[Run: uv run --managed-python scripts/taiwan_calendar.py range 2025-01-01 2025-01-31]
Output: 2025-01-01 到 2025-01-31 共有 23 個工作日。

期間假日：
  - 2025-01-01 (週三) - 元旦

"這個月（1月）有 23 個工作日，期間有元旦（1/1）放假。"
```

### Example 5: Next Holiday

```
User: "下一個連假是什麼時候？"

Response:
[Run: uv run --managed-python scripts/taiwan_calendar.py next-holiday]
Output: 下一個假日是 2025-01-29 (週三) - 春節。

"下一個假日是春節，從 1 月 29 日（週三）開始。"
```

---

## Technical Details

### Data Source

- **Primary**: Taiwan government open data platform (data.gov.tw)
- **Fallback**: New Taipei City open data

### Caching

- **Location**: System temp directory (cross-platform via `tempfile.gettempdir()`)
- **File**: `taiwan-calendar-cache.json`
- **Expiry**: 1 hour
- **Behavior**: Automatically refreshes when expired

### Timezone

- All operations use Taiwan timezone (Asia/Taipei, UTC+8)
- Current time queries reflect Taiwan local time

### Error Handling

- Clear error messages if API unavailable
- Automatic fallback to secondary API source
- Uses expired cache with warning if network unavailable

---

## Important Notes

### When to Use This Skill

✅ **DO use for:**

- Any Taiwan date/calendar queries
- Working day calculations
- Holiday information
- Date arithmetic involving working days

❌ **DON'T use for:**

- Non-Taiwan regions/calendars
- Lunar calendar queries (農曆)
- 24 solar terms (二十四節氣)
- Historical dates (use for current/future dates)

### Natural Language Output

The script outputs Chinese (Traditional) responses. Use these directly when responding to users, or translate if needed.

### Command Execution

Always use the full command with `uv run --managed-python`:

```bash
uv run --managed-python scripts/taiwan_calendar.py <command> [args]
```

**NEVER** use:

- `python scripts/taiwan_calendar.py` ❌
- `cd scripts && uv run taiwan_calendar.py` ❌

The script path is relative to the skill directory.

---

## Troubleshooting

### "Failed to fetch calendar data"

**Cause**: All API sources unavailable

**Solution**:

1. Check network connection
2. Verify government API status
3. Script will use expired cache if available (with warning)

### "Invalid date format"

**Cause**: Unrecognized date format

**Solution**: Use supported formats:

- `YYYY-MM-DD` (e.g., 2025-01-06)
- `YYYY/MM/DD` (e.g., 2025/01/06)
- `MM/DD` (e.g., 01/06)

### "Unable to parse date"

**Cause**: Ambiguous date input

**Solution**: Be explicit with year for dates far from today

---

## Progressive Disclosure

This is the main skill file. All essential information is included here for immediate use.

For implementation details, see: `scripts/taiwan_calendar.py`
