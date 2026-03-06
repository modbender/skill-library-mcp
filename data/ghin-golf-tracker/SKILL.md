---
name: GHIN Golf Tracker
description: OpenClaw skill for analyzing GHIN (Golf Handicap and Information
  Network) golf statistics and handicap tracking.
---

# GHIN Golf Tracker

OpenClaw skill for analyzing GHIN (Golf Handicap and Information Network) golf statistics and handicap tracking.

## Description

This skill provides comprehensive analysis of golf statistics from GHIN data including handicap trends, scoring patterns, course performance, and historical breakdowns. The skill reads pre-collected GHIN data from a JSON file and computes detailed statistics in both human-readable and machine-readable formats.

**Key Features:**
- Current handicap index with trend analysis (improving/declining/stable)
- Lifetime totals including round counts and scoring extremes
- Best 5 differentials with course and date information
- Most played courses with round counts and average scores
- Year-by-year performance breakdown
- Scoring averages by par (3/4/5) when available
- Performance statistics (GIR%, fairways%, putts) when available
- Handicap range analysis with dates

## System Access

**File System:**
- **READ**: Single GHIN data JSON file (path provided as command-line argument)

**Network Access:** None

**Subprocess/Shell:** None

## What It Does NOT Do

This skill is designed for **data analysis only** and explicitly does NOT:

- **No network access**: Does not connect to GHIN.com or any external services
- **No web scraping**: Does not perform browser automation or web requests
- **No subprocess execution**: Does not run external commands or shell scripts
- **No file writes**: Does not create, modify, or delete any files
- **No credential handling**: Does not store, read, or manage login credentials
- **No data collection**: Does not gather GHIN data from external sources

**Data Collection**: GHIN does not offer a public API for score history. Data collection requires separate browser automation tooling (not included in this skill). See the README for guidance on how to populate the data file.

## Resources

### Scripts

- `scripts/ghin_stats.py` - Main analysis script (Python 3.8+ required)

## Usage

### Basic Analysis

```bash
python3 scripts/ghin_stats.py /path/to/ghin-data.json
```

### JSON Output

```bash
python3 scripts/ghin_stats.py /path/to/ghin-data.json --format json
```

### Expected Data Format

The script expects a JSON file with the following structure:

```json
{
  "handicap_index": 18.0,
  "lifetime_rounds": 83,
  "handicap_history": [
    {"date": "2026-02-02", "index": 18.0},
    {"date": "2026-01-15", "index": 17.8}
  ],
  "stats": {
    "par3_avg": 4.06,
    "par4_avg": 4.94,
    "par5_avg": 5.73,
    "gir_pct": 50,
    "fairways_pct": 65,
    "putts_avg": 31.2
  },
  "scores": [
    {
      "date": "2026-02-01",
      "score": "82A",
      "course": "Las Vegas Golf Club",
      "cr_slope": "68.0/117",
      "differential": 13.5
    }
  ]
}
```

### Example Output (Text Format)

```
GHIN Golf Statistics Report
==============================

Current Handicap: 18.0
Trend (last 5): ↗️  Improving

LIFETIME TOTALS
---------------
Total Rounds: 83
Best Score: 72
Worst Score: 95

BEST DIFFERENTIALS
-----------------
1. 8.2 - Pebble Beach Golf Links (2025-08-15)
2. 9.1 - Augusta National Golf Club (2025-09-22)
3. 10.4 - St. Andrews Old Course (2025-07-10)

MOST PLAYED COURSES
-------------------
Las Vegas Golf Club: 12 rounds (avg 84.2)
Phoenix Country Club: 8 rounds (avg 86.1)
Scottsdale National: 6 rounds (avg 82.9)

YEARLY BREAKDOWN
----------------
2026: 8 rounds (avg 83.4)
2025: 42 rounds (avg 84.7)
2024: 33 rounds (avg 87.2)
```

## Dependencies

- Python 3.8+
- Standard library only (json, sys, argparse, statistics, datetime, pathlib, collections, re)

## Installation

This skill can be installed via ClawHub:

```bash
clawhub install ghin-golf-tracker
```

Or manually by cloning the repository and placing it in your OpenClaw skills directory.

## Error Handling

The script provides specific error handling for:
- `FileNotFoundError`: When the specified JSON file doesn't exist
- `json.JSONDecodeError`: When the JSON file is malformed
- Graceful handling of missing or malformed data fields

## Output Formats

- **Text (default)**: Human-readable formatted report
- **JSON**: Machine-readable structured data for further processing

## Privacy & Security

- All processing is done locally on the provided data file
- No external network connections are made
- No credentials or sensitive data are stored or transmitted
- Data is processed in memory only with no persistent storage