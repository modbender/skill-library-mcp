#!/usr/bin/env python3
"""
fetch_mlb.py — Fetch MLB scores, box scores, starting pitchers, and injury info.

Uses the free MLB Stats API (no API key required).
Outputs structured JSON to stdout for the OpenClaw agent to format.

Usage:
    python3 fetch_mlb.py --config                    # reads from OpenClaw config
    python3 fetch_mlb.py --team "Toronto Blue Jays"   # explicit team
    python3 fetch_mlb.py --team "New York Yankees" --timezone "America/New_York"
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Log status and errors to stderr so stdout stays clean for JSON output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("mlb-daily-scores")

try:
    import statsapi
except ImportError:
    log.error("MLB-StatsAPI not installed")
    print(
        json.dumps(
            {
                "error": "MLB-StatsAPI not installed. Run: pip3 install MLB-StatsAPI",
                "has_data": False,
            }
        )
    )
    sys.exit(1)

try:
    import requests
except ImportError:
    log.warning("requests library not installed — injury reports will be unavailable")
    requests = None

try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        ZoneInfo = None


VALID_TEAMS = {
    "arizona diamondbacks", "atlanta braves", "baltimore orioles",
    "boston red sox", "chicago cubs", "chicago white sox",
    "cincinnati reds", "cleveland guardians", "colorado rockies",
    "detroit tigers", "houston astros", "kansas city royals",
    "los angeles angels", "los angeles dodgers", "miami marlins",
    "milwaukee brewers", "minnesota twins", "new york mets",
    "new york yankees", "oakland athletics", "philadelphia phillies",
    "pittsburgh pirates", "san diego padres", "san francisco giants",
    "seattle mariners", "st. louis cardinals", "tampa bay rays",
    "texas rangers", "toronto blue jays", "washington nationals",
}

# Regex for validating IANA timezone strings (e.g., America/New_York)
import re
_TZ_PATTERN = re.compile(r"^[A-Za-z_]+(/[A-Za-z_]+){0,2}$")


def _load_openclaw_config() -> dict:
    """Load team/timezone from the OpenClaw config file."""
    if sys.platform == "win32":
        home = Path(os.environ.get("USERPROFILE", Path.home()))
    else:
        home = Path.home()
    config_path = home / ".openclaw" / "openclaw.json"

    if not config_path.exists():
        log.warning("OpenClaw config not found at %s", config_path)
        return {}

    try:
        log.info("Loading config from %s", config_path)
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        skill_cfg = (
            data.get("skills", {})
            .get("entries", {})
            .get("mlb-daily-scores", {})
            .get("config", {})
        )
        return skill_cfg
    except (json.JSONDecodeError, OSError) as e:
        log.error("Failed to load config: %s", e)
        return {}


def _validate_team(team: str) -> str:
    """Validate the team name against the known list of MLB teams."""
    if team.lower().strip() not in VALID_TEAMS:
        raise ValueError(
            f"Invalid team name: '{team}'. "
            "Must be a full official MLB team name (e.g., 'Toronto Blue Jays')."
        )
    return team.strip()


def _validate_timezone(tz: str | None) -> str | None:
    """Validate that a timezone string looks like a safe IANA identifier."""
    if tz is None:
        return None
    if not _TZ_PATTERN.match(tz) or len(tz) > 50:
        raise ValueError(
            f"Invalid timezone: '{tz}'. "
            "Must be an IANA timezone (e.g., 'America/New_York')."
        )
    return tz


# All game types we want to include:
#   S = Spring Training, R = Regular Season, F = Wild Card,
#   D = Division Series, L = League Championship Series,
#   W = World Series, E = Exhibition, A = All-Star
ALL_GAME_TYPES = "S,R,F,D,L,W,E,A"

_GAME_TYPE_LABELS = {
    "S": "Spring Training",
    "R": "Regular Season",
    "F": "Wild Card",
    "D": "Division Series",
    "L": "League Championship",
    "W": "World Series",
    "E": "Exhibition",
    "A": "All-Star",
}


def _schedule(date: str, team_id: int) -> list[dict]:
    """Fetch the schedule for a date/team including all game types.

    statsapi.schedule() does not support a game_type parameter, so we use
    the lower-level statsapi.get() and normalise the response into the same
    flat list-of-dicts format that statsapi.schedule() returns.
    """
    try:
        log.info("Fetching schedule for team %s on %s", team_id, date)
        raw = statsapi.get(
            "schedule",
            {
                "date": date,
                "teamId": team_id,
                "sportId": 1,
                "gameTypes": ALL_GAME_TYPES,
                "hydrate": "probablePitcher,linescore,broadcasts",
            },
        )
    except Exception as e:
        log.error("Failed to fetch schedule for team %s on %s: %s", team_id, date, e)
        return []

    games: list[dict] = []
    for d in raw.get("dates", []):
        for g in d.get("games", []):
            away = g.get("teams", {}).get("away", {})
            home = g.get("teams", {}).get("home", {})
            away_team = away.get("team", {})
            home_team = home.get("team", {})
            away_pitcher = away.get("probablePitcher", {})
            home_pitcher = home.get("probablePitcher", {})
            games.append(
                {
                    "game_id": g.get("gamePk"),
                    "game_type": g.get("gameType", "R"),
                    "game_datetime": g.get("gameDate", ""),
                    "status": g.get("status", {}).get("detailedState", ""),
                    "away_name": away_team.get("name", "?"),
                    "away_id": away_team.get("id"),
                    "away_score": away.get("score", 0),
                    "home_name": home_team.get("name", "?"),
                    "home_id": home_team.get("id"),
                    "home_score": home.get("score", 0),
                    "away_probable_pitcher": away_pitcher.get("fullName"),
                    "home_probable_pitcher": home_pitcher.get("fullName"),
                    "venue_name": g.get("venue", {}).get("name"),
                    "winning_pitcher": g.get("decisions", {}).get("winner", {}).get("fullName"),
                    "losing_pitcher": g.get("decisions", {}).get("loser", {}).get("fullName"),
                    "save_pitcher": g.get("decisions", {}).get("save", {}).get("fullName"),
                    "summary": g.get("description", ""),
                }
            )
    return games


def get_team_id(team_name: str) -> int | None:
    """Resolve a team name to its MLB team ID."""
    teams = statsapi.get("teams", {"sportId": 1})
    for team in teams.get("teams", []):
        full = team.get("name", "").lower()
        abbr = team.get("abbreviation", "").lower()
        short = team.get("teamName", "").lower()
        club = team.get("clubName", "").lower()
        needle = team_name.lower().strip()
        if needle in (full, abbr, short, club) or needle in full:
            return team["id"]
    return None


def get_dates(timezone: str | None) -> tuple[str, str]:
    """Return (yesterday, today) as 'YYYY-MM-DD' strings in the given timezone."""
    if timezone and ZoneInfo:
        try:
            tz = ZoneInfo(timezone)
            now = datetime.now(tz)
        except Exception:
            now = datetime.now()
    else:
        now = datetime.now()

    today = now.strftime("%Y-%m-%d")
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
    return yesterday, today


def fetch_yesterday_game(team_id: int, team_name: str, date: str) -> dict:
    """Fetch yesterday's game result, box score, and key stats."""
    result = {
        "played": False,
        "summary": None,
        "linescore": None,
        "boxscore": None,
        "key_stats": [],
        "winning_pitcher": None,
        "losing_pitcher": None,
        "save_pitcher": None,
    }

    sched = _schedule(date, team_id)
    if not sched:
        return result

    # Find the game for our team (prefer Final status)
    game = None
    for g in sched:
        status = g.get("status", "")
        if "Final" in status or "Game Over" in status or "Completed" in status:
            game = g
            break
    if not game:
        # Take the first game even if not final (e.g., postponed)
        game = sched[0]
        status = game.get("status", "")
        if "Final" not in status and "Game Over" not in status and "Completed" not in status:
            result["summary"] = f"Game status: {status}"
            if "Postponed" in status:
                result["summary"] = (
                    f"{game.get('away_name', '?')} @ {game.get('home_name', '?')} — Postponed"
                )
            return result

    game_pk = game["game_id"]
    result["played"] = True
    result["game_type"] = _GAME_TYPE_LABELS.get(
        game.get("game_type", "R"), game.get("game_type", "")
    )

    # Summary line
    away = game.get("away_name", "?")
    home = game.get("home_name", "?")
    away_score = game.get("away_score", 0)
    home_score = game.get("home_score", 0)
    result["summary"] = f"{away} {away_score}, {home} {home_score}"
    result["winning_pitcher"] = game.get("winning_pitcher", None)
    result["losing_pitcher"] = game.get("losing_pitcher", None)
    result["save_pitcher"] = game.get("save_pitcher", None)

    # Linescore
    try:
        log.info("Fetching linescore for game %s", game_pk)
        result["linescore"] = statsapi.linescore(game_pk)
    except Exception as e:
        log.error("Failed to fetch linescore for game %s: %s", game_pk, e)

    # Box score
    try:
        log.info("Fetching boxscore for game %s", game_pk)
        result["boxscore"] = statsapi.boxscore(game_pk)
    except Exception as e:
        log.error("Failed to fetch boxscore for game %s: %s", game_pk, e)

    # Key stats from box score data
    try:
        box_data = statsapi.boxscore_data(game_pk)
        for side in ["away", "home"]:
            batters = box_data.get(side, {}).get("batters", [])
            batting = box_data.get(side, {}).get("batting", [])
            for batter_id in batters:
                info = box_data.get(side, {}).get("battingInfo", {})
                # Try the player stats from the API
            # Pull notable stats from the text boxscore
            # (The boxscore text is easier to parse for notable performances)
        # Extract home runs from game data
        if "home_runs" in str(result.get("boxscore", "")):
            pass  # Already included in boxscore text
    except Exception:
        pass

    # Extract key performer info from the scoring plays / game data
    try:
        log.info("Fetching scoring plays for game %s", game_pk)
        scoring = statsapi.game_scoring_plays(game_pk)
        if scoring:
            result["scoring_plays"] = scoring
    except Exception as e:
        log.error("Failed to fetch scoring plays for game %s: %s", game_pk, e)

    # Get game highlights summary
    try:
        log.info("Fetching highlights for game %s", game_pk)
        highlights = statsapi.game_highlights(game_pk)
        if highlights:
            # Trim to first 500 chars to avoid bloat
            result["highlights_summary"] = highlights[:500]
    except Exception as e:
        log.error("Failed to fetch highlights for game %s: %s", game_pk, e)

    return result


def fetch_today_game(team_id: int, team_name: str, date: str, timezone: str | None) -> dict:
    """Fetch today's upcoming game info with probable pitchers."""
    result = {
        "scheduled": False,
        "summary": None,
        "game_time": None,
        "game_time_local": None,
        "venue": None,
        "away_team": None,
        "home_team": None,
        "away_pitcher": None,
        "home_pitcher": None,
        "is_home": None,
        "opponent": None,
        "broadcast": None,
    }

    sched = _schedule(date, team_id)
    if not sched:
        return result

    game = sched[0]
    result["scheduled"] = True
    result["game_type"] = _GAME_TYPE_LABELS.get(
        game.get("game_type", "R"), game.get("game_type", "")
    )

    away = game.get("away_name", "?")
    home = game.get("home_name", "?")
    result["away_team"] = away
    result["home_team"] = home

    # Determine if our team is home or away
    is_home = team_name.lower() in home.lower()
    result["is_home"] = is_home
    result["opponent"] = away if is_home else home

    # Game time
    game_dt = game.get("game_datetime", "")
    result["game_time"] = game_dt
    if game_dt and timezone and ZoneInfo:
        try:
            utc_dt = datetime.fromisoformat(game_dt.replace("Z", "+00:00"))
            local_dt = utc_dt.astimezone(ZoneInfo(timezone))
            result["game_time_local"] = local_dt.strftime("%I:%M %p %Z")
        except Exception:
            result["game_time_local"] = game_dt

    # Venue
    result["venue"] = game.get("venue_name", None)

    # Probable pitchers
    result["away_pitcher"] = game.get("away_probable_pitcher", None)
    result["home_pitcher"] = game.get("home_probable_pitcher", None)
    result["summary"] = game.get("summary", f"{away} @ {home}")

    # Broadcast info (if available)
    try:
        log.info("Fetching broadcast info for game %s", game["game_id"])
        game_data = statsapi.get("game", {"gamePk": game["game_id"]})
        broadcasts = game_data.get("gameData", {}).get("broadcasts", [])
        if broadcasts:
            bc_list = [b.get("name", "") for b in broadcasts if b.get("name")]
            result["broadcast"] = ", ".join(bc_list[:4])
    except Exception as e:
        log.error("Failed to fetch broadcast info: %s", e)

    return result


def fetch_probable_pitcher_stats(pitcher_name: str) -> dict | None:
    """Fetch season stats for a probable pitcher by name."""
    if not pitcher_name or pitcher_name in ("", "TBD"):
        return None

    try:
        log.info("Fetching stats for pitcher %s", pitcher_name)
        search = statsapi.lookup_player(pitcher_name)
        if not search:
            return None
        player_id = search[0]["id"]
        # Get current season stats
        stats = statsapi.player_stat_data(
            player_id, group="pitching", type="season"
        )
        if stats and stats.get("stats"):
            for s in stats["stats"]:
                if s.get("stats"):
                    st = s["stats"]
                    return {
                        "name": pitcher_name,
                        "wins": st.get("wins", 0),
                        "losses": st.get("losses", 0),
                        "era": st.get("era", "-"),
                        "strikeouts": st.get("strikeOuts", 0),
                        "innings": st.get("inningsPitched", "-"),
                        "whip": st.get("whip", "-"),
                    }
    except Exception as e:
        log.error("Failed to fetch pitcher stats for %s: %s", pitcher_name, e)
    return None


def fetch_injuries(team_id: int) -> list:
    """Fetch current injuries for the team using the MLB API injuries endpoint."""
    injuries = []
    if not requests:
        return injuries

    try:
        log.info("Fetching injuries for team %s", team_id)
        url = f"https://statsapi.mlb.com/api/v1/injuries?sportId=1&teamId={team_id}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            for entry in data.get("injuries", []):
                player = entry.get("playerName", entry.get("player", {}).get("fullName", "Unknown"))
                if isinstance(entry.get("player"), dict):
                    player = entry["player"].get("fullName", player)
                injuries.append(
                    {
                        "player": player,
                        "position": entry.get("player", {}).get("primaryPosition", {}).get("abbreviation", ""),
                        "injury": entry.get("description", entry.get("injuryDescription", "Undisclosed")),
                        "status": entry.get("status", ""),
                        "date": entry.get("date", ""),
                    }
                )
    except Exception as e:
        log.error("Failed to fetch injuries for team %s: %s", team_id, e)

    return injuries


def main():
    parser = argparse.ArgumentParser(description="Fetch MLB daily scores and info")
    parser.add_argument("--team", default=None, help="Full MLB team name (e.g., 'Toronto Blue Jays')")
    parser.add_argument("--timezone", default=None, help="IANA timezone (e.g., 'America/New_York')")
    parser.add_argument(
        "--config", action="store_true",
        help="Read team/timezone from ~/.openclaw/openclaw.json instead of CLI args"
    )
    args = parser.parse_args()

    # Resolve team/timezone from config file or CLI args
    team = args.team
    timezone = args.timezone

    if args.config:
        cfg = _load_openclaw_config()
        if not team:
            team = cfg.get("team")
        if not timezone:
            timezone = cfg.get("timezone")

    if not team:
        log.error("No team specified")
        print(
            json.dumps(
                {
                    "error": "No team specified. Use --team or --config with openclaw.json.",
                    "has_data": False,
                }
            )
        )
        sys.exit(1)

    # Validate inputs to prevent injection / garbage values
    try:
        team = _validate_team(team)
        timezone = _validate_timezone(timezone)
    except ValueError as e:
        log.error("Validation error: %s", e)
        print(json.dumps({"error": str(e), "has_data": False}))
        sys.exit(1)

    log.info("Starting MLB Daily Scores for team='%s', timezone='%s'", team, timezone)

    # Resolve team
    log.info("Resolving team ID")
    team_id = get_team_id(team)
    if team_id is None:
        log.error("Team '%s' not found", team)
        # Try to list available teams for a helpful error
        teams = statsapi.get("teams", {"sportId": 1})
        names = sorted([t["name"] for t in teams.get("teams", [])])
        print(
            json.dumps(
                {
                    "error": f"Team '{team}' not found.",
                    "available_teams": names,
                    "has_data": False,
                }
            )
        )
        sys.exit(1)

    yesterday, today = get_dates(timezone)
    log.info("Dates: yesterday=%s, today=%s", yesterday, today)

    # Fetch all data
    log.info("Fetching yesterday's game")
    yesterday_data = fetch_yesterday_game(team_id, team, yesterday)
    log.info("Fetching today's game")
    today_data = fetch_today_game(team_id, team, today, timezone)

    # Fetch pitcher stats for today's probable pitchers
    pitcher_stats = {}
    for key in ("away_pitcher", "home_pitcher"):
        name = today_data.get(key)
        if name:
            stats = fetch_probable_pitcher_stats(name)
            if stats:
                pitcher_stats[name] = stats

    # Fetch injuries
    log.info("Fetching injury report")
    injuries = fetch_injuries(team_id)

    # Determine if we have any data worth reporting
    has_data = yesterday_data["played"] or today_data["scheduled"]

    output = {
        "has_data": has_data,
        "team": team,
        "team_id": team_id,
        "date_yesterday": yesterday,
        "date_today": today,
        "timezone": timezone,
        "yesterday": yesterday_data,
        "today": today_data,
        "pitcher_stats": pitcher_stats,
        "injuries": injuries,
    }

    log.info("Done — has_data=%s", has_data)
    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    main()
