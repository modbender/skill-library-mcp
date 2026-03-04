#!/usr/bin/env python3
"""
MLB Stats API Client

Fetches game schedules and live game data from the MLB Stats API.
Standard library only — no external dependencies.
"""

import json
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen


SCHEDULE_URL = "https://statsapi.mlb.com/api/v1/schedule/games"
LIVE_FEED_URL = "https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
PLAYER_SEARCH_URL = "https://statsapi.mlb.com/api/v1/people/search"
PLAYER_URL = "https://statsapi.mlb.com/api/v1/people/{player_id}"
PLAYER_STATS_URL = "https://statsapi.mlb.com/api/v1/people/{player_id}/stats"
TIMEOUT_SECONDS = 30

# All 30 MLB teams: abbreviation -> {id, name}
MLB_TEAMS = {
    "ARI": {"id": 109, "name": "Arizona Diamondbacks"},
    "ATL": {"id": 144, "name": "Atlanta Braves"},
    "BAL": {"id": 110, "name": "Baltimore Orioles"},
    "BOS": {"id": 111, "name": "Boston Red Sox"},
    "CHC": {"id": 112, "name": "Chicago Cubs"},
    "CWS": {"id": 145, "name": "Chicago White Sox"},
    "CIN": {"id": 113, "name": "Cincinnati Reds"},
    "CLE": {"id": 114, "name": "Cleveland Guardians"},
    "COL": {"id": 115, "name": "Colorado Rockies"},
    "DET": {"id": 116, "name": "Detroit Tigers"},
    "HOU": {"id": 117, "name": "Houston Astros"},
    "KC":  {"id": 118, "name": "Kansas City Royals"},
    "LAA": {"id": 108, "name": "Los Angeles Angels"},
    "LAD": {"id": 119, "name": "Los Angeles Dodgers"},
    "MIA": {"id": 146, "name": "Miami Marlins"},
    "MIL": {"id": 158, "name": "Milwaukee Brewers"},
    "MIN": {"id": 142, "name": "Minnesota Twins"},
    "NYM": {"id": 121, "name": "New York Mets"},
    "NYY": {"id": 147, "name": "New York Yankees"},
    "OAK": {"id": 133, "name": "Oakland Athletics"},
    "PHI": {"id": 143, "name": "Philadelphia Phillies"},
    "PIT": {"id": 134, "name": "Pittsburgh Pirates"},
    "SD":  {"id": 135, "name": "San Diego Padres"},
    "SF":  {"id": 137, "name": "San Francisco Giants"},
    "SEA": {"id": 136, "name": "Seattle Mariners"},
    "STL": {"id": 138, "name": "St. Louis Cardinals"},
    "TB":  {"id": 139, "name": "Tampa Bay Rays"},
    "TEX": {"id": 140, "name": "Texas Rangers"},
    "TOR": {"id": 141, "name": "Toronto Blue Jays"},
    "WSH": {"id": 120, "name": "Washington Nationals"},
}

# Reverse lookup: team ID -> abbreviation
_TEAM_ID_TO_ABBR = {info["id"]: abbr for abbr, info in MLB_TEAMS.items()}


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------

def _fetch_json(url):
    """Fetch JSON from a URL using urllib. Returns parsed dict or None on error."""
    try:
        with urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as e:
        print(f"Error: HTTP {e.code} fetching {url}", file=sys.stderr)
    except URLError as e:
        print(f"Error: Network error fetching {url}: {e.reason}", file=sys.stderr)
    except TimeoutError:
        print(f"Error: Request timed out fetching {url}", file=sys.stderr)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON from {url}", file=sys.stderr)
    return None


# ---------------------------------------------------------------------------
# Date/time helper
# ---------------------------------------------------------------------------

def _parse_game_datetime(iso_string):
    """Parse an ISO 8601 datetime string to a local datetime."""
    if not iso_string:
        return None
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.astimezone()
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class Team:
    def __init__(self, data):
        self.id = data.get("id", 0)
        self.name = data.get("name", "")
        self.abbreviation = data.get("abbreviation", "") or _TEAM_ID_TO_ABBR.get(self.id, "")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "abbreviation": self.abbreviation}


class Inning:
    def __init__(self, data):
        self.away_runs = data.get("away", {}).get("runs", 0)
        self.home_runs = data.get("home", {}).get("runs", 0)

    def to_dict(self):
        return {"away_runs": self.away_runs, "home_runs": self.home_runs}


class LineScore:
    def __init__(self, linescore_data):
        self.innings = []
        self.current_inning = linescore_data.get("currentInning", 0)
        self.is_top_inning = linescore_data.get("isTopInning", False)
        self.away_runs = linescore_data.get("teams", {}).get("away", {}).get("runs", 0)
        self.away_hits = linescore_data.get("teams", {}).get("away", {}).get("hits", 0)
        self.away_errors = linescore_data.get("teams", {}).get("away", {}).get("errors", 0)
        self.home_runs = linescore_data.get("teams", {}).get("home", {}).get("runs", 0)
        self.home_hits = linescore_data.get("teams", {}).get("home", {}).get("hits", 0)
        self.home_errors = linescore_data.get("teams", {}).get("home", {}).get("errors", 0)

        for inning_data in linescore_data.get("innings", []):
            self.innings.append(Inning(inning_data))

    def to_dict(self):
        return {
            "innings": [i.to_dict() for i in self.innings],
            "current_inning": self.current_inning,
            "is_top_inning": self.is_top_inning,
            "away": {"runs": self.away_runs, "hits": self.away_hits, "errors": self.away_errors},
            "home": {"runs": self.home_runs, "hits": self.home_hits, "errors": self.home_errors},
        }


class Matchup:
    def __init__(self, matchup_data):
        batter = matchup_data.get("batter", {})
        pitcher = matchup_data.get("pitcher", {})
        self.batter_name = batter.get("fullName", "")
        self.pitcher_name = pitcher.get("fullName", "")

    def to_dict(self):
        return {"batter_name": self.batter_name, "pitcher_name": self.pitcher_name}


class PlayResult:
    def __init__(self, result_data, about_data):
        self.description = result_data.get("description", "")
        self.event_type = result_data.get("event", "")
        self.rbi = result_data.get("rbi", 0)
        self.away_score = result_data.get("awayScore", 0)
        self.home_score = result_data.get("homeScore", 0)

    def to_dict(self):
        return {
            "description": self.description,
            "event_type": self.event_type,
            "rbi": self.rbi,
            "away_score": self.away_score,
            "home_score": self.home_score,
        }


class GameStatus:
    """Full live game data from the live feed endpoint."""

    def __init__(self, game_pk, data):
        self.game_pk = game_pk
        game_data = data.get("gameData", {})
        live_data = data.get("liveData", {})

        # Status
        status_node = game_data.get("status", {})
        self.status = status_node.get("detailedState", "Unknown")

        # Teams
        teams_node = game_data.get("teams", {})
        self.away_team = Team(teams_node.get("away", {}))
        self.home_team = Team(teams_node.get("home", {}))

        # Venue and start time
        venue_node = game_data.get("venue", {})
        self.venue = venue_node.get("name", "")
        datetime_node = game_data.get("datetime", {})
        self.start_time = _parse_game_datetime(datetime_node.get("dateTime"))

        # Line score
        linescore_data = live_data.get("linescore", {})
        self.line_score = LineScore(linescore_data)

        # Score (from linescore totals)
        self.away_score = self.line_score.away_runs
        self.home_score = self.line_score.home_runs

        # Inning info
        self.inning = linescore_data.get("currentInning", 0)
        self.inning_half = "Top" if linescore_data.get("isTopInning", True) else "Bottom"

        # Count and outs
        self.balls = 0
        self.strikes = 0
        self.outs = linescore_data.get("outs", 0)

        # Runners
        self.runners = {"first": False, "second": False, "third": False}

        # Current play data
        self.matchup = None
        self.last_play = None

        plays_node = live_data.get("plays", {})
        current_play = plays_node.get("currentPlay", {})

        if current_play:
            # Count
            count = current_play.get("count", {})
            self.balls = count.get("balls", 0)
            self.strikes = count.get("strikes", 0)
            self.outs = count.get("outs", self.outs)

            # Matchup
            matchup_data = current_play.get("matchup", {})
            if matchup_data:
                self.matchup = Matchup(matchup_data)
                # Runners from matchup
                if "postOnFirst" in matchup_data:
                    self.runners["first"] = True
                if "postOnSecond" in matchup_data:
                    self.runners["second"] = True
                if "postOnThird" in matchup_data:
                    self.runners["third"] = True

            # Last play result
            result_data = current_play.get("result", {})
            about_data = current_play.get("about", {})
            if result_data.get("description"):
                self.last_play = PlayResult(result_data, about_data)

    def to_dict(self):
        result = {
            "game_pk": self.game_pk,
            "status": self.status,
            "venue": self.venue,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "away_team": self.away_team.to_dict(),
            "home_team": self.home_team.to_dict(),
            "away_score": self.away_score,
            "home_score": self.home_score,
            "inning": self.inning,
            "inning_half": self.inning_half,
            "balls": self.balls,
            "strikes": self.strikes,
            "outs": self.outs,
            "runners": self.runners,
            "matchup": self.matchup.to_dict() if self.matchup else None,
            "last_play": self.last_play.to_dict() if self.last_play else None,
            "line_score": self.line_score.to_dict(),
        }
        return result


class GameSummary:
    """Summary game info from the schedule endpoint (no live feed call)."""

    def __init__(self, game_node):
        self.game_pk = game_node.get("gamePk", 0)

        # Status
        status_node = game_node.get("status", {})
        self.status = status_node.get("detailedState", "Unknown")

        # Teams
        teams_node = game_node.get("teams", {})
        away_node = teams_node.get("away", {})
        home_node = teams_node.get("home", {})
        self.away_team = Team(away_node.get("team", {}))
        self.home_team = Team(home_node.get("team", {}))

        # Records
        away_record = away_node.get("leagueRecord", {})
        home_record = home_node.get("leagueRecord", {})
        self.away_record = f"{away_record.get('wins', 0)}-{away_record.get('losses', 0)}"
        self.home_record = f"{home_record.get('wins', 0)}-{home_record.get('losses', 0)}"

        # Score (available for in-progress and final games)
        self.away_score = away_node.get("score", 0)
        self.home_score = home_node.get("score", 0)

        # Venue and time
        venue_node = game_node.get("venue", {})
        self.venue = venue_node.get("name", "")
        self.start_time = _parse_game_datetime(game_node.get("gameDate"))

    def to_dict(self):
        return {
            "game_pk": self.game_pk,
            "status": self.status,
            "away_team": self.away_team.to_dict(),
            "home_team": self.home_team.to_dict(),
            "away_record": self.away_record,
            "home_record": self.home_record,
            "away_score": self.away_score,
            "home_score": self.home_score,
            "venue": self.venue,
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }


class PlayerInfo:
    """Player profile from search or people endpoint."""

    def __init__(self, data):
        self.id = data.get("id", 0)
        self.full_name = data.get("fullName", "")
        self.first_name = data.get("firstName", "")
        self.last_name = data.get("lastName", "")
        self.active = data.get("active", False)
        self.primary_number = data.get("primaryNumber", "")
        self.height = data.get("height", "")
        self.weight = data.get("weight", 0)
        self.birth_date = data.get("birthDate", "")
        self.current_age = data.get("currentAge", 0)
        self.mlb_debut_date = data.get("mlbDebutDate", "")
        pos = data.get("primaryPosition", {})
        self.position = pos.get("abbreviation", "")
        self.position_name = pos.get("name", "")
        self.bats = data.get("batSide", {}).get("code", "")
        self.throws = data.get("pitchHand", {}).get("code", "")
        team = data.get("currentTeam", {})
        self.team_id = team.get("id", 0)
        self.team_name = team.get("name", "")
        self.team_abbreviation = _TEAM_ID_TO_ABBR.get(self.team_id, "")

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "active": self.active,
            "primary_number": self.primary_number,
            "height": self.height,
            "weight": self.weight,
            "birth_date": self.birth_date,
            "age": self.current_age,
            "mlb_debut_date": self.mlb_debut_date,
            "position": self.position,
            "position_name": self.position_name,
            "bats": self.bats,
            "throws": self.throws,
            "team_id": self.team_id,
            "team": self.team_name,
            "team_abbreviation": self.team_abbreviation,
        }


class BattingStats:
    """Season batting statistics."""

    def __init__(self, data):
        stat = data.get("stat", {})
        self.season = data.get("season", "")
        self.team_name = data.get("team", {}).get("name", "")
        self.games_played = stat.get("gamesPlayed", 0)
        self.at_bats = stat.get("atBats", 0)
        self.plate_appearances = stat.get("plateAppearances", 0)
        self.runs = stat.get("runs", 0)
        self.hits = stat.get("hits", 0)
        self.doubles = stat.get("doubles", 0)
        self.triples = stat.get("triples", 0)
        self.home_runs = stat.get("homeRuns", 0)
        self.rbi = stat.get("rbi", 0)
        self.stolen_bases = stat.get("stolenBases", 0)
        self.walks = stat.get("baseOnBalls", 0)
        self.strikeouts = stat.get("strikeOuts", 0)
        self.avg = stat.get("avg", ".000")
        self.obp = stat.get("obp", ".000")
        self.slg = stat.get("slg", ".000")
        self.ops = stat.get("ops", ".000")

    def to_dict(self):
        return {
            "season": self.season,
            "team_name": self.team_name,
            "games_played": self.games_played,
            "at_bats": self.at_bats,
            "plate_appearances": self.plate_appearances,
            "runs": self.runs,
            "hits": self.hits,
            "doubles": self.doubles,
            "triples": self.triples,
            "home_runs": self.home_runs,
            "rbi": self.rbi,
            "stolen_bases": self.stolen_bases,
            "walks": self.walks,
            "strikeouts": self.strikeouts,
            "avg": self.avg,
            "obp": self.obp,
            "slg": self.slg,
            "ops": self.ops,
        }


class PitchingStats:
    """Season pitching statistics."""

    def __init__(self, data):
        stat = data.get("stat", {})
        self.season = data.get("season", "")
        self.team_name = data.get("team", {}).get("name", "")
        self.games_played = stat.get("gamesPlayed", 0)
        self.games_started = stat.get("gamesStarted", 0)
        self.wins = stat.get("wins", 0)
        self.losses = stat.get("losses", 0)
        self.era = stat.get("era", "0.00")
        self.innings_pitched = stat.get("inningsPitched", "0.0")
        self.hits = stat.get("hits", 0)
        self.runs = stat.get("runs", 0)
        self.earned_runs = stat.get("earnedRuns", 0)
        self.home_runs = stat.get("homeRuns", 0)
        self.strikeouts = stat.get("strikeOuts", 0)
        self.walks = stat.get("baseOnBalls", 0)
        self.saves = stat.get("saves", 0)
        self.holds = stat.get("holds", 0)
        self.whip = stat.get("whip", "0.00")
        self.strikeouts_per_9 = stat.get("strikeoutsPer9Inn", "0.00")
        self.walks_per_9 = stat.get("walksPer9Inn", "0.00")

    def to_dict(self):
        return {
            "season": self.season,
            "team_name": self.team_name,
            "games_played": self.games_played,
            "games_started": self.games_started,
            "wins": self.wins,
            "losses": self.losses,
            "era": self.era,
            "innings_pitched": self.innings_pitched,
            "hits": self.hits,
            "runs": self.runs,
            "earned_runs": self.earned_runs,
            "home_runs": self.home_runs,
            "strikeouts": self.strikeouts,
            "walks": self.walks,
            "saves": self.saves,
            "holds": self.holds,
            "whip": self.whip,
            "strikeouts_per_9": self.strikeouts_per_9,
            "walks_per_9": self.walks_per_9,
        }


class PlayerStats:
    """Container for player info and season stats."""

    def __init__(self, player, batting=None, pitching=None):
        self.player = player
        self.batting = batting
        self.pitching = pitching

    def to_dict(self):
        result = {"player": self.player.to_dict()}
        result["batting"] = self.batting.to_dict() if self.batting else None
        result["pitching"] = self.pitching.to_dict() if self.pitching else None
        return result


# ---------------------------------------------------------------------------
# API functions
# ---------------------------------------------------------------------------

def fetch_schedule(date_str, end_date_str=None):
    """Fetch the game schedule. Returns list of GameSummary.

    Args:
        date_str: Start date in MM/DD/YYYY format.
        end_date_str: Optional end date in MM/DD/YYYY format for a range.
    """
    if end_date_str:
        url = f"{SCHEDULE_URL}?sportId=1&startDate={date_str}&endDate={end_date_str}"
    else:
        url = f"{SCHEDULE_URL}?sportId=1&date={date_str}"
    data = _fetch_json(url)
    if data is None:
        return []

    games = []
    for date_entry in data.get("dates", []):
        date_label = date_entry.get("date", "")
        for game_node in date_entry.get("games", []):
            summary = GameSummary(game_node)
            summary.date_label = date_label
            games.append(summary)
    return games


def fetch_live_game(game_pk):
    """Fetch full live data for a game. Returns GameStatus or None."""
    url = LIVE_FEED_URL.format(game_pk=game_pk)
    data = _fetch_json(url)
    if data is None:
        return None
    return GameStatus(game_pk, data)


def lookup_team(query):
    """Look up a team by abbreviation or partial name (case-insensitive).

    Returns (abbreviation, team_info) or (None, None) if not found.
    """
    query_upper = query.strip().upper()

    # Exact abbreviation match
    if query_upper in MLB_TEAMS:
        return query_upper, MLB_TEAMS[query_upper]

    # Partial name match
    query_lower = query.strip().lower()
    for abbr, info in MLB_TEAMS.items():
        if query_lower in info["name"].lower():
            return abbr, info

    return None, None


def search_players(name, team_abbr=None):
    """Search for active MLB players by name.

    Args:
        name: Player name (or partial name) to search for.
        team_abbr: Optional team abbreviation to filter results.

    Returns list of PlayerInfo.
    """
    url = f"{PLAYER_SEARCH_URL}?names={quote(name)}&hydrate=currentTeam"
    data = _fetch_json(url)
    if data is None:
        return []

    players = []
    for row in data.get("people", []):
        if not row.get("active", False):
            continue
        player = PlayerInfo(row)
        if team_abbr and player.team_abbreviation != team_abbr.upper():
            continue
        players.append(player)
    return players


def fetch_player_stats(player_id, season=None):
    """Fetch player info and season stats.

    Args:
        player_id: MLB player ID.
        season: Year (int or str). Defaults to current year.

    Returns PlayerStats or None.
    """
    if season is None:
        season = datetime.now().year

    # Fetch player info
    info_url = f"{PLAYER_URL.format(player_id=player_id)}?hydrate=currentTeam"
    info_data = _fetch_json(info_url)
    if info_data is None:
        return None
    people = info_data.get("people", [])
    if not people:
        return None
    player = PlayerInfo(people[0])

    # Fetch stats (hitting + pitching in one call)
    stats_url = (
        f"{PLAYER_STATS_URL.format(player_id=player_id)}"
        f"?stats=season&season={season}&group=hitting,pitching"
    )
    stats_data = _fetch_json(stats_url)

    batting = None
    pitching = None
    if stats_data:
        for group in stats_data.get("stats", []):
            group_name = group.get("group", {}).get("displayName", "")
            splits = group.get("splits", [])
            if not splits:
                continue
            if group_name == "hitting":
                batting = BattingStats(splits[-1])
            elif group_name == "pitching":
                pitching = PitchingStats(splits[-1])

    return PlayerStats(player, batting, pitching)
