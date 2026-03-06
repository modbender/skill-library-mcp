#!/usr/bin/env python3
"""
Profile Engine — scores opportunities against user preferences.

Takes raw opportunities from browse.py/autopilot.py and applies the user's
profile to filter, boost, and enrich them with the data they care about.
"""

import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import httpx

SCRIPT_DIR = Path(__file__).parent
FUKU_BASE = "https://cbb-predictions-api-nzpk.onrender.com"


# ---------------------------------------------------------------------------
# Profile loading
# ---------------------------------------------------------------------------

def load_profile(name: str = "default") -> dict:
    """Load a named profile from config/profiles/."""
    profiles_dir = SCRIPT_DIR.parent / "config" / "profiles"
    path = profiles_dir / f"{name}.json"
    if not path.exists():
        # Try exact path
        path = Path(name)
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {name}")
    with open(path) as f:
        return json.load(f)


def list_profiles() -> List[dict]:
    """List available profiles with name + description."""
    profiles_dir = SCRIPT_DIR.parent / "config" / "profiles"
    results = []
    if profiles_dir.exists():
        for p in sorted(profiles_dir.glob("*.json")):
            try:
                with open(p) as f:
                    data = json.load(f)
                results.append({
                    "file": p.stem,
                    "name": data.get("name", p.stem),
                    "description": data.get("description", ""),
                })
            except Exception:
                pass
    return results


# ---------------------------------------------------------------------------
# Data enrichment — fetch team/player stats the profile cares about
# ---------------------------------------------------------------------------

@dataclass
class TeamData:
    name: str
    overall_rank: int = 0
    offense_rank: int = 0
    defense_rank: int = 0
    overall_score: float = 0.0
    categories: dict = field(default_factory=dict)
    top_players: list = field(default_factory=list)


def fetch_team_data(team_name: str, sport: str) -> Optional[TeamData]:
    """Fetch FPR and stats for a team from the Fuku API."""
    try:
        if sport == "cbb":
            # Rankings endpoint
            r = httpx.get(f"{FUKU_BASE}/api/public/cbb/rankings", params={"limit": 400}, timeout=10)
            rankings = r.json() if isinstance(r.json(), list) else r.json().get("rankings", [])
            for t in rankings:
                if t.get("team_name", "").lower() == team_name.lower():
                    return TeamData(
                        name=team_name,
                        overall_rank=t.get("overall_rank", 0),
                        offense_rank=t.get("offense_rank", 0),
                        defense_rank=t.get("defense_rank", 0),
                        overall_score=t.get("overall_score", 0),
                        categories=t.get("categories", {}),
                    )
        elif sport == "nba":
            r = httpx.get(f"{FUKU_BASE}/api/nba/teams", timeout=10)
            teams = r.json() if isinstance(r.json(), list) else r.json().get("teams", [])
            for t in teams:
                if t.get("team_name", "").lower() == team_name.lower():
                    return TeamData(
                        name=team_name,
                        overall_rank=t.get("overall_rank", 0),
                        offense_rank=t.get("offense_rank", 0),
                        defense_rank=t.get("defense_rank", 0),
                    )
    except Exception:
        pass
    return None


def fetch_top_players(team_name: str, sport: str, limit: int = 3) -> list:
    """Fetch top players by FPR rank for a team."""
    try:
        if sport == "cbb":
            r = httpx.get(f"{FUKU_BASE}/api/public/cbb/players",
                         params={"team": team_name, "limit": limit}, timeout=10)
            data = r.json()
            players = data if isinstance(data, list) else data.get("players", [])
            return [{
                "name": p.get("name", ""),
                "fpr_rank": p.get("stats", {}).get("fpr_rank", 0),
                "position": p.get("position", ""),
                "scoring_rank": p.get("stats", {}).get("scoring_rank"),
                "bpr": p.get("stats", {}).get("bpr"),
            } for p in players]
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# Opportunity scoring
# ---------------------------------------------------------------------------

@dataclass
class ScoredOpportunity:
    """An opportunity enriched with profile-based scoring."""
    # From browse.py
    sport: str
    game: str
    ticker: str
    title: str
    side: str
    price: int
    edge: float
    model_prob: float
    contracts: int
    cost: float
    payout: float
    view_text: str = ""
    
    # Profile scoring
    raw_edge: float = 0.0
    situation_boost: float = 1.0
    profile_score: float = 0.0
    reasons: list = field(default_factory=list)
    
    # Enrichment
    home_team_data: Optional[dict] = None
    away_team_data: Optional[dict] = None
    home_players: list = field(default_factory=list)
    away_players: list = field(default_factory=list)
    situational_factors: list = field(default_factory=list)


def detect_situations(pred: dict) -> Dict[str, bool]:
    """Detect which situational factors apply to a game prediction."""
    situations = {}
    
    sit = pred.get("situational", {})
    factors = sit.get("factors", [])
    factor_codes = {f.get("code", ""): f for f in factors}
    
    # Map Fuku factor codes to profile situation keys
    code_to_situation = {
        "picking_home_fav": "home_dogs",  # inverted — if picking home fav, it's NOT a home dog
        "picking_road_dog": "road_favorites",  # inverted
        "is_monday": "monday_games",
        "large_spread": "large_spread",
        "tiny_edge": "close_spread",
        "medium_spread": None,
        "big_edge": None,
    }
    
    # Spread-based detection
    spread = pred.get("fuku_spread", 0)
    home_score = pred.get("projected_home_score", 0)
    away_score = pred.get("projected_away_score", 0)
    
    # Home dog: home team has lower projected score but market line is close
    if home_score and away_score:
        if home_score < away_score:
            situations["home_dogs"] = True
            situations["road_favorites"] = True
        
    # Close spread
    if abs(spread) <= 3:
        situations["close_spread"] = True
    
    # Large spread
    if abs(spread) > 10:
        situations["large_spread"] = True
    
    # Monday games
    if "is_monday" in factor_codes:
        situations["monday_games"] = True
    
    # Conference games (from factor codes)
    if "conference" in factor_codes:
        situations["conference_games"] = True
    
    return situations


def score_opportunity(opp: dict, pred: dict, profile: dict) -> Optional[ScoredOpportunity]:
    """Score an opportunity against a user profile. Returns None if filtered out."""
    sport = opp.get("sport", "")
    
    # Check sport enabled
    sport_config = profile.get("sports", {}).get(sport, {})
    if not sport_config.get("enabled", True):
        return None
    
    # Check soccer league filter
    if sport == "soccer" and "leagues" in sport_config:
        league = pred.get("league", "")
        if league and league not in sport_config["leagues"]:
            return None
    
    # Check market type
    market_types = profile.get("market_types", {})
    title = opp.get("title", "").lower()
    ticker = opp.get("ticker", "").lower()
    
    is_spread = "spread" in ticker or "wins by" in title
    is_total = "total" in ticker
    is_ml = "winner" in title or "game" in ticker.split("-")[0] if ticker else False
    
    if is_spread and not market_types.get("spreads", True):
        return None
    if is_total and not market_types.get("totals", True):
        return None
    if is_ml and not market_types.get("moneylines", True):
        return None
    
    # Check edge thresholds
    edge = opp.get("edge", 0)
    edge_reqs = profile.get("edge_requirements", {})
    global_min = edge_reqs.get("global_min_edge", 5.0)
    
    if edge < global_min:
        return None
    
    if is_spread and edge < edge_reqs.get("spread_min_edge", 10.0):
        return None
    if is_total and edge < edge_reqs.get("total_min_edge", 10.0):
        return None
    if is_ml and edge < edge_reqs.get("ml_min_edge", 15.0):
        return None
    
    # Detect situations
    situations = detect_situations(pred)
    
    # Calculate situation boost
    sit_prefs = profile.get("situations", {})
    boost = 1.0
    reasons = []
    
    # Check if any required situations are missing
    for sit_key, sit_config in sit_prefs.items():
        if isinstance(sit_config, dict) and sit_config.get("require", False):
            if not situations.get(sit_key, False):
                return None  # Required situation not present
    
    # Apply boosts
    for sit_key, is_present in situations.items():
        if is_present and sit_key in sit_prefs:
            sit_config = sit_prefs[sit_key]
            if isinstance(sit_config, dict) and sit_config.get("enabled", False):
                sit_boost = sit_config.get("boost", 1.0)
                boost *= sit_boost
                reasons.append(f"{sit_key.replace('_', ' ').title()} (×{sit_boost})")
    
    # Sport weight
    sport_weight = sport_config.get("weight", 1.0)
    
    # Stats filters
    stats = profile.get("stats", {})
    
    # FPR gap check
    min_fpr_gap = stats.get("min_fpr_gap", 0)
    if min_fpr_gap > 0:
        # We'd need team data here — for now, use spread as proxy
        spread = abs(pred.get("fuku_spread", 0))
        estimated_gap = spread * 8  # rough: 1 point ≈ 8 FPR ranks
        if estimated_gap < min_fpr_gap:
            return None
    
    # Calculate final score
    profile_score = edge * boost * sport_weight
    
    scored = ScoredOpportunity(
        sport=sport,
        game=opp.get("game", ""),
        ticker=opp.get("ticker", ""),
        title=opp.get("title", ""),
        side=opp.get("side", "yes"),
        price=opp.get("price", 50),
        edge=edge,
        model_prob=opp.get("model_prob", 50),
        contracts=opp.get("contracts", 0),
        cost=opp.get("cost", 0),
        payout=opp.get("payout", 0),
        view_text=opp.get("view_text", ""),
        raw_edge=edge,
        situation_boost=boost,
        profile_score=profile_score,
        reasons=reasons,
        situational_factors=pred.get("situational", {}).get("factors", []),
    )
    
    return scored


def enrich_opportunity(scored: ScoredOpportunity, pred: dict, profile: dict) -> ScoredOpportunity:
    """Fetch additional team/player data based on profile preferences."""
    pres = profile.get("presentation", {})
    players_config = profile.get("players", {})
    
    home = pred.get("home_team", "")
    away = pred.get("away_team", "")
    sport = scored.sport
    
    # Team stats
    if pres.get("show_team_stats", True):
        home_data = fetch_team_data(home, sport)
        away_data = fetch_team_data(away, sport)
        if home_data:
            scored.home_team_data = {
                "name": home_data.name,
                "fpr_rank": home_data.overall_rank,
                "off_rank": home_data.offense_rank,
                "def_rank": home_data.defense_rank,
            }
        if away_data:
            scored.away_team_data = {
                "name": away_data.name,
                "fpr_rank": away_data.overall_rank,
                "off_rank": away_data.offense_rank,
                "def_rank": away_data.defense_rank,
            }
    
    # Player data
    if pres.get("show_player_data", True) or players_config.get("fpr_matchup_check", False):
        scored.home_players = fetch_top_players(home, sport)
        scored.away_players = fetch_top_players(away, sport)
        
        # Player FPR gap check
        if players_config.get("fpr_matchup_check") and scored.home_players and scored.away_players:
            home_best = min(p.get("fpr_rank", 999) for p in scored.home_players if p.get("fpr_rank"))
            away_best = min(p.get("fpr_rank", 999) for p in scored.away_players if p.get("fpr_rank"))
            gap = abs(home_best - away_best)
            min_gap = players_config.get("min_player_fpr_gap", 0)
            if gap >= min_gap and min_gap > 0:
                scored.reasons.append(f"Player FPR gap: {gap} ranks")
    
    return scored


# ---------------------------------------------------------------------------
# Formatted output
# ---------------------------------------------------------------------------

def format_scored_opportunity(scored: ScoredOpportunity, profile: dict, rank: int = 1) -> str:
    """Format a scored opportunity for the user."""
    pres = profile.get("presentation", {})
    lines = []
    
    # Header
    emoji = {"cbb": "🏀", "nba": "🏀", "nhl": "🏒", "soccer": "⚽"}.get(scored.sport, "🏀")
    edge_icon = "🔥" if scored.edge >= 20 else "✅" if scored.edge >= 10 else "📊"
    
    lines.append(f"{rank}. {emoji} {scored.game} ({scored.sport.upper()}) — {edge_icon} +{scored.edge:.0f}% edge")
    lines.append(f"   {scored.title}")
    lines.append(f"   {scored.contracts} contracts @ {scored.price}¢ = ${scored.cost:.2f} → ${scored.payout:.2f}")
    
    # Profile score
    if scored.situation_boost != 1.0:
        lines.append(f"   📈 Profile score: {scored.profile_score:.1f} (edge {scored.raw_edge:.0f}% × boost {scored.situation_boost:.1f}×)")
    
    # Reasons
    if scored.reasons:
        lines.append(f"   💡 {', '.join(scored.reasons)}")
    
    # Team stats
    if pres.get("show_team_stats") and (scored.home_team_data or scored.away_team_data):
        stats_parts = []
        if scored.away_team_data:
            d = scored.away_team_data
            stats_parts.append(f"{d['name']} FPR #{d['fpr_rank']} (Off #{d['off_rank']}, Def #{d['def_rank']})")
        if scored.home_team_data:
            d = scored.home_team_data
            stats_parts.append(f"{d['name']} FPR #{d['fpr_rank']} (Off #{d['off_rank']}, Def #{d['def_rank']})")
        if stats_parts:
            lines.append(f"   📊 {' vs '.join(stats_parts)}")
    
    # Players
    if pres.get("show_player_data") and (scored.home_players or scored.away_players):
        player_parts = []
        for p in (scored.away_players + scored.home_players)[:4]:
            if p.get("fpr_rank"):
                player_parts.append(f"{p['name']} (FPR #{p['fpr_rank']})")
        if player_parts:
            lines.append(f"   🏅 {', '.join(player_parts)}")
    
    # Situational factors
    if pres.get("show_model_reasoning") and scored.situational_factors:
        factor_strs = [f.get("name", "") for f in scored.situational_factors[:3]]
        if factor_strs:
            lines.append(f"   🎯 Factors: {', '.join(factor_strs)}")
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main — score and rank opportunities against a profile
# ---------------------------------------------------------------------------

def apply_profile(opportunities: list, predictions: list, profile: dict,
                  enrich: bool = True) -> List[ScoredOpportunity]:
    """
    Score, filter, and rank opportunities against a profile.
    
    Args:
        opportunities: raw opps from autopilot.py scan
        predictions: raw Fuku predictions (for situational data)
        profile: loaded profile dict
        enrich: whether to fetch team/player data (slower but richer)
    
    Returns:
        Sorted list of ScoredOpportunity objects
    """
    # Build prediction lookup by game key
    pred_lookup = {}
    for p in predictions:
        key = f"{p.get('away_team', '')}@{p.get('home_team', '')}"
        pred_lookup[key] = p
        # Also index by just team names for flexible matching
        for team in [p.get("away_team", ""), p.get("home_team", "")]:
            if team:
                pred_lookup[team.lower()] = p
    
    scored = []
    for opp in opportunities:
        # Find matching prediction
        game = opp.get("game", "")
        pred = pred_lookup.get(game) or pred_lookup.get(game.replace(" @ ", "@"))
        
        # Fallback: match by team name substring
        if not pred:
            for team_name in game.split(" @ "):
                pred = pred_lookup.get(team_name.strip().lower())
                if pred:
                    break
        
        if not pred:
            pred = {}  # Use empty pred, still score on edge alone
        
        result = score_opportunity(opp, pred, profile)
        if result:
            if enrich:
                result = enrich_opportunity(result, pred, profile)
            scored.append(result)
    
    # Sort by profile score descending
    scored.sort(key=lambda s: s.profile_score, reverse=True)
    
    # Cap at max
    max_opps = profile.get("presentation", {}).get("max_opportunities", 5)
    return scored[:max_opps]


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Profile Engine — score opportunities against user preferences")
    parser.add_argument("--profile", default="default", help="Profile name or path")
    parser.add_argument("--list", action="store_true", help="List available profiles")
    parser.add_argument("--test", action="store_true", help="Run a test scan with the profile")
    parser.add_argument("--date", help="Date (YYYY-MM-DD)")
    parser.add_argument("--no-enrich", action="store_true", help="Skip team/player data fetch")
    args = parser.parse_args()
    
    if args.list:
        profiles = list_profiles()
        print("📋 Available profiles:\n")
        for p in profiles:
            print(f"  {p['file']}: {p['name']}")
            print(f"    {p['description']}\n")
        return
    
    if args.test:
        from datetime import date as dt_mod
        from autopilot import scan_all_sports, load_config, get_balance_dollars
        from kalshi_client import KalshiClient
        
        profile = load_profile(args.profile)
        config = load_config()
        scan_date = args.date or dt_mod.today().isoformat()
        
        print(f"🔍 Testing profile: {profile.get('name', args.profile)}")
        print(f"   {profile.get('description', '')}\n")
        
        client = KalshiClient()
        balance = get_balance_dollars(client)
        
        # Override config sports from profile
        config["sports"] = [s for s, cfg in profile.get("sports", {}).items() if cfg.get("enabled", True)]
        
        opps = scan_all_sports(config, client, scan_date)
        
        # Fetch predictions for enrichment
        all_preds = []
        for sport in config["sports"]:
            from browse import fetch_predictions
            preds = fetch_predictions(sport, scan_date)
            all_preds.extend(preds)
        
        scored = apply_profile(opps, all_preds, profile, enrich=not args.no_enrich)
        
        if not scored:
            print("❌ No opportunities match this profile")
        else:
            print(f"💰 Balance: ${balance:.2f} | {len(scored)} opportunities match\n")
            for i, s in enumerate(scored, 1):
                print(format_scored_opportunity(s, profile, i))
                print()
        
        client.close()
        return
    
    # Default: just show profile info
    profile = load_profile(args.profile)
    print(json.dumps(profile, indent=2))


if __name__ == "__main__":
    main()
