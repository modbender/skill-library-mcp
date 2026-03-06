---
name: minimax-usage
description: Monitor MiniMax Coding Plan usage via API. Check remaining prompts,
  usage percentage, and reset time.
---

# minimax-usage

Monitor MiniMax Coding Plan usage via API. Check remaining prompts, usage percentage, and reset time.

## Description

This skill provides a command-line tool to query your MiniMax Coding Plan usage through the official API. It displays:
- Total available prompts (based on your subscription)
- Current usage across all time windows
- Remaining prompts
- Time until next reset
- Warning alerts when usage exceeds 80%

## Requirements

- Python 3.8+
- `requests` library
- Windows (for environment variable reading)
- MiniMax Coding Plan subscription
- MiniMax Coding Plan API Key

## Setup

### 1. Get API Key

1. Visit [MiniMax Console](https://platform.minimaxi.com/user-center/payment/coding-plan)
2. Create a new Coding Plan Key
3. Copy the key

### 2. Set Environment Variable

**Windows PowerShell (User-level, permanent):**
```powershell
[System.Environment]::SetEnvironmentVariable("MINIMAX_CODING_KEY", "your-api-key-here", "User")
```

**Windows PowerShell (Session-level, temporary):**
```powershell
$env:MINIMAX_CODING_KEY = "your-api-key-here"
```

**Linux/Mac:**
```bash
export MINIMAX_CODING_KEY="your-api-key-here"
```

### 3. Install Dependencies

```bash
pip install requests
```

## Usage

### Basic Check
```bash
python check_minimax.py
```

### With Notifications
```bash
python check_minimax.py --notify
```

### JSON Output
```bash
python check_minimax.py --json
```

## Output Example

```
=== MiniMax Coding Plan Usage ===
Model: MiniMax-M2
Total Available: 1,500 prompts
Used (all windows): 500 (33.3%)
Remaining: 1,000 prompts (66.7%)
Reset in: 2h 30m
Status: [OK]
```

## Integration

### Add to Heartbeat (OpenClaw)

In your `HEARTBEAT.md`:
```markdown
### MiniMax Usage Check (Hourly)
- Run: python scripts/check_minimax.py --notify
- Alert: Less than 20% remaining
```

### Cron Job (Linux/Mac)

```bash
# Add to crontab
0 * * * * /path/to/check_minimax.py --notify
```

## Technical Details

- API Endpoint: `https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains`
- Auth: Bearer token (Coding Plan API Key)
- **Important**: The API returns `usage_count` as REMAINING prompts, not used!
- Window Calculation: 15 x 5-hour windows (1500 total = 15 × 100 for Plus plan)
  - Total = 1500 prompts
  - Used = 1500 - usage_count
  - Current window = usage_count % 100

## Files

```
minimax-usage/
├── SKILL.md              # This file
├── README.md             # Setup guide
├── check_minimax.py      # Main script
└── requirements.txt       # Python dependencies
```

## License

MIT
