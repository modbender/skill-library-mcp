#!/usr/bin/env python3
"""
Kalshi Market Browser — Conversational Output

Shows today's markets enriched with Fuku predictions and edges.
Designed to be called by agents and relayed to users as-is.

Output format: one "main line" per market type per game (closest to 50¢),
our model prediction first, then the recommended side with edge and payout.

Usage:
    python browse.py                      # Tonight's NBA
    python browse.py --sport nba          # Explicit sport
    python browse.py --date 2026-03-03    # Specific date
    python browse.py --game "Boston"      # Filter to one game
    python browse.py --json               # Machine-readable output
"""

import os
import sys
import json
import math
import argparse
from datetime import date
from typing import Dict, List, Optional, Tuple

try:
    import httpx
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing: {e}. Run: pip install httpx python-dotenv")
    sys.exit(1)

_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(_dir, "..", ".env"))
load_dotenv()

from kalshi_client import KalshiClient

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

FUKU_BASE = "https://cbb-predictions-api-nzpk.onrender.com"

SPORT_STD = {
    "nba":    {"spread": 11.0, "total": 10.5},
    "cbb":    {"spread": 12.0, "total": 11.0},
    "nhl":    {"spread": 1.5,  "total": 1.3},
    "soccer": {"spread": 1.2,  "total": 1.1},
}

# Map sport → Kalshi series tickers
SERIES = {
    "nba": {
        "spread": "KXNBASPREAD",
        "total":  "KXNBATOTAL",
        "winner": "KXNBAGAME",
    },
    "cbb": {
        "spread": "KXNCAAMBSPREAD",
        "total":  "KXNCAAMBTOTAL",
        "winner": "KXNCAABGAME",
    },
    "nhl": {
        "spread": "KXNHLSPREAD",
        "total":  "KXNHLTOTAL",
        "winner": "KXNHLGAME",
    },
}

# Soccer league code → Kalshi series mapping
SOCCER_SERIES = {
    "EPL": {"spread": "KXEPLSPREAD", "total": "KXEPLTOTAL", "winner": "KXEPLGAME", "btts": "KXEPLBTTS"},
    "ESP": {"spread": "KXLALIGASPREAD", "total": "KXLALIGATOTAL", "winner": "KXLALIGAGAME", "btts": "KXLALIGABTTS"},
    "GER": {"spread": "KXBUNDESLIGASPREAD", "total": "KXBUNDESLIGATOTAL", "winner": "KXBUNDESLIGAGAME", "btts": "KXBUNDESLIGABTTS"},
    "ITA": {"spread": "KXSERIEASPREAD", "total": "KXSERIEATOTAL", "winner": "KXSERIEAGAME", "btts": "KXSERIEABTTS"},
    "FRA": {"spread": "KXLIGUE1SPREAD", "total": "KXLIGUE1TOTAL", "winner": "KXLIGUE1GAME", "btts": "KXLIGUE1BTTS"},
    "UCL": {"spread": "KXUCLSPREAD", "total": "KXUCLTOTAL", "winner": "KXUCLGAME", "btts": "KXUCLBTTS"},
    "MLS": {"spread": "KXMLSSPREAD", "total": "KXMLSTOTAL", "winner": "KXMLSGAME", "btts": "KXMLSBTTS"},
}

# Team abbreviation map (extend as needed)
TEAM_ABBR = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BKN",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS",
    # NHL
    "Anaheim Ducks": "ANA", "Arizona Coyotes": "ARI", "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF", "Calgary Flames": "CGY", "Carolina Hurricanes": "CAR",
    "Chicago Blackhawks": "CHI", "Colorado Avalanche": "COL", "Columbus Blue Jackets": "CBJ",
    "Dallas Stars": "DAL", "Detroit Red Wings": "DET", "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA", "Los Angeles Kings": "LAK", "Minnesota Wild": "MIN",
    "Montreal Canadiens": "MTL", "Nashville Predators": "NSH", "New Jersey Devils": "NJD",
    "New York Islanders": "NYI", "New York Rangers": "NYR", "Ottawa Senators": "OTT",
    "Philadelphia Flyers": "PHI", "Pittsburgh Penguins": "PIT", "San Jose Sharks": "SJS",
    "Seattle Kraken": "SEA", "St. Louis Blues": "STL", "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR", "Utah Hockey Club": "UTA", "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK", "Washington Capitals": "WSH", "Winnipeg Jets": "WPG",
}
ABBR_TO_TEAM = {v: k for k, v in TEAM_ABBR.items()}


# ---------------------------------------------------------------------------
# Math
# ---------------------------------------------------------------------------

def ncdf(x: float) -> float:
    """Standard normal CDF via erfc."""
    return 0.5 * math.erfc(-x / math.sqrt(2))


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_predictions(sport: str, dt: str) -> List[Dict]:
    """Fetch Fuku predictions for a sport + date."""
    if sport == "soccer":
        url = f"{FUKU_BASE}/api/public/soccer/predictions"
    else:
        url = f"{FUKU_BASE}/api/public/{sport}/predictions"
    try:
        r = httpx.get(url, params={"date": dt}, timeout=15)
        if r.status_code != 200:
            return []
        data = r.json()
        if sport == "soccer":
            # Normalize soccer fields to match other sports
            matches = data.get("matches", [])
            for m in matches:
                m["projected_home_score"] = m.get("predicted_home_score")
                m["projected_away_score"] = m.get("predicted_away_score")
                m["fuku_total"] = m.get("predicted_total")
                m["home_team"] = m.get("home_team", "")
                m["away_team"] = m.get("away_team", "")
            return matches
        return data if isinstance(data, list) else data.get("games", data.get("predictions", []))
    except Exception:
        return []


def fetch_markets(client: KalshiClient, sport: str) -> Dict[str, List[Dict]]:
    """Fetch all Kalshi markets grouped by type for a sport."""
    if sport == "soccer":
        # Fetch from all soccer leagues
        result: Dict[str, List[Dict]] = {"spread": [], "total": [], "winner": [], "btts": []}
        for league, league_series in SOCCER_SERIES.items():
            for mtype, ticker in league_series.items():
                mkts = client.get_all_markets(series_ticker=ticker)
                if mtype in result:
                    result[mtype].extend(mkts)
        return result
    series = SERIES.get(sport, {})
    result = {}
    for mtype, ticker in series.items():
        result[mtype] = client.get_all_markets(series_ticker=ticker)
    return result


# ---------------------------------------------------------------------------
# Matching + Edge calculation
# ---------------------------------------------------------------------------

def find_main_line(markets: List[Dict], game_key: str) -> Optional[Dict]:
    """Find the contract closest to 50¢ for a game (the 'main line')."""
    candidates = [m for m in markets if game_key in m.get("ticker", "")]
    if not candidates:
        return None
    # Closest to 50¢
    return min(candidates, key=lambda m: abs(int(m.get("yes_ask", m.get("yes_price", 50))) - 50))


def find_all_game_markets(markets: List[Dict], game_key: str) -> List[Dict]:
    """Return all contracts for a game."""
    return [m for m in markets if game_key in m.get("ticker", "")]


def parse_spread_ticker(ticker: str) -> Optional[Tuple[str, float]]:
    """Extract team code and line from spread ticker.
    KXNBASPREAD-26MAR02BOSMIL-BOS7 → ('BOS', 7.5)"""
    import re
    match = re.search(r'-([A-Z]+)(\d+)$', ticker)
    if not match:
        return None
    return match.group(1), float(match.group(2)) + 0.5


def parse_total_ticker(ticker: str) -> Optional[float]:
    """Extract total line from total ticker.
    KXNBATOTAL-26MAR02BOSMIL-215 → 215.5"""
    import re
    match = re.search(r'-(\d+)$', ticker)
    if not match:
        return None
    return float(match.group(1)) + 0.5


def game_key_from_pred(pred: Dict, dt_short: str) -> Optional[str]:
    """Build the Kalshi game key portion from a Fuku prediction.
    e.g., '26MAR02BOSMIL' for Boston @ Milwaukee on 2026-03-02."""
    away = TEAM_ABBR.get(pred.get("away_team", ""), "")
    home = TEAM_ABBR.get(pred.get("home_team", ""), "")
    if not away or not home:
        return None
    return f"{dt_short}{away}{home}"


def match_pred_to_events(pred: Dict, events: List[Dict]) -> Optional[str]:
    """Match a Fuku prediction to a Kalshi event by fuzzy team name matching.
    Returns the event_ticker's game key portion (e.g., '26MAR02ISUARIZ').
    Works for CBB where we don't have a fixed abbreviation map."""
    away = pred.get("away_team", "").lower()
    home = pred.get("home_team", "").lower()
    if not away or not home:
        return None

    # Build match terms from team names
    # Handle abbreviations: "NC State" → also match "north carolina"
    EXPAND = {
        "nc": "north carolina", "sc": "south carolina",
        "utrgv": "rio grande", "umes": "maryland-eastern",
        "etamu": "east texas", "tamucc": "corpus christi",
        "sfa": "stephen", "hcu": "houston christian",
        "nau": "northern arizona", "ewu": "eastern washington",
    }
    away_terms = [w for w in away.replace("-", " ").split() if len(w) > 2]
    home_terms = [w for w in home.replace("-", " ").split() if len(w) > 2]
    # Add expanded abbreviations
    for abbr, expansion in EXPAND.items():
        if abbr in away.lower().split():
            away_terms.extend(expansion.split())
        if abbr in home.lower().split():
            home_terms.extend(expansion.split())

    for e in events:
        title = e.get("title", "").lower()
        eticker = e.get("event_ticker", "")

        # Check if both teams appear in the event title
        away_match = any(t in title for t in away_terms)
        home_match = any(t in title for t in home_terms)
        if away_match and home_match:
            # Extract game key: everything after the series prefix + first dash
            # e.g., KXNCAAMBSPREAD-26MAR02ISUARIZ → 26MAR02ISUARIZ
            parts = eticker.split("-", 1)
            return parts[1] if len(parts) > 1 else None

    return None


def build_game_view(pred: Dict, markets_by_type: Dict[str, List[Dict]],
                    game_key: str, sport: str) -> Optional[Dict]:
    """Build a single game's view with main lines and edges."""
    sigma_s = SPORT_STD[sport]["spread"]
    sigma_t = SPORT_STD[sport]["total"]

    fuku_spread = pred.get("fuku_spread")  # negative = away favored
    fuku_total = pred.get("fuku_total")
    away = pred.get("away_team", "?")
    home = pred.get("home_team", "?")
    game_time = pred.get("game_time", "")
    # CBB team name shortener: "Iowa State" → "Iowa St", "NC State" → "NC State"
    def _short(name: str) -> str:
        """Short display name for a team."""
        # Known short names
        shorts = {
            "Arizona": "Arizona", "Duke": "Duke", "Iowa State": "Iowa St",
            "NC State": "NC State", "Howard": "Howard", "Idaho": "Idaho",
            "Montana": "Montana", "Montana State": "Montana St",
            "McNeese State": "McNeese", "Nicholls State": "Nicholls",
            "Northern Colorado": "N. Colorado", "Northern Arizona": "N. Arizona",
            "Portland State": "Portland St", "Sacramento State": "Sac State",
            "Weber State": "Weber St", "Idaho State": "Idaho St",
            "Cleveland State": "Cleveland St", "IU Indy": "IU Indy",
            "Delaware State": "Delaware St", "South Carolina State": "SC State",
            "Norfolk State": "Norfolk St", "Morgan State": "Morgan St",
            "Coppin State": "Coppin St", "Stephen F. Austin": "SFA",
            "Incarnate Word": "UIW", "Lamar": "Lamar",
            "Houston Christian": "HCU", "New Orleans": "New Orleans",
            "Southeastern Louisiana": "SE Louisiana",
            "East Texas A&M": "East Texas A&M",
            "Texas A&M-Corpus Christi": "TAMUCC",
            "Northwestern State": "NW State",
            "Texas-Rio Grande Valley": "UTRGV",
            "Maryland-Eastern Shore": "UMES",
            "North Carolina Central": "NC Central",
            "Eastern Washington": "E. Washington",
        }
        return shorts.get(name, name.split()[-1][:6])

    away_abbr = TEAM_ABBR.get(away, _short(away))
    home_abbr = TEAM_ABBR.get(home, _short(home))

    # Determine favorite using projected scores (most reliable across sports)
    away_score = pred.get("projected_away_score")
    home_score = pred.get("projected_home_score")

    if away_score is not None and home_score is not None:
        margin = abs(float(away_score) - float(home_score))
        if float(away_score) > float(home_score):
            fav_team, fav_abbr = away, away_abbr
            dog_team, dog_abbr = home, home_abbr
        else:
            fav_team, fav_abbr = home, home_abbr
            dog_team, dog_abbr = away, away_abbr
    elif fuku_spread is not None and fuku_spread != 0:
        # Fallback: NBA uses negative=away fav, CBB uses positive=away fav
        # Use absolute value and spread_pick field if available
        margin = abs(fuku_spread)
        spread_pick = pred.get("spread_pick", "")
        if spread_pick:
            # e.g., "NC State +9.5" → NC State is dog, other team is fav
            dog_in_pick = spread_pick.split("+")[0].strip() if "+" in spread_pick else ""
            if dog_in_pick and (dog_in_pick.lower() in away.lower()):
                fav_team, fav_abbr = home, home_abbr
                dog_team, dog_abbr = away, away_abbr
            else:
                fav_team, fav_abbr = away, away_abbr
                dog_team, dog_abbr = home, home_abbr
        elif fuku_spread < 0:  # NBA convention
            fav_team, fav_abbr = away, away_abbr
            dog_team, dog_abbr = home, home_abbr
        else:
            fav_team, fav_abbr = home, home_abbr
            dog_team, dog_abbr = away, away_abbr
    else:
        fav_team, fav_abbr = away, away_abbr
        dog_team, dog_abbr = home, home_abbr
        margin = 0

    view = {
        "away": away, "home": home, "away_abbr": away_abbr, "home_abbr": home_abbr,
        "game_time": game_time, "sport": sport,
        "fuku_spread": fuku_spread, "fuku_total": fuku_total,
        "fav": fav_team, "fav_abbr": fav_abbr,
        "dog": dog_team, "dog_abbr": dog_abbr,
        "margin": margin,
        "lines": {},
    }

    # --- Helper: evaluate a spread contract ---
    def eval_spread(mkt: Dict) -> Optional[Dict]:
        parsed = parse_spread_ticker(mkt["ticker"])
        if not parsed:
            return None
        mkt_team, line = parsed
        yes_ask = int(mkt.get("yes_ask", mkt.get("yes_price", 50)))
        vol = mkt.get("volume", 0)

        if mkt_team.upper() == fav_abbr.upper():
            model_prob = ncdf((margin - line) / sigma_s) * 100
        else:
            model_prob = ncdf((-margin - line) / sigma_s) * 100

        edge_yes = model_prob - yes_ask
        edge_no = (100 - model_prob) - (100 - yes_ask)

        if edge_yes >= edge_no:
            rec_team_abbr = mkt_team
            is_fav = mkt_team.upper() == fav_abbr.upper()
            rec_label = f"{rec_team_abbr} -{line}" if is_fav else f"{rec_team_abbr} +{line}"
            return {"ticker": mkt["ticker"], "label": rec_label, "side": "yes",
                    "price": yes_ask, "model_pct": round(model_prob, 1),
                    "edge": round(edge_yes, 1), "volume": vol}
        else:
            is_fav = mkt_team.upper() == fav_abbr.upper()
            opp_abbr = dog_abbr if is_fav else fav_abbr
            rec_label = f"{opp_abbr} +{line}" if is_fav else f"{opp_abbr} -{line}"
            return {"ticker": mkt["ticker"], "label": rec_label, "side": "no",
                    "price": 100 - yes_ask, "model_pct": round(100 - model_prob, 1),
                    "edge": round(edge_no, 1), "volume": vol}

    # --- Helper: evaluate a total contract ---
    def eval_total(mkt: Dict) -> Optional[Dict]:
        total_line = parse_total_ticker(mkt["ticker"])
        if not total_line:
            return None
        yes_ask = int(mkt.get("yes_ask", mkt.get("yes_price", 50)))
        vol = mkt.get("volume", 0)

        model_over = ncdf((fuku_total - total_line) / sigma_t) * 100
        edge_over = model_over - yes_ask
        edge_under = (100 - model_over) - (100 - yes_ask)

        if edge_over >= edge_under:
            return {"ticker": mkt["ticker"], "label": f"Over {total_line}", "side": "yes",
                    "price": yes_ask, "model_pct": round(model_over, 1),
                    "edge": round(edge_over, 1), "volume": vol}
        else:
            return {"ticker": mkt["ticker"], "label": f"Under {total_line}", "side": "no",
                    "price": 100 - yes_ask, "model_pct": round(100 - model_over, 1),
                    "edge": round(edge_under, 1), "volume": vol}

    # --- Helper: pick 3 tiers from evaluated contracts ---
    def pick_tiers(evaluated: List[Dict]) -> Tuple[Optional[Dict], Optional[Dict], Optional[Dict]]:
        """Returns (safe, main, risky) — 3 tiers of the same market type.
        safe  = highest edge (our model's sweet spot, lower payout)
        main  = closest to 50¢ (market consensus)
        risky = cheapest price with positive edge (longshot, highest payout)
        """
        if not evaluated:
            return None, None, None
        positive = [e for e in evaluated if e["edge"] > 0]
        if not positive:
            # Even main line might have negative edge — still show it
            main = min(evaluated, key=lambda x: abs(x["price"] - 50))
            return None, main, None

        main = min(positive, key=lambda x: abs(x["price"] - 50))
        safe = max(positive, key=lambda x: x["edge"])
        # Risky = contract near our model's prediction (cheaper than main, still has edge)
        # For spreads this means near fuku_spread; for totals near fuku_total
        risky_candidates = [e for e in positive if e["price"] < main["price"] - 3 and e["edge"] >= 3]
        if risky_candidates:
            # Pick the one closest to 50% model probability (≈ our predicted line)
            risky = min(risky_candidates, key=lambda x: abs(x["model_pct"] - 50))
        else:
            risky = None

        # Only include if meaningfully different from main
        if safe["ticker"] == main["ticker"] or safe["edge"] - main["edge"] < 2:
            safe = None
        if risky is None or risky["ticker"] == main["ticker"] or risky["price"] >= main["price"] - 3:
            risky = None
        # Don't show risky if it's the same as safe
        if risky and safe and risky["ticker"] == safe["ticker"]:
            risky = None

        return safe, main, risky

    # --- Spread: main line + safe + risky ---
    all_spreads = find_all_game_markets(markets_by_type.get("spread", []), game_key)
    if all_spreads and fuku_spread is not None:
        evaluated = [e for m in all_spreads if (e := eval_spread(m)) is not None]
        safe, main, risky = pick_tiers(evaluated)
        if main:
            view["lines"]["spread"] = main
        if safe:
            view["lines"]["spread_safe"] = safe
        if risky:
            view["lines"]["spread_risky"] = risky

    # --- Total: main line + safe + risky ---
    all_totals = find_all_game_markets(markets_by_type.get("total", []), game_key)
    if all_totals and fuku_total:
        evaluated = [e for m in all_totals if (e := eval_total(m)) is not None]
        safe, main, risky = pick_tiers(evaluated)
        if main:
            view["lines"]["total"] = main
        if safe:
            view["lines"]["total_safe"] = safe
        if risky:
            view["lines"]["total_risky"] = risky

    # --- Winner main line ---
    winner_markets = [m for m in markets_by_type.get("winner", []) if game_key in m.get("ticker", "")]
    if winner_markets and fuku_spread is not None:
        # Find the favorite's ML contract
        fav_market = None
        dog_market = None
        for wm in winner_markets:
            if fav_abbr in wm.get("ticker", ""):
                fav_market = wm
            elif dog_abbr in wm.get("ticker", ""):
                dog_market = wm

        # Model win probability for favorite
        model_fav_win = ncdf(margin / sigma_s) * 100

        # Check both sides for best edge
        best_winner = None
        if fav_market:
            fav_yes = int(fav_market.get("yes_ask", fav_market.get("yes_price", 50)))
            fav_edge = model_fav_win - fav_yes
            best_winner = {
                "ticker": fav_market["ticker"],
                "label": f"{fav_abbr} ML",
                "side": "yes",
                "price": fav_yes,
                "model_pct": round(model_fav_win, 1),
                "edge": round(fav_edge, 1),
                "volume": fav_market.get("volume", 0),
            }

        if dog_market:
            dog_yes = int(dog_market.get("yes_ask", dog_market.get("yes_price", 50)))
            model_dog_win = 100 - model_fav_win
            dog_edge = model_dog_win - dog_yes
            if best_winner is None or dog_edge > best_winner["edge"]:
                best_winner = {
                    "ticker": dog_market["ticker"],
                    "label": f"{dog_abbr} ML",
                    "side": "yes",
                    "price": dog_yes,
                    "model_pct": round(model_dog_win, 1),
                    "edge": round(dog_edge, 1),
                    "volume": dog_market.get("volume", 0),
                }

        if best_winner:
            view["lines"]["winner"] = best_winner

    return view if view["lines"] else None


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def payout_str(amount: float, price_cents: int) -> str:
    """$5 pays $X.XX"""
    if price_cents <= 0 or price_cents >= 100:
        return ""
    contracts = int(amount / (price_cents / 100))
    payout = contracts * 1.0
    return f"${amount:.0f} pays ${payout:.2f}"


def format_line(line: Dict, bet_amount: float = 5.0) -> str:
    """Format a single market line for chat."""
    price = line["price"]
    edge = line["edge"]
    model = line["model_pct"]
    label = line["label"]
    pays = payout_str(bet_amount, price)

    edge_icon = "🔥" if edge >= 20 else "✅" if edge >= 10 else "📊" if edge >= 5 else "➖"

    if edge >= 5:
        return f"• {label} at {price}¢ → {model:.0f}% model (+{edge:.0f}% edge {edge_icon}) — {pays}"
    elif edge > 0:
        return f"• {label} at {price}¢ → {model:.0f}% model (+{edge:.0f}% edge)"
    else:
        return f"• {label} at {price}¢ → {model:.0f}% model ({edge:+.0f}%, no edge)"


def format_alt_line(line: Dict, prefix: str, bet_amount: float = 5.0) -> str:
    """Format an alternative tier line (safe or risky)."""
    price = line["price"]
    edge = line["edge"]
    model = line["model_pct"]
    label = line["label"]
    pays = payout_str(bet_amount, price)
    return f"  {prefix} {label} at {price}¢ → {model:.0f}% model (+{edge:.0f}% edge) — {pays}"


def format_game(view: Dict, bet_amount: float = 5.0) -> str:
    """Format a full game for chat output."""
    away = view["away"]
    home = view["home"]
    time_str = view.get("game_time", "")

    spread_str = ""
    if view.get("margin") and view["margin"] > 0:
        spread_str = f"{view['fav_abbr']} -{view['margin']:.1f}"

    total_str = f"Total {view['fuku_total']:.1f}" if view.get("fuku_total") else ""

    parts = [x for x in [spread_str, total_str] if x]
    model_line = " | ".join(parts)

    lines_out = []
    for mtype in ("spread", "total", "winner"):
        if mtype in view["lines"]:
            lines_out.append(format_line(view["lines"][mtype], bet_amount))
            # Safe = higher confidence, lower payout
            safe_key = f"{mtype}_safe"
            if safe_key in view["lines"]:
                lines_out.append(format_alt_line(view["lines"][safe_key], "↳ 🔒 Safer:", bet_amount))
            # Risky = lower confidence, higher payout
            risky_key = f"{mtype}_risky"
            if risky_key in view["lines"]:
                lines_out.append(format_alt_line(view["lines"][risky_key], "↳ 🎰 Riskier:", bet_amount))

    sport_emoji = {"nba": "🏀", "cbb": "🏀", "nhl": "🏒", "soccer": "⚽"}.get(view.get("sport", ""), "🏀")
    header = f"{sport_emoji} {away} @ {home}"
    if time_str:
        header += f" — {time_str}"

    return f"{header}\n📊 Our model: {model_line}\n" + "\n".join(lines_out)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Kalshi Market Browser")
    parser.add_argument("--sport", default="nba", choices=list(SERIES.keys()) + ["soccer"])
    parser.add_argument("--date", help="YYYY-MM-DD (default today)")
    parser.add_argument("--game", help="Filter to games matching this text")
    parser.add_argument("--bet", type=float, default=5.0, help="Example bet amount for payout calc")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    dt = args.date or date.today().isoformat()
    # Short date for Kalshi ticker matching: 26MAR02
    from datetime import datetime as _dt
    d = _dt.strptime(dt, "%Y-%m-%d")
    dt_short = d.strftime("%y%b%d").upper()  # e.g., 26MAR02

    # Fetch data
    client = KalshiClient()
    if not client.is_configured():
        print("❌ Kalshi not configured. Add API key to .env")
        sys.exit(1)

    bal = client.get_balance()
    preds = fetch_predictions(args.sport, dt)
    markets = fetch_markets(client, args.sport)

    if not preds:
        print(f"No {args.sport.upper()} predictions for {dt}")
        client.close()
        return

    # For CBB/NHL/soccer (without fixed abbreviation maps), use event-based matching
    event_map: Dict[str, str] = {}  # pred key → game_key
    if args.sport in ("cbb", "nhl", "soccer"):
        # Fetch events from spread series to get game keys
        if args.sport == "soccer":
            # Fetch events from ALL soccer league spread series
            all_events = []
            for league, lseries in SOCCER_SERIES.items():
                spread_ticker = lseries.get("spread", "")
                if spread_ticker:
                    evts = client.get_events(limit=200, series_ticker=spread_ticker)
                    all_events.extend(evts)
            events = all_events
        else:
            series_ticker = SERIES.get(args.sport, {}).get("spread", "")
            events = client.get_events(limit=200, series_ticker=series_ticker) if series_ticker else []
        for pred in preds:
            gk = match_pred_to_events(pred, events)
            if gk:
                pk = f"{pred.get('away_team','')}@{pred.get('home_team','')}"
                event_map[pk] = gk

    # Build views
    views = []
    for pred in preds:
        pk = f"{pred.get('away_team','')}@{pred.get('home_team','')}"
        gk = event_map.get(pk) or game_key_from_pred(pred, dt_short)
        if not gk:
            continue
        if args.game and args.game.lower() not in json.dumps(pred).lower():
            continue
        view = build_game_view(pred, markets, gk, args.sport)
        if view:
            views.append(view)

    client.close()

    if args.json:
        print(json.dumps(views, indent=2))
        return

    # Chat output
    balance = bal.get("balance_dollars", 0) if bal.get("success") else 0
    print(f"💰 Balance: ${balance:.2f}\n")

    if not views:
        print(f"No Kalshi markets matched for {args.sport.upper()} on {dt}")
        return

    for i, v in enumerate(views):
        if i > 0:
            print()
        print(format_game(v, args.bet))

    # Summary
    all_edges = []
    for v in views:
        for lt, ld in v["lines"].items():
            if ld["edge"] >= 5:
                all_edges.append(ld)
    if all_edges:
        best = max(all_edges, key=lambda x: x["edge"])
        print(f"\n🏆 Best edge: {best['label']} (+{best['edge']:.0f}%)")


if __name__ == "__main__":
    main()
