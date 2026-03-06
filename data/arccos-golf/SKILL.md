---
name: arccos-golf
description: Analyze Arccos Golf performance data including club distances, strokes gained metrics, scoring patterns, and round-by-round performance. Use when the user asks about golf statistics, club recommendations, performance trends, or wants detailed analysis from their Arccos Golf sensors.
---

# Arccos Golf Performance Analyzer

Comprehensive analysis tool for Arccos Golf performance data including club distances, strokes gained metrics, scoring patterns, putting analysis, and performance trends.

## Description

This skill provides detailed analysis of golf performance data from Arccos Golf sensors. It processes pre-collected Arccos data and generates insights into:

- **Strokes Gained Analysis**: Performance vs. PGA Tour averages across driving, approach, short game, and putting
- **Club Distance Tracking**: Average distances, shot counts, and longest shots for each club
- **Scoring Patterns**: Performance on different par values and score distribution analysis
- **Putting Performance**: Putts per round, GIR putting, and distance-based performance
- **Approach Shot Analysis**: Greens in regulation, miss patterns, and performance by distance/terrain
- **Round-by-Round Tracking**: Recent performance trends and course-specific analysis

**Key Features:**
- Comprehensive strokes gained breakdown with improvement recommendations
- Club distance analysis with filtering capabilities
- Scoring tendency analysis (birdie %, par %, bogey+ %)
- Putting performance metrics including three-putt frequency
- Approach shot miss pattern analysis
- Recent round performance tracking
- Multiple output formats (human-readable text and machine-readable JSON)

## System Access

**File System:**
- **READ**: Single Arccos data JSON file (path provided as command-line argument)

**Network Access:** None

**Subprocess/Shell:** None

## What It Does NOT Do

This skill is designed for **data analysis only** and explicitly does NOT:

- **No network access**: Does not connect to Arccos Golf services or any external APIs
- **No web scraping**: Does not perform browser automation or web requests to Arccos dashboard
- **No subprocess execution**: Does not run external commands or shell scripts
- **No file writes**: Does not create, modify, or delete any files (read-only operation)
- **No credential handling**: Does not store, read, or manage login credentials
- **No data collection**: Does not gather data from Arccos sensors or dashboard

**Data Collection**: Arccos does not offer a public API. Data collection requires separate browser automation tooling (not included in this skill). See the README for guidance on how to populate the data file.

## Resources

### Scripts

- `scripts/arccos_golf.py` - Main analysis script (Python 3.8+ required)

## Usage

### Basic Analysis (Full Report)

```bash
python3 scripts/arccos_golf.py /path/to/arccos-data.json
```

### Summary Statistics Only

```bash
python3 scripts/arccos_golf.py /path/to/arccos-data.json --summary
```

### Strokes Gained Analysis

```bash
python3 scripts/arccos_golf.py /path/to/arccos-data.json --strokes-gained
```

### Club Distance Analysis

```bash
# All clubs
python3 scripts/arccos_golf.py /path/to/arccos-data.json --clubs all

# Filter by club type
python3 scripts/arccos_golf.py /path/to/arccos-data.json --clubs iron
python3 scripts/arccos_golf.py /path/to/arccos-data.json --clubs wedge
python3 scripts/arccos_golf.py /path/to/arccos-data.json --clubs wood
```

### JSON Output

```bash
python3 scripts/arccos_golf.py /path/to/arccos-data.json --format json
```

### Recent Rounds Analysis

```bash
# Last 10 rounds
python3 scripts/arccos_golf.py /path/to/arccos-data.json --recent-rounds 10
```

## Expected Data Format

The script expects a JSON file with the following structure:

```json
{
  "golfer": "Player Name",
  "last_fetched": "2026-02-22",
  "total_shots": 7057,
  "total_rounds": 75,
  "longest_shot": 308,
  "strokes_gained": {
    "overall": -12.0,
    "driving": -3.3,
    "approach": -5.0,
    "short_game": -2.7,
    "putting": -1.1
  },
  "scoring": {
    "par3_avg": 3.8,
    "par4_avg": 5.4,
    "par5_avg": 6.3,
    "birdies_pct": 2.0,
    "pars_pct": 17.8,
    "bogeys_pct": 41.8,
    "double_plus_pct": 38.4
  },
  "clubs": [
    {
      "club": "Driver",
      "avg_distance": 234,
      "smart_distance": null,
      "longest": 281,
      "total_shots": 533
    }
  ],
  "recent_rounds": [
    {
      "date": "2026-02-01",
      "course": "Las Vegas GC",
      "score": 82,
      "over_par": 10
    }
  ]
}
```

## Example Output (Text Format)

```
🏌️ Arccos Golf Performance Report
========================================
Golfer: Paul Frederiksen
Last Updated: 2026-02-22
Total Shots Tracked: 7,057
Total Rounds: 75
Longest Drive: 308 yards

📊 STROKES GAINED ANALYSIS
------------------------------
Overall: -12.0
Driving: -3.3
Approach: -5.0
Short Game: -2.7
Putting: -1.1

⚠️ Areas for Improvement:
  • Approach: -5.0
  • Driving: -3.3
  • Short Game: -2.7
  • Putting: -1.1

🎯 Priority Areas:
  1. Approach
  2. Driving
  3. Short Game

🏌️ CLUB DISTANCES
--------------------
Driver: 234 yds avg (533 shots, longest: 281)
3 Wood: 204 yds avg (57 shots, longest: 320)
5 Wood: 182 yds avg (322 shots, longest: 206)
4 Iron: 149 yds avg (32 shots, longest: 171)

⛳ SCORING ANALYSIS
--------------------
Par 3 Average: 3.8
Par 4 Average: 5.4
Par 5 Average: 6.3

Score Distribution:
  Birdies+: 2.0%
  Pars: 17.8%
  Bogeys: 41.8%
  Double+: 38.4%

⛳ PUTTING ANALYSIS
--------------------
Putts per Round: 35.9
GIR Putts: 2.2
One-Putts: 15.8%
Three-Putts+: 15.1%

📈 RECENT ROUNDS
--------------------
2026-02-01: 82 (+10) at Las Vegas GC
2026-01-25: 93 (+21) at Stallion Mountain CC
2026-01-17: 95 (+23) at Coyote Springs GC
2026-01-10: 98 (+26) at Boulder Creek GC
```

## Analysis Categories

### Strokes Gained
- **Overall**: Total strokes gained/lost vs. PGA Tour average
- **Driving**: Performance from tee to landing position
- **Approach**: Performance from fairway/rough to green
- **Short Game**: Chipping and pitching performance
- **Putting**: Performance on the green

### Club Analysis
- Average carry distances for each club
- Shot count and consistency metrics
- Longest recorded shots
- Smart distance recommendations (when available)

### Scoring Patterns
- Performance on different par values (3, 4, 5)
- Score distribution (birdies, pars, bogeys, doubles+)
- Scoring tendencies and consistency metrics

### Putting Metrics
- Putts per round and per hole
- Performance on greens in regulation
- One-putt and three-putt+ percentages
- Distance-based putting performance

## Dependencies

- Python 3.8+
- Standard library only (json, sys, argparse, statistics, datetime, pathlib, typing)

## Installation

This skill can be installed via ClawHub:

```bash
clawhub install arccos-golf
```

Or manually by cloning the repository and placing it in your OpenClaw skills directory.

## Error Handling

The script provides specific error handling for:
- `FileNotFoundError`: When the specified JSON file doesn't exist
- `json.JSONDecodeError`: When the JSON file is malformed
- `KeyboardInterrupt`: Graceful handling of user interruption
- Graceful handling of missing or malformed data fields with appropriate defaults

## Output Formats

- **Text (default)**: Human-readable formatted report with emojis and clear sections
- **JSON**: Machine-readable structured data for further processing

## Privacy & Security

- All processing is done locally on the provided data file
- No external network connections are made
- No credentials or sensitive data are stored or transmitted
- Data is processed in memory only with no persistent storage
- Uses only Python standard library modules for security compliance
- No subprocess calls or shell execution

## Performance Insights

The analyzer provides actionable insights including:

1. **Improvement Priority**: Ranks weakest areas by strokes gained impact
2. **Club Recommendations**: Distance gaps and consistency analysis
3. **Scoring Patterns**: Identifies holes types where performance suffers
4. **Putting Analysis**: Short game improvement opportunities
5. **Round Trends**: Performance consistency and course-specific insights

## Golf Terminology

- **Strokes Gained**: Measures performance vs. statistical baseline (PGA Tour average)
- **GIR**: Greens in Regulation (reaching green in regulation strokes)
- **Smart Distance**: Arccos recommendation for club selection
- **Carry Distance**: Distance ball travels in air before landing
- **Up and Down**: Getting ball in hole within 2 strokes from off-green position