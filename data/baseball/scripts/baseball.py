#!/usr/bin/env python3
"""
Baseball — MLB game schedules, live status, box scores, player search, and stats.

Usage:
    python scripts/baseball.py games [--team PHI] [--date MM/DD/YYYY] [--format text|json]
    python scripts/baseball.py live <gamePk_or_team> [--date MM/DD/YYYY] [--format text|json]
    python scripts/baseball.py score <gamePk_or_team> [--date MM/DD/YYYY] [--format text|json]
    python scripts/baseball.py player <name> [--team PHI] [--format text|json]
    python scripts/baseball.py stats <player> [--season 2025] [--format text|json]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

from mlb_api import (
    fetch_schedule, fetch_live_game, lookup_team, MLB_TEAMS,
    search_players, fetch_player_stats,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_start_time(dt):
    """Format a datetime as a short local time string like '7:10 PM'."""
    if dt is None:
        return "TBD"
    return dt.strftime("%I:%M %p").lstrip("0")


def _ordinal(n):
    """Return ordinal string: 1 -> '1st', 2 -> '2nd', etc."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def _resolve_game_pk(arg, date=None):
    """Resolve a game PK from a numeric string or team abbreviation.

    If arg is numeric, return it as an integer.
    If alphabetic, look up the schedule for that team's game on the given date
    (defaults to today).
    """
    if arg.isdigit():
        return int(arg)

    abbr, team_info = lookup_team(arg)
    if abbr is None:
        print(f"Error: Unknown team '{arg}'.", file=sys.stderr)
        print("Run 'baseball.py teams' to see valid abbreviations.", file=sys.stderr)
        sys.exit(1)

    team_name = team_info["name"]
    lookup_date = date if date else datetime.now().strftime("%m/%d/%Y")
    games = fetch_schedule(lookup_date)

    if not games:
        print(f"Error: No games scheduled for {lookup_date}.", file=sys.stderr)
        sys.exit(1)

    for game in games:
        if game.away_team.abbreviation == abbr or game.home_team.abbreviation == abbr:
            return game.game_pk

    print(f"Error: {team_name} ({abbr}) is not playing on {lookup_date}.", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# games subcommand
# ---------------------------------------------------------------------------

def _status_display(game):
    """Short status string for the games table."""
    status = game.status
    if status == "Final":
        if game.away_score or game.home_score:
            return f"Final ({game.away_score}-{game.home_score})"
        return "Final"
    if status in ("In Progress", "Manager Challenge"):
        return "In Progress"
    if status in ("Scheduled", "Pre-Game", "Warmup"):
        return _format_start_time(game.start_time)
    return status


def cmd_games(args):
    start_date = args.date if args.date else datetime.now().strftime("%m/%d/%Y")
    end_date = None

    if args.days and args.days > 1:
        try:
            start_dt = datetime.strptime(start_date, "%m/%d/%Y")
        except ValueError:
            print(f"Error: Invalid date format '{start_date}'. Use MM/DD/YYYY.", file=sys.stderr)
            sys.exit(1)
        end_dt = start_dt + timedelta(days=args.days - 1)
        end_date = end_dt.strftime("%m/%d/%Y")

    games = fetch_schedule(start_date, end_date)

    # Filter by team
    team_abbr = None
    if args.team:
        team_abbr, _ = lookup_team(args.team)
        if team_abbr is None:
            print(f"Error: Unknown team '{args.team}'.", file=sys.stderr)
            print("Run 'baseball.py teams' to see valid abbreviations.", file=sys.stderr)
            sys.exit(1)
        games = [
            g for g in games
            if g.away_team.abbreviation == team_abbr or g.home_team.abbreviation == team_abbr
        ]

    date_label = start_date if not end_date else f"{start_date} - {end_date}"

    if not games:
        msg = f"No games found for {date_label}"
        if args.team:
            msg += f" (team: {args.team.upper()})"
        if args.format == "json":
            print(json.dumps({"date": date_label, "games": []}, indent=2))
        else:
            print(msg)
        return

    if args.format == "json":
        output = {
            "date": date_label,
            "games": [g.to_dict() for g in games],
        }
        print(json.dumps(output, indent=2))
    else:
        _output_games_text(date_label, games, multi_day=bool(end_date))


def _output_games_text(date_label, games, multi_day=False):
    print(f"MLB Games - {date_label}")
    header = f"{'Away':<17} {'Record':<10} {'Home':<17} {'Record':<10} {'Time':<10} {'Status':<20} {'Game ID'}"
    print(header)
    print("-" * 95)

    current_date = None
    for g in games:
        # Print date separator for multi-day ranges
        if multi_day:
            game_date = getattr(g, "date_label", "")
            if game_date and game_date != current_date:
                if current_date is not None:
                    print()
                print(f"  {game_date}")
                current_date = game_date

        away_label = f"{g.away_team.abbreviation} {g.away_team.name.split()[-1]}"
        home_label = f"{g.home_team.abbreviation} {g.home_team.name.split()[-1]}"
        time_str = _format_start_time(g.start_time)
        status = _status_display(g)
        print(
            f"{away_label:<17} {g.away_record:<10} "
            f"{home_label:<17} {g.home_record:<10} "
            f"{time_str:<10} {status:<20} {g.game_pk}"
        )


# ---------------------------------------------------------------------------
# live subcommand
# ---------------------------------------------------------------------------

def cmd_live(args):
    game_pk = _resolve_game_pk(args.game, date=args.date)
    game = fetch_live_game(game_pk)

    if game is None:
        print(f"Error: Could not fetch live data for game {game_pk}.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(game.to_dict(), indent=2))
    else:
        _output_live_text(game)


def _output_live_text(game):
    away = game.away_team
    home = game.home_team

    # Header line
    away_label = f"{away.abbreviation} {away.name.split()[-1]}"
    home_label = f"{home.abbreviation} {home.name.split()[-1]}"
    print(f"{away_label} {game.away_score}  @  {home_label} {game.home_score}")

    # Status line
    if game.status in ("In Progress", "Manager Challenge"):
        half = "Top" if game.inning_half == "Top" else "Bot"
        inning_str = _ordinal(game.inning)
        outs_str = f"{game.outs} out{'s' if game.outs != 1 else ''}"
        count_str = f"{game.balls}-{game.strikes} count"
        print(f"  {half} {inning_str}  |  {outs_str}  |  {count_str}")

        # Runners
        first = "[X]" if game.runners["first"] else "[ ]"
        second = "[X]" if game.runners["second"] else "[ ]"
        third = "[X]" if game.runners["third"] else "[ ]"
        print(f"  Bases: 1B {first}  2B {second}  3B {third}")

        # Matchup
        if game.matchup:
            print(f"  AB: {game.matchup.batter_name}  vs  P: {game.matchup.pitcher_name}")

        # Last play
        if game.last_play and game.last_play.description:
            print(f"  Last: {game.last_play.description}")
    else:
        print(f"  Status: {game.status}")

    print()
    _output_linescore_text(game)


def _output_linescore_text(game):
    """Print the box score line score."""
    innings = game.line_score.innings
    num_innings = max(len(innings), 9)

    # Header
    header = "    "
    for i in range(1, num_innings + 1):
        header += f"{i:>3}"
    header += "    R  H  E"
    print(header)

    # Away line
    away_line = f"{game.away_team.abbreviation:<4}"
    for i in range(num_innings):
        if i < len(innings):
            away_line += f"{innings[i].away_runs:>3}"
        else:
            away_line += "  -"
    away_line += f"  {game.line_score.away_runs:>3}{game.line_score.away_hits:>3}{game.line_score.away_errors:>3}"
    print(away_line)

    # Home line
    home_line = f"{game.home_team.abbreviation:<4}"
    for i in range(num_innings):
        if i < len(innings):
            # If current inning, top half, and this is the last inning — home hasn't batted yet
            if (i == len(innings) - 1
                    and game.line_score.is_top_inning
                    and game.status in ("In Progress", "Manager Challenge")):
                home_line += "  -"
            else:
                home_line += f"{innings[i].home_runs:>3}"
        else:
            home_line += "  -"
    home_line += f"  {game.line_score.home_runs:>3}{game.line_score.home_hits:>3}{game.line_score.home_errors:>3}"
    print(home_line)


# ---------------------------------------------------------------------------
# score subcommand
# ---------------------------------------------------------------------------

def cmd_score(args):
    game_pk = _resolve_game_pk(args.game, date=args.date)
    game = fetch_live_game(game_pk)

    if game is None:
        print(f"Error: Could not fetch data for game {game_pk}.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        print(json.dumps(game.to_dict(), indent=2))
    else:
        _output_score_text(game)


def _output_score_text(game):
    away = game.away_team
    home = game.home_team

    away_label = f"{away.abbreviation} {away.name.split()[-1]}"
    home_label = f"{home.abbreviation} {home.name.split()[-1]}"

    if game.status == "Final":
        print(f"Final: {away_label} {game.away_score}  @  {home_label} {game.home_score}")
    else:
        print(f"{game.status}: {away_label} {game.away_score}  @  {home_label} {game.home_score}")

    print()
    _output_linescore_text(game)


# ---------------------------------------------------------------------------
# teams subcommand
# ---------------------------------------------------------------------------

def cmd_teams(args):
    teams = sorted(MLB_TEAMS.items(), key=lambda t: t[0])

    if args.format == "json":
        output = [{"abbreviation": abbr, "name": info["name"]} for abbr, info in teams]
        print(json.dumps({"teams": output}, indent=2))
    else:
        print(f"{'Abbr':<6} {'Team Name'}")
        print("-" * 35)
        for abbr, info in teams:
            print(f"{abbr:<6} {info['name']}")


# ---------------------------------------------------------------------------
# player subcommand
# ---------------------------------------------------------------------------

def cmd_player(args):
    name = " ".join(args.name)
    team_abbr = None
    if args.team:
        team_abbr, _ = lookup_team(args.team)
        if team_abbr is None:
            print(f"Error: Unknown team '{args.team}'.", file=sys.stderr)
            sys.exit(1)

    players = search_players(name, team_abbr=team_abbr)

    if not players:
        msg = f'No active players found for "{name}"'
        if team_abbr:
            msg += f" on {team_abbr}"
        if args.format == "json":
            print(json.dumps({"query": name, "players": []}, indent=2))
        else:
            print(msg)
        return

    if args.format == "json":
        output = {
            "query": name,
            "players": [p.to_dict() for p in players],
        }
        print(json.dumps(output, indent=2))
    else:
        _output_player_search_text(name, players)


def _output_player_search_text(query, players):
    print(f'Player Search: "{query}"')
    print(f"{'ID':<11}{'Name':<26}{'Pos':<6}{'Team':<21}{'#':<6}{'B/T':<6}{'Age'}")
    print("-" * 80)
    for p in players:
        team_label = f"{p.team_abbreviation} {p.team_name.split()[-1]}" if p.team_abbreviation else p.team_name
        bt = f"{p.bats}/{p.throws}" if p.bats and p.throws else ""
        num = p.primary_number if p.primary_number else ""
        age = str(p.current_age) if p.current_age else ""
        print(f"{p.id:<11}{p.full_name:<26}{p.position:<6}{team_label:<21}{num:<6}{bt:<6}{age}")
    if len(players) > 1:
        print(f"\nUse 'stats <ID>' to view a player's season statistics.")


# ---------------------------------------------------------------------------
# stats subcommand
# ---------------------------------------------------------------------------

def cmd_stats(args):
    player_arg = " ".join(args.player)
    season = args.season if args.season else datetime.now().year

    # Determine player ID: numeric or name search
    if player_arg.isdigit():
        player_id = int(player_arg)
    else:
        players = search_players(player_arg)
        if not players:
            print(f'Error: No active players found for "{player_arg}".', file=sys.stderr)
            sys.exit(1)
        if len(players) > 1:
            print(f'Multiple players match "{player_arg}". Use a player ID:', file=sys.stderr)
            for p in players:
                team_label = f"{p.team_abbreviation} {p.team_name.split()[-1]}" if p.team_abbreviation else p.team_name
                print(f"  {p.id:<11}{p.full_name:<26}{p.position:<6}{team_label}", file=sys.stderr)
            sys.exit(1)
        player_id = players[0].id

    result = fetch_player_stats(player_id, season=season)
    if result is None:
        print(f"Error: Could not fetch stats for player {player_id}.", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        output = result.to_dict()
        output["season"] = str(season)
        print(json.dumps(output, indent=2))
    else:
        _output_stats_text(result, season)


def _output_stats_text(result, season):
    p = result.player
    team_label = p.team_name if p.team_name else "Free Agent"
    num = f"  #{p.primary_number}" if p.primary_number else ""
    pos = f"  {p.position}" if p.position else ""
    bt = f"{p.bats}/{p.throws}" if p.bats and p.throws else ""
    age = f"Age {p.current_age}" if p.current_age else ""
    parts = [s for s in [bt, age] if s]
    extra = "  |  ".join(parts)
    print(f"{p.full_name}{num}{pos}  |  {team_label}  |  {extra}")

    if result.batting:
        _output_batting_text(result.batting, season)
    if result.pitching:
        _output_pitching_text(result.pitching, season)
    if not result.batting and not result.pitching:
        print(f"No stats available for {season} season.")


def _output_batting_text(b, season):
    print(f"{season} Season Batting Statistics")
    print(
        f"  {'G':<6}{'AB':<6}{'R':<6}{'H':<5}{'2B':<5}{'3B':<5}"
        f"{'HR':<5}{'RBI':<6}{'SB':<5}{'BB':<6}{'K':<6}"
        f"{'AVG':<7}{'OBP':<7}{'SLG':<7}{'OPS'}"
    )
    print(
        f"  {b.games_played:<6}{b.at_bats:<6}{b.runs:<6}{b.hits:<5}"
        f"{b.doubles:<5}{b.triples:<5}{b.home_runs:<5}{b.rbi:<6}"
        f"{b.stolen_bases:<5}{b.walks:<6}{b.strikeouts:<6}"
        f"{b.avg:<7}{b.obp:<7}{b.slg:<7}{b.ops}"
    )


def _output_pitching_text(pit, season):
    print(f"{season} Season Pitching Statistics")
    print(
        f"  {'G':<5}{'GS':<5}{'W':<5}{'L':<5}{'ERA':<7}{'IP':<8}"
        f"{'H':<5}{'R':<5}{'ER':<5}{'HR':<5}{'SO':<5}{'BB':<5}"
        f"{'SV':<5}{'HLD':<5}{'WHIP':<7}{'K/9':<7}{'BB/9'}"
    )
    print(
        f"  {pit.games_played:<5}{pit.games_started:<5}{pit.wins:<5}{pit.losses:<5}"
        f"{pit.era:<7}{pit.innings_pitched:<8}{pit.hits:<5}{pit.runs:<5}"
        f"{pit.earned_runs:<5}{pit.home_runs:<5}{pit.strikeouts:<5}{pit.walks:<5}"
        f"{pit.saves:<5}{pit.holds:<5}{pit.whip:<7}{pit.strikeouts_per_9:<7}"
        f"{pit.walks_per_9}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="MLB game schedules, live status, box scores, player search, and stats"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # teams
    teams_parser = subparsers.add_parser("teams", help="List all MLB team abbreviations")
    teams_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    # games
    games_parser = subparsers.add_parser("games", help="List games for a date")
    games_parser.add_argument("--team", help="Filter by team abbreviation (e.g., PHI)")
    games_parser.add_argument("--date", help="Start date in MM/DD/YYYY format (default: today)")
    games_parser.add_argument("--days", type=int, help="Number of days to show (e.g., 7 for a week)")
    games_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    # live
    live_parser = subparsers.add_parser("live", help="Live game status with count, runners, matchup")
    live_parser.add_argument("game", help="Game PK (numeric) or team abbreviation (e.g., PHI)")
    live_parser.add_argument("--date", help="Date to look up team's game (MM/DD/YYYY, default: today)")
    live_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    # score
    score_parser = subparsers.add_parser("score", help="Box score for a game")
    score_parser.add_argument("game", help="Game PK (numeric) or team abbreviation (e.g., PHI)")
    score_parser.add_argument("--date", help="Date to look up team's game (MM/DD/YYYY, default: today)")
    score_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    # player
    player_parser = subparsers.add_parser("player", help="Search for a player by name")
    player_parser.add_argument("name", nargs="+", help="Player name (e.g., Judge or Aaron Judge)")
    player_parser.add_argument("--team", help="Filter by team abbreviation (e.g., PHI)")
    player_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show player season statistics")
    stats_parser.add_argument("player", nargs="+", help="Player ID (numeric) or name (e.g., Aaron Judge)")
    stats_parser.add_argument("--season", type=int, help="Season year (default: current year)")
    stats_parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    if args.command == "teams":
        cmd_teams(args)
    elif args.command == "games":
        cmd_games(args)
    elif args.command == "live":
        cmd_live(args)
    elif args.command == "score":
        cmd_score(args)
    elif args.command == "player":
        cmd_player(args)
    elif args.command == "stats":
        cmd_stats(args)


if __name__ == "__main__":
    main()
