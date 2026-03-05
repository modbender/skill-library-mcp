---
name: baseball
description: >
  Fetch MLB game schedules, live game status, box scores, player search, and season
  statistics via the MLB Stats API. Use when the user asks about baseball games,
  scores, who is playing today, game results, live updates, pitching matchups,
  MLB schedule information, player lookups, or player stats.
metadata: {"openclaw":{"emoji":"⚾","requires":{"bins":["python3"]}}}
---

# Baseball — MLB Game Tracker

Fetch real-time MLB game schedules, live game status, box scores, player search, and season statistics via the MLB Stats API.

## Quick Start

```bash
# List today's games
python scripts/baseball.py games

# Live game status for the Phillies
python scripts/baseball.py live PHI

# Box score for a specific game
python scripts/baseball.py score 718415

# Box score for last Tuesday's Phillies game
python scripts/baseball.py score PHI --date 02/15/2026

# Search for a player
python scripts/baseball.py player Judge

# Search with team filter
python scripts/baseball.py player Wheeler --team PHI

# Player season stats by ID
python scripts/baseball.py stats 592450

# Player season stats by name
python scripts/baseball.py stats Aaron Judge --season 2025
```

## Usage

### List Teams

```bash
# Show all team abbreviations
python scripts/baseball.py teams
```

### List Games

```bash
# Today's games
python scripts/baseball.py games

# Games on a specific date
python scripts/baseball.py games --date 09/15/2025

# Next 7 days of games
python scripts/baseball.py games --days 7

# Upcoming week for a specific team
python scripts/baseball.py games --team PHI --days 7

# Filter by team
python scripts/baseball.py games --team PHI

# JSON output
python scripts/baseball.py games --format json
```

### Live Game Status

Show live count, runners, batter/pitcher matchup, and line score for an in-progress game.

```bash
# By team abbreviation (finds today's game)
python scripts/baseball.py live PHI

# By game PK
python scripts/baseball.py live 718415

# Game status from a specific date
python scripts/baseball.py live NYY --date 02/10/2026

# JSON output
python scripts/baseball.py live PHI --format json
```

### Box Score

Show the line score for any game (in-progress or final).

```bash
# By team abbreviation (today's game)
python scripts/baseball.py score PHI

# By game PK (works for any game, past or present)
python scripts/baseball.py score 718415

# By team abbreviation for a past date
python scripts/baseball.py score PHI --date 02/15/2026

# JSON output
python scripts/baseball.py score PHI --format json
```

### Search Players

```bash
# Search by last name
python scripts/baseball.py player Judge

# Search by full name
python scripts/baseball.py player Aaron Judge

# Filter by team
python scripts/baseball.py player Wheeler --team PHI

# JSON output
python scripts/baseball.py player Judge --format json
```

### Player Stats

```bash
# By player ID (from player search results)
python scripts/baseball.py stats 592450

# By player name (auto-resolves if unique match)
python scripts/baseball.py stats Aaron Judge

# Specific season
python scripts/baseball.py stats Aaron Judge --season 2024

# JSON output
python scripts/baseball.py stats 592450 --format json
```

## Output Format

### Text (Default)

**games:**

```
MLB Games - 09/15/2025
Away              Record     Home              Record     Time       Status               Game ID
-----------------------------------------------------------------------------------------------
PHI Phillies      85-62      NYM Mets          80-67      7:10 PM    In Progress          718415
BOS Red Sox       72-75      TB Rays           78-69      6:40 PM    Final (5-3)          718420
```

**live:**

```
PHI Phillies 3  @  NYM Mets 5
  Top 6th  |  1 out  |  2-1 count
  Bases: 1B [X]  2B [ ]  3B [X]
  AB: Kyle Schwarber  vs  P: Sean Manaea
  Last: Trea Turner singled on a line drive to left field.

       1  2  3  4  5  6  7  8  9    R  H  E
PHI    0  1  0  2  0  0  -  -  -    3  7  1
NYM    2  0  0  1  2  0  -  -  -    5  9  0
```

**score:**

```
Final: PHI Phillies 6  @  NYM Mets 4

       1  2  3  4  5  6  7  8  9    R  H  E
PHI    0  1  0  2  0  0  2  0  1    6  11  0
NYM    2  0  0  1  2  0  0  0  0    4   9  1
```

**player:**

```
Player Search: "Judge"
ID         Name                      Pos   Team                 #     B/T   Age
--------------------------------------------------------------------------------
592450     Aaron Judge               RF    NYY Yankees          99    R/R   33
```

**stats (batting):**

```
Aaron Judge  #99  RF  |  New York Yankees  |  R/R  |  Age 33
2025 Season Batting Statistics
  G     AB    R     H    2B   3B   HR   RBI   SB   BB    K    AVG    OBP    SLG    OPS
  152   541   137   179  30   2    53   114   12   124   160  .331   .457   .688   1.145
```

**stats (pitching):**

```
Zack Wheeler  #45  P  |  Philadelphia Phillies  |  L/R  |  Age 35
2025 Season Pitching Statistics
  G    GS   W    L    ERA    IP      H    R    ER   HR   SO   BB   SV   HLD  WHIP   K/9    BB/9
  30   30   14   6    2.85   198.1   155  68   63   18   210  42   0    0    0.99   9.55   1.91
```

### JSON

```json
{
  "date": "09/15/2025",
  "games": [
    {
      "game_pk": 718415,
      "status": "In Progress",
      "away_team": {"id": 143, "name": "Philadelphia Phillies", "abbreviation": "PHI"},
      "home_team": {"id": 121, "name": "New York Mets", "abbreviation": "NYM"},
      "away_record": "85-62",
      "home_record": "80-67",
      "away_score": 3,
      "home_score": 5,
      "venue": "Citi Field",
      "start_time": "2025-09-15T19:10:00-04:00"
    }
  ]
}
```

**player search (JSON):**

```json
{
  "query": "Judge",
  "players": [
    {
      "id": 592450,
      "full_name": "Aaron Judge",
      "position": "RF",
      "position_name": "Right Fielder",
      "primary_number": "99",
      "bats": "R",
      "throws": "R",
      "age": 33,
      "team": "New York Yankees",
      "team_abbreviation": "NYY",
      "active": true
    }
  ]
}
```

## Output Fields

- **game_pk** — Unique MLB game identifier
- **status** — Game state: Scheduled, Pre-Game, Warmup, In Progress, Final, Postponed, etc.
- **away_team / home_team** — Team id, full name, and abbreviation
- **away_record / home_record** — Win-loss record (schedule only)
- **away_score / home_score** — Current or final score
- **inning / inning_half** — Current inning number and half (Top/Bottom)
- **balls / strikes / outs** — Current count
- **runners** — Base occupancy: first, second, third (true/false)
- **matchup** — Current batter and pitcher names
- **last_play** — Description of the last completed play
- **line_score** — Inning-by-inning runs with R/H/E totals
- **venue** — Ballpark name
- **start_time** — Scheduled start in local time (ISO 8601)
- **id** — MLB player identifier (use with `stats` command)
- **full_name** — Player's full name
- **position** — Position abbreviation (RF, P, C, SS, etc.)
- **primary_number** — Jersey number
- **bats / throws** — Batting side and throwing hand (R, L, S)
- **batting** — Season batting stats (avg, obp, slg, ops, hr, rbi, etc.)
- **pitching** — Season pitching stats (era, wins, losses, whip, strikeouts, etc.)

## Team Abbreviations

Run `python scripts/baseball.py teams` to list all abbreviations. Partial team names also work (e.g., "Phillies", "Dodgers", "Red Sox").

ARI, ATL, BAL, BOS, CHC, CWS, CIN, CLE, COL, DET, HOU, KC, LAA, LAD, MIA, MIL, MIN, NYM, NYY, OAK, PHI, PIT, SD, SF, SEA, STL, TB, TEX, TOR, WSH

## Notes

- Data is sourced from the MLB Stats API. See [copyright](http://gdx.mlb.com/components/copyright.txt).
- The MLB Stats API is free and open — no API key or authentication is required. Please don't abuse it. Excessive requests (rapid polling, bulk scraping, etc.) may result in your IP being blocked. When checking live games, poll no more than once every 15 seconds.
- The `live` and `score` commands accept either a numeric game PK or a team abbreviation. When using an abbreviation, the script looks up today's schedule to find the team's game. Use `--date MM/DD/YYYY` to look up a game on a different date.
- The `games` text output includes a Game ID column. Use this ID with `score` or `live` to drill into a specific game — especially useful for doubleheaders where team abbreviation alone is ambiguous.
- The `player` command searches active MLB players. Use `stats <ID>` with the player ID from search results to view season statistics.
- The `stats` command accepts either a numeric player ID or a player name. If a name matches multiple players, you'll be prompted to use a specific ID.
- During the offseason, use `--season` to view stats from a previous year (e.g., `--season 2025`).
