---
name: leetify
description: Get CS2 player statistics, match analysis, and gameplay insights from Leetify API. Supports player comparison and season stats. Use for stat queries and demo analysis.
metadata:
  {
    "openclaw":
      {
        "requires":
          {
            "env": ["LEETIFY_API_KEY"],
            "bins": ["python3", "bash", "bunzip2", "gunzip"],
            "pip": ["requests", "demoparser2"],
          },
      },
  }
---

# Leetify API Skill

Access CS2 statistics and match data from the Leetify platform.

## Quick Stats

Use these commands for general statistics, ranks, and recent performance.

### Show Statistics
```bash
bash scripts/get_stats_by_username.sh USERNAME
```
Displays averages, recent match performance, and ranks.

### Get Match Data
```bash
bash scripts/get_match_details.sh USERNAME [INDEX]
```
Fetches raw JSON statistics for a specific match. When presenting this data, provide a structured report covering shooting, utility usage, and performance metrics.

### Compare Players
```bash
bash scripts/compare_by_username.sh USERNAME1 USERNAME2
```
Compares two players based on their Leetify profiles.

### Season Stats
```bash
python3 scripts/season_stats.py
```
Provides a summary table for players tracked in the local database.

## Demo Analysis

Use this workflow for detailed tactical reviews and round-by-round breakdowns.

### 1. Identify the Player
- Resolve Steam ID: `python3 scripts/steam_ids.py get --username USERNAME`
- Match the player in the match log using the resolved Steam ID.

### 2. Generate Match Log
```bash
python3 scripts/analyze_last_demo.py --username USERNAME [--match-index N] [--no-cache]
```
- Downloads and parses the demo file (requires significant memory).
- Generates a text log containing scoreboard and round timeline.

### 3. Analyze Performance
Review the generated log to assess:
- Shooting accuracy and trade efficiency.
- Utility effectiveness (flash duration, grenade damage).
- Role performance (entry, anchor, support).
- Tactical highlights and mistakes.

Actionable recommendations can be provided based on the observed patterns. Guides or tutorials for specific map positions may be referenced if performance in those areas was suboptimal.

## Data Management

### Manage Steam IDs
```bash
# Save a player profile
python3 scripts/steam_ids.py save --username "username" --steam-id "7656119..." --name "Name"

# List all tracked players
python3 scripts/steam_ids.py list
```

## Configuration

The skill requires the `LEETIFY_API_KEY` environment variable.
API documentation is available at: https://api-public-docs.cs-prod.leetify.com/
