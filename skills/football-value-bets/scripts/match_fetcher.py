#!/usr/bin/env python3
"""
Fetch football match data from football-data.org API.

Modes:
  fixtures   -- Today's and tomorrow's matches for configured competitions
  standings  -- League tables with form data
  h2h        -- Head-to-head record for a specific match
  full       -- Combined analysis package (fixtures + standings + h2h for each match)

Output: structured JSON to stdout.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import requests
except ImportError:
    print(json.dumps({
        "status": "error",
        "code": "missing_dependency",
        "message": "requests library not installed. Run: pip install requests"
    }))
    sys.exit(1)

BASE_URL = "https://api.football-data.org/v4"
CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "settings.json"

COMPETITION_CODES = ["PL", "BL1", "SA", "PD", "FL1", "DED", "CL"]

RATE_LIMIT_DELAY = 6.5


def _load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _get_api_key() -> str:
    key = os.environ.get("FOOTBALL_DATA_API_KEY", "")
    if not key:
        cfg = _load_config()
        key = cfg.get("api_key", "")
    return key


def _get_competitions() -> List[str]:
    cfg = _load_config()
    return cfg.get("competitions", COMPETITION_CODES)


def _get_competition_names() -> Dict[str, str]:
    cfg = _load_config()
    return cfg.get("competition_names", {})


def _api_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    api_key = _get_api_key()
    if not api_key:
        return {
            "status": "error",
            "code": "no_api_key",
            "message": "No FOOTBALL_DATA_API_KEY set. Get a free key at football-data.org/client/register"
        }

    headers = {"X-Auth-Token": api_key}
    url = f"{BASE_URL}{endpoint}"

    for attempt in range(3):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)

            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "10"))
                time.sleep(retry_after)
                continue

            if resp.status_code == 200:
                return resp.json()

            return {
                "status": "error",
                "code": f"http_{resp.status_code}",
                "message": resp.text[:500]
            }
        except requests.RequestException as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            return {
                "status": "error",
                "code": "request_failed",
                "message": str(exc)
            }

    return {"status": "error", "code": "max_retries", "message": "Max retries exceeded"}


def fetch_fixtures(date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
    """Fetch matches for today and tomorrow across configured competitions."""
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)

    if not date_from:
        date_from = today.isoformat()
    if not date_to:
        date_to = tomorrow.isoformat()

    competitions = _get_competitions()
    comp_names = _get_competition_names()
    all_matches = []

    for code in competitions:
        data = _api_request(f"/competitions/{code}/matches", {
            "dateFrom": date_from,
            "dateTo": date_to,
        })

        if "status" in data and data.get("status") == "error":
            continue

        matches = data.get("matches", [])
        for match in matches:
            all_matches.append({
                "id": match.get("id"),
                "competition": code,
                "competition_name": comp_names.get(code, code),
                "matchday": match.get("matchday"),
                "date": match.get("utcDate"),
                "status": match.get("status"),
                "home_team": match.get("homeTeam", {}).get("name"),
                "home_team_id": match.get("homeTeam", {}).get("id"),
                "away_team": match.get("awayTeam", {}).get("name"),
                "away_team_id": match.get("awayTeam", {}).get("id"),
                "score": {
                    "home": match.get("score", {}).get("fullTime", {}).get("home"),
                    "away": match.get("score", {}).get("fullTime", {}).get("away"),
                },
            })

        time.sleep(RATE_LIMIT_DELAY)

    scheduled = [m for m in all_matches if m["status"] in ("SCHEDULED", "TIMED")]
    scheduled.sort(key=lambda m: m.get("date", ""))

    return {
        "mode": "fixtures",
        "date_from": date_from,
        "date_to": date_to,
        "total_matches": len(all_matches),
        "scheduled_matches": len(scheduled),
        "matches": scheduled,
        "completed_matches": [m for m in all_matches if m["status"] == "FINISHED"],
    }


def fetch_standings(competition: Optional[str] = None) -> Dict[str, Any]:
    """Fetch league standings with form data for one or all competitions."""
    competitions = [competition] if competition else _get_competitions()
    comp_names = _get_competition_names()
    all_standings = {}

    for code in competitions:
        if code == "CL":
            continue

        data = _api_request(f"/competitions/{code}/standings")

        if "status" in data and data.get("status") == "error":
            all_standings[code] = {"error": data.get("message", "Unknown error")}
            time.sleep(RATE_LIMIT_DELAY)
            continue

        standings_list = data.get("standings", [])
        total_standing = None
        for s in standings_list:
            if s.get("type") == "TOTAL":
                total_standing = s
                break

        if not total_standing:
            total_standing = standings_list[0] if standings_list else {"table": []}

        table = []
        for entry in total_standing.get("table", []):
            team = entry.get("team", {})
            table.append({
                "position": entry.get("position"),
                "team": team.get("name"),
                "team_id": team.get("id"),
                "played": entry.get("playedGames"),
                "won": entry.get("won"),
                "draw": entry.get("draw"),
                "lost": entry.get("lost"),
                "goals_for": entry.get("goalsFor"),
                "goals_against": entry.get("goalsAgainst"),
                "goal_difference": entry.get("goalDifference"),
                "points": entry.get("points"),
                "form": entry.get("form"),
            })

        all_standings[code] = {
            "competition_name": comp_names.get(code, code),
            "season": data.get("season", {}).get("id"),
            "matchday": data.get("season", {}).get("currentMatchday"),
            "table": table,
        }

        time.sleep(RATE_LIMIT_DELAY)

    return {
        "mode": "standings",
        "standings": all_standings,
    }


def fetch_h2h(match_id: int) -> Dict[str, Any]:
    """Fetch head-to-head record for a specific match."""
    data = _api_request(f"/matches/{match_id}/head2head", {"limit": 5})

    if "status" in data and data.get("status") == "error":
        return data

    agg = data.get("aggregates", {})
    matches = data.get("matches", [])

    h2h_matches = []
    for m in matches:
        h2h_matches.append({
            "date": m.get("utcDate"),
            "competition": m.get("competition", {}).get("name"),
            "home_team": m.get("homeTeam", {}).get("name"),
            "away_team": m.get("awayTeam", {}).get("name"),
            "score_home": m.get("score", {}).get("fullTime", {}).get("home"),
            "score_away": m.get("score", {}).get("fullTime", {}).get("away"),
            "winner": m.get("score", {}).get("winner"),
        })

    return {
        "mode": "h2h",
        "match_id": match_id,
        "total_matches": agg.get("numberOfMatches"),
        "home_team": agg.get("homeTeam", {}).get("name"),
        "away_team": agg.get("awayTeam", {}).get("name"),
        "home_wins": agg.get("homeTeam", {}).get("wins"),
        "away_wins": agg.get("awayTeam", {}).get("wins"),
        "draws": agg.get("homeTeam", {}).get("draws"),
        "recent_matches": h2h_matches,
    }


def _get_team_form(standings: Dict[str, Any], team_name: str) -> Optional[Dict[str, Any]]:
    """Look up a team's standing data across all competition standings."""
    for code, comp_data in standings.get("standings", {}).items():
        if isinstance(comp_data, dict) and "table" in comp_data:
            for entry in comp_data["table"]:
                if entry.get("team") == team_name:
                    return {
                        "competition": code,
                        "position": entry.get("position"),
                        "played": entry.get("played"),
                        "won": entry.get("won"),
                        "draw": entry.get("draw"),
                        "lost": entry.get("lost"),
                        "goals_for": entry.get("goals_for"),
                        "goals_against": entry.get("goals_against"),
                        "goal_difference": entry.get("goal_difference"),
                        "points": entry.get("points"),
                        "form": entry.get("form"),
                    }
    return None


def fetch_full(date_from: Optional[str] = None, date_to: Optional[str] = None) -> Dict[str, Any]:
    """Full analysis package: fixtures + standings + h2h for each scheduled match."""
    fixtures = fetch_fixtures(date_from, date_to)

    if not fixtures.get("scheduled_matches"):
        return {
            "mode": "full",
            "date_from": fixtures.get("date_from"),
            "date_to": fixtures.get("date_to"),
            "total_scheduled": 0,
            "message": "No scheduled matches found for the given date range.",
            "matches": [],
        }

    standings = fetch_standings()

    enriched_matches = []
    for match in fixtures.get("matches", []):
        home_form = _get_team_form(standings, match.get("home_team"))
        away_form = _get_team_form(standings, match.get("away_team"))

        match_data = {
            "id": match.get("id"),
            "competition": match.get("competition"),
            "competition_name": match.get("competition_name"),
            "date": match.get("date"),
            "home_team": match.get("home_team"),
            "away_team": match.get("away_team"),
            "home_form": home_form,
            "away_form": away_form,
            "h2h": None,
        }

        match_id = match.get("id")
        if match_id:
            time.sleep(RATE_LIMIT_DELAY)
            h2h = fetch_h2h(match_id)
            if h2h.get("mode") == "h2h":
                match_data["h2h"] = h2h

        enriched_matches.append(match_data)

    return {
        "mode": "full",
        "date_from": fixtures.get("date_from"),
        "date_to": fixtures.get("date_to"),
        "total_scheduled": len(enriched_matches),
        "matches": enriched_matches,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch football match data")
    parser.add_argument("--mode", required=True, choices=["fixtures", "standings", "h2h", "full"],
                        help="Data mode to fetch")
    parser.add_argument("--match-id", type=int, help="Match ID for h2h mode")
    parser.add_argument("--competition", type=str, help="Competition code for standings (e.g. PL, BL1)")
    parser.add_argument("--date-from", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--date-to", type=str, help="End date (YYYY-MM-DD)")

    args = parser.parse_args()

    if args.mode == "fixtures":
        result = fetch_fixtures(args.date_from, args.date_to)
    elif args.mode == "standings":
        result = fetch_standings(args.competition)
    elif args.mode == "h2h":
        if not args.match_id:
            result = {"status": "error", "code": "missing_param", "message": "--match-id is required for h2h mode"}
        else:
            result = fetch_h2h(args.match_id)
    elif args.mode == "full":
        result = fetch_full(args.date_from, args.date_to)
    else:
        result = {"status": "error", "code": "unknown_mode", "message": f"Unknown mode: {args.mode}"}

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
