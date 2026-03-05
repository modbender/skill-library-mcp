#!/usr/bin/env python3
"""
Kalshi Market Scanner

Scans Fuku predictions API for edges and matches them to Kalshi markets.
Calculates probability edges between our model and Kalshi prices.

Usage:
    python scanner.py                    # Scan all sports
    python scanner.py --sport cbb        # Scan CBB only
    python scanner.py --min-edge 3.0     # Filter by minimum edge
    python scanner.py --date 2024-01-15  # Specific date
"""

import os
import sys
import argparse
import json
import re
import math
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

try:
    import httpx
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install httpx python-dotenv")
    sys.exit(1)

from kalshi_client import KalshiClient

# Load environment variables
load_dotenv()

# Team name variations for matching across sports
TEAM_VARIATIONS = {
    # NBA teams
    "Atlanta Hawks": ["hawks", "atl", "atlanta"],
    "Boston Celtics": ["celtics", "bos", "boston"],
    "Brooklyn Nets": ["nets", "bkn", "brooklyn"],
    "Charlotte Hornets": ["hornets", "cha", "charlotte"],
    "Chicago Bulls": ["bulls", "chi", "chicago"],
    "Cleveland Cavaliers": ["cavaliers", "cavs", "cle", "cleveland"],
    "Dallas Mavericks": ["mavericks", "mavs", "dal", "dallas"],
    "Denver Nuggets": ["nuggets", "den", "denver"],
    "Detroit Pistons": ["pistons", "det", "detroit"],
    "Golden State Warriors": ["warriors", "gsw", "golden state"],
    "Houston Rockets": ["rockets", "hou", "houston"],
    "Indiana Pacers": ["pacers", "ind", "indiana"],
    "Los Angeles Clippers": ["clippers", "lac", "la clippers"],
    "Los Angeles Lakers": ["lakers", "lal", "la lakers"],
    "Memphis Grizzlies": ["grizzlies", "mem", "memphis"],
    "Miami Heat": ["heat", "mia", "miami"],
    "Milwaukee Bucks": ["bucks", "mil", "milwaukee"],
    "Minnesota Timberwolves": ["timberwolves", "wolves", "min", "minnesota"],
    "New Orleans Pelicans": ["pelicans", "nop", "new orleans"],
    "New York Knicks": ["knicks", "nyk", "new york"],
    "Oklahoma City Thunder": ["thunder", "okc", "oklahoma city"],
    "Orlando Magic": ["magic", "orl", "orlando"],
    "Philadelphia 76ers": ["76ers", "sixers", "phi", "philadelphia"],
    "Phoenix Suns": ["suns", "phx", "phoenix"],
    "Portland Trail Blazers": ["blazers", "trail blazers", "por", "portland"],
    "Sacramento Kings": ["kings", "sac", "sacramento"],
    "San Antonio Spurs": ["spurs", "sas", "san antonio"],
    "Toronto Raptors": ["raptors", "tor", "toronto"],
    "Utah Jazz": ["jazz", "uta", "utah"],
    "Washington Wizards": ["wizards", "was", "washington"],
    
    # Common CBB team names (add more as needed)
    "Duke Blue Devils": ["duke", "blue devils"],
    "North Carolina Tar Heels": ["unc", "north carolina", "tar heels"],
    "Kentucky Wildcats": ["kentucky", "wildcats", "uk"],
    "Kansas Jayhawks": ["kansas", "jayhawks", "ku"],
    "UCLA Bruins": ["ucla", "bruins"],
    "Michigan Wolverines": ["michigan", "wolverines"],
    "Arizona Wildcats": ["arizona", "wildcats"],
    "Louisville Cardinals": ["louisville", "cardinals"],
    "Syracuse Orange": ["syracuse", "orange"],
    "Georgetown Hoyas": ["georgetown", "hoyas"],
    
    # NHL teams
    "Boston Bruins": ["bruins", "bos", "boston"],
    "New York Rangers": ["rangers", "nyr", "ny rangers"],
    "Toronto Maple Leafs": ["maple leafs", "leafs", "tor", "toronto"],
    "Tampa Bay Lightning": ["lightning", "tbl", "tampa bay", "tampa"],
    "Colorado Avalanche": ["avalanche", "avs", "col", "colorado"],
    "Vegas Golden Knights": ["golden knights", "vgk", "vegas"],
    "Carolina Hurricanes": ["hurricanes", "canes", "car", "carolina"],
    "Pittsburgh Penguins": ["penguins", "pens", "pit", "pittsburgh"],
    "Washington Capitals": ["capitals", "caps", "was", "washington"],
    "Philadelphia Flyers": ["flyers", "phi", "philadelphia"],
}

# Build reverse lookup
TEAM_LOOKUP = {}
for full_name, variations in TEAM_VARIATIONS.items():
    TEAM_LOOKUP[full_name.lower()] = full_name
    for var in variations:
        TEAM_LOOKUP[var.lower()] = full_name

# Kalshi market patterns by sport
KALSHI_PATTERNS = {
    "nba": ["KXNBA", "NBASINGLEGAME", "KXNBAGAME", "KXNBASPREAD", "KXNBATOTAL", "KXPROBBALL"],
    "cbb": ["KXCBB", "CBBSINGLEGAME", "KXCBBGAME", "KXCBBSPREAD", "KXCBBTOTAL", "BASKETBALL", "MARCHMADNESS"],
    "nhl": ["KXNHL", "NHLSINGLEGAME", "KXNHLGAME", "KXNHLSPREAD", "KXNHLTOTAL", "HOCKEY"],
    "soccer": ["KXSOCCER", "KXFOOTBALL", "SOCCERGAME", "FOOTBALLGAME", "UEFA", "FIFA", "PREMIER", "CHAMPIONS"],
}

# Sport-specific standard deviations for margin of victory (empirically derived)
# Used for converting point edges → probability edges via normal distribution
SPORT_STD_DEVS = {
    "cbb":    {"spread": 12.0, "total": 11.0},   # College basketball
    "nba":    {"spread": 11.0, "total": 10.5},   # Pro basketball
    "nhl":    {"spread":  1.5, "total":  1.3},   # Hockey (goals)
    "soccer": {"spread":  1.2, "total":  1.1},   # Soccer (goals)
}

def normal_cdf(x: float) -> float:
    """Standard normal CDF using the complementary error function (no scipy needed)."""
    return 0.5 * math.erfc(-x / math.sqrt(2))

def point_edge_to_probability(edge_points: float, sport: str, market_type: str) -> float:
    """
    Convert a point spread/total edge to a probability edge using normal distribution.
    
    For spreads: If our model says Team A -9.5 and Kalshi contract asks "Team A wins by 10+?",
    we calculate P(margin > 10) using our predicted margin as the mean and sport-specific std dev.
    
    Returns probability edge as percentage (e.g., 6.3 means 6.3% edge).
    """
    std_devs = SPORT_STD_DEVS.get(sport, SPORT_STD_DEVS["cbb"])
    sigma = std_devs.get(market_type, std_devs.get("spread", 12.0))
    
    # The edge in standard deviations
    z = edge_points / sigma
    
    # CDF gives us the probability shift
    # For a 1-point edge in CBB (sigma=12): z=0.083, probability shift ≈ 3.3%
    # For a 3-point edge in CBB: z=0.25, probability shift ≈ 9.9%
    prob_edge = normal_cdf(z) - 0.5  # Shift from 50% baseline
    
    return prob_edge * 100  # Return as percentage

@dataclass
class Prediction:
    """Fuku prediction data."""
    sport: str
    home_team: str
    away_team: str
    game_time: str
    fuku_spread: Optional[float] = None
    book_spread: Optional[float] = None
    fuku_total: Optional[float] = None
    book_total: Optional[float] = None
    spread_edge: Optional[float] = None
    total_edge: Optional[float] = None

@dataclass 
class PlayerPrediction:
    """Fuku player prediction data for prop matching."""
    sport: str
    player_name: str
    team_name: str
    stat_type: str      # "points", "rebounds", "assists", "threes", etc.
    predicted_value: float
    fpr_rank: Optional[int] = None
    minutes: Optional[float] = None

@dataclass
class OpportunityMatch:
    """Matched opportunity between Fuku prediction and Kalshi market."""
    prediction: Prediction
    kalshi_market: Dict
    market_type: str  # "spread", "total", "game_winner"
    edge_type: str    # "spread", "total"
    edge_points: float
    edge_probability: float
    recommended_side: str  # "yes" or "no"
    recommended_price: float
    confidence: float  # 0-1 matching confidence

class FukuAPI:
    """Client for Fuku predictions API."""
    
    BASE_URL = "https://cbb-predictions-api-nzpk.onrender.com"
    
    def __init__(self):
        self.debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
    
    def _debug_log(self, message: str):
        if self.debug:
            print(f"[FUKU] {message}")
    
    def get_predictions(self, sport: str, game_date: str) -> List[Prediction]:
        """Fetch predictions for a sport and date."""
        endpoint = f"/api/public/{sport}/predictions"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.BASE_URL}{endpoint}",
                    params={"date": game_date}
                )
                
                if response.status_code != 200:
                    self._debug_log(f"API error {response.status_code} for {sport}")
                    return []
                
                data = response.json()
                predictions = []
                
                # Handle different response structures
                games_data = data
                if isinstance(data, dict):
                    games_data = data.get("predictions", data.get("games", []))
                
                for game in games_data:
                    try:
                        pred = Prediction(
                            sport=sport,
                            home_team=game.get("home_team", ""),
                            away_team=game.get("away_team", ""),
                            game_time=game.get("game_time", ""),
                            fuku_spread=game.get("fuku_spread"),
                            book_spread=game.get("book_spread"),
                            fuku_total=game.get("fuku_total"),
                            book_total=game.get("book_total"),
                        )
                        
                        # Calculate edges
                        if pred.fuku_spread is not None and pred.book_spread is not None:
                            pred.spread_edge = abs(pred.fuku_spread - pred.book_spread)
                        
                        if pred.fuku_total is not None and pred.book_total is not None:
                            pred.total_edge = abs(pred.fuku_total - pred.book_total)
                        
                        predictions.append(pred)
                    except Exception as e:
                        self._debug_log(f"Error parsing game: {e}")
                        continue
                
                self._debug_log(f"Fetched {len(predictions)} {sport} predictions")
                return predictions
                
        except Exception as e:
            print(f"❌ Failed to fetch {sport} predictions: {e}")
            return []

    def get_player_data(self, sport: str, team: str) -> List[PlayerPrediction]:
        """Fetch player data for prop matching."""
        if sport not in ("cbb", "nba"):
            return []  # Player props mainly available for basketball
        
        endpoint = f"/api/public/{sport}/players"
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(
                    f"{self.BASE_URL}{endpoint}",
                    params={"team": team, "limit": 10}
                )
                
                if response.status_code != 200:
                    return []
                
                data = response.json()
                players_data = data if isinstance(data, list) else data.get("players", [])
                
                players = []
                for p in players_data:
                    name = p.get("player_name", p.get("name", ""))
                    if not name:
                        continue
                    
                    # Create predictions for each stat type the player has
                    stat_map = {
                        "points": p.get("ppg", p.get("pts_per_game")),
                        "rebounds": p.get("rpg", p.get("reb_per_game")),
                        "assists": p.get("apg", p.get("ast_per_game")),
                        "threes": p.get("tpg", p.get("three_pm_per_game")),
                    }
                    
                    for stat_type, value in stat_map.items():
                        if value and float(value) > 0:
                            players.append(PlayerPrediction(
                                sport=sport,
                                player_name=name,
                                team_name=team,
                                stat_type=stat_type,
                                predicted_value=float(value),
                                fpr_rank=p.get("fpr_rank"),
                                minutes=p.get("minutes", p.get("mpg")),
                            ))
                
                self._debug_log(f"Fetched {len(players)} player predictions for {team}")
                return players
                
        except Exception as e:
            self._debug_log(f"Error fetching players for {team}: {e}")
            return []


class KalshiMatcher:
    """Matches Fuku predictions to Kalshi markets."""
    
    def __init__(self, kalshi_client: KalshiClient):
        self.client = kalshi_client
        self.debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
    
    def _debug_log(self, message: str):
        if self.debug:
            print(f"[MATCHER] {message}")
    
    def _normalize_team_name(self, text: str) -> Optional[str]:
        """Normalize team name using lookup table."""
        text_lower = text.lower()
        
        for variation, full_name in TEAM_LOOKUP.items():
            if variation in text_lower:
                return full_name
        
        # Try exact match on full names
        for full_name in TEAM_VARIATIONS.keys():
            if full_name.lower() in text_lower:
                return full_name
        
        return None
    
    def _extract_line_from_market(self, title: str, subtitle: str = "") -> Optional[float]:
        """Extract spread/total line from Kalshi market text."""
        text = f"{title} {subtitle}".lower()
        
        # Look for number patterns
        patterns = [
            r'([+-]?\d+\.?\d*)\s*(?:points?|pts?|goals?)?',
            r'(?:over|under|o|u)\s*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*(?:or more|or less|plus)',
            r'by\s*([+-]?\d+\.?\d*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    return float(match)
                except ValueError:
                    continue
        
        return None
    
    def _detect_market_type(self, title: str, subtitle: str, ticker: str) -> str:
        """Detect Kalshi market type."""
        text = f"{title} {subtitle}".lower()
        ticker_upper = ticker.upper()
        
        # Ticker-based detection (most reliable)
        if any(x in ticker_upper for x in ["SPREAD", "GAME"]):
            return "spread"
        elif any(x in ticker_upper for x in ["TOTAL", "OVER", "UNDER"]):
            return "total"
        elif "WINNER" in ticker_upper:
            return "game_winner"
        
        # Text-based fallback
        if any(x in text for x in ["winner", "win", "beat"]):
            return "game_winner"
        elif any(x in text for x in ["total", "over", "under", "combined"]):
            return "total"
        elif any(x in text for x in ["spread", "by", "cover"]):
            return "spread"
        
        return "unknown"
    
    def _convert_edge_to_probability(self, edge_points: float, market_type: str, sport: str = "cbb") -> float:
        """
        Convert point edge to probability edge using normal distribution.
        
        Uses sport-specific standard deviations for accurate conversion.
        Example: 2-point CBB spread edge (σ=12) → ~6.6% probability edge
        Example: 0.3-goal soccer edge (σ=1.2) → ~9.9% probability edge
        """
        return point_edge_to_probability(edge_points, sport, market_type)
    
    def find_matches(self, predictions: List[Prediction], 
                     player_predictions: Optional[List[PlayerPrediction]] = None) -> List[OpportunityMatch]:
        """Find Kalshi markets matching our predictions (game-level and player props)."""
        matches = []
        
        if not self.client.is_configured():
            print("❌ Kalshi client not configured")
            return matches
        
        # Get relevant Kalshi markets
        all_markets = []
        
        # Try sport-specific series
        for prediction in predictions:
            sport_patterns = KALSHI_PATTERNS.get(prediction.sport, [])
            for pattern in sport_patterns:
                markets = self.client.get_markets(limit=100, series_ticker=pattern)
                all_markets.extend(markets)
                self._debug_log(f"Found {len(markets)} markets for series {pattern}")
        
        # If no sport-specific markets, try general search
        if not all_markets:
            self._debug_log("No sport-specific markets found, trying general search")
            all_markets = self.client.get_markets(limit=200, status="open")
        
        self._debug_log(f"Total markets to search: {len(all_markets)}")
        
        # Match game-level predictions to markets
        for prediction in predictions:
            pred_matches = self._match_prediction_to_markets(prediction, all_markets)
            matches.extend(pred_matches)
        
        # Match player props to markets
        if player_predictions:
            prop_matches = self._match_player_props(player_predictions, all_markets)
            matches.extend(prop_matches)
        
        return matches
    
    def _match_player_props(self, players: List[PlayerPrediction], markets: List[Dict]) -> List[OpportunityMatch]:
        """Match player predictions to Kalshi player prop markets."""
        matches = []
        
        PROP_KEYWORDS = {
            "points": ["points", "pts", "score"],
            "rebounds": ["rebounds", "reb", "boards"],
            "assists": ["assists", "ast", "dimes"],
            "threes": ["3-pointers", "threes", "3pm", "three pointers", "3pt"],
        }
        
        for player in players:
            name_parts = player.player_name.lower().split()
            if len(name_parts) < 2:
                continue
            
            keywords = PROP_KEYWORDS.get(player.stat_type, [])
            
            for market in markets:
                title = market.get("title", "").lower()
                subtitle = market.get("subtitle", "").lower()
                combined = f"{title} {subtitle}"
                
                # Check if player name matches (at least last name + first initial or full name)
                name_match = all(part in combined for part in name_parts)
                if not name_match:
                    # Try last name + first initial
                    last_name = name_parts[-1]
                    first_initial = name_parts[0][0] if name_parts[0] else ""
                    name_match = last_name in combined and first_initial in combined
                
                if not name_match:
                    continue
                
                # Check if stat type matches
                stat_match = any(kw in combined for kw in keywords)
                if not stat_match:
                    continue
                
                # Extract the line from the market
                line = self._extract_line_from_market(title, subtitle)
                if line is None:
                    continue
                
                # Calculate edge: our predicted value vs Kalshi line
                edge = player.predicted_value - line
                
                # Only flag if there's meaningful edge (>10% of line)
                if abs(edge) < line * 0.05:
                    continue
                
                # Convert to probability edge
                # For player props, use ~15% of predicted value as std dev
                prop_sigma = max(player.predicted_value * 0.3, 2.0)
                z = edge / prop_sigma
                prob_edge = (normal_cdf(z) - 0.5) * 100
                
                if abs(prob_edge) < 2.0:  # Minimum 2% probability edge
                    continue
                
                # Determine side: over (yes) or under (no)
                recommended_side = "yes" if edge > 0 else "no"
                
                # Build a pseudo-prediction for the match object
                pseudo_pred = Prediction(
                    sport=player.sport,
                    home_team=player.team_name,
                    away_team=f"[{player.player_name} {player.stat_type}]",
                    game_time="",
                    spread_edge=abs(edge),
                )
                
                match = OpportunityMatch(
                    prediction=pseudo_pred,
                    kalshi_market=market,
                    market_type="player_prop",
                    edge_type=f"prop_{player.stat_type}",
                    edge_points=abs(edge),
                    edge_probability=abs(prob_edge),
                    recommended_side=recommended_side,
                    recommended_price=50 + (abs(prob_edge) / 2),
                    confidence=0.65 if player.fpr_rank and player.fpr_rank < 100 else 0.5
                )
                matches.append(match)
                self._debug_log(f"Player prop match: {player.player_name} {player.stat_type} "
                              f"pred={player.predicted_value:.1f} line={line} edge={edge:.1f}")
        
        return matches
    
    def _match_prediction_to_markets(self, prediction: Prediction, markets: List[Dict]) -> List[OpportunityMatch]:
        """Match a single prediction to Kalshi markets."""
        matches = []
        
        # Get team variations for matching
        home_variations = TEAM_VARIATIONS.get(prediction.home_team, [prediction.home_team.lower()])
        away_variations = TEAM_VARIATIONS.get(prediction.away_team, [prediction.away_team.lower()])
        
        for market in markets:
            title = market.get("title", "")
            subtitle = market.get("subtitle", "")
            ticker = market.get("ticker", "")
            combined_text = f"{title} {subtitle}".lower()
            
            # Check team matching
            home_match = any(var in combined_text for var in home_variations)
            away_match = any(var in combined_text for var in away_variations)
            
            if not (home_match or away_match):
                continue
            
            # Detect market type
            market_type = self._detect_market_type(title, subtitle, ticker)
            kalshi_line = self._extract_line_from_market(title, subtitle)
            
            # Check for spread edge
            if (market_type in ["spread", "game_winner"] and 
                prediction.spread_edge is not None and 
                prediction.spread_edge >= 1.0):  # Minimum 1-point edge
                
                edge_prob = self._convert_edge_to_probability(prediction.spread_edge, "spread", prediction.sport)
                
                # Determine recommended side
                if prediction.fuku_spread and prediction.book_spread:
                    if prediction.fuku_spread < prediction.book_spread:
                        # Model thinks home team will win by less than book
                        recommended_side = "no" if home_match else "yes"
                    else:
                        # Model thinks home team will win by more than book
                        recommended_side = "yes" if home_match else "no"
                else:
                    recommended_side = "yes"  # Default
                
                match = OpportunityMatch(
                    prediction=prediction,
                    kalshi_market=market,
                    market_type=market_type,
                    edge_type="spread",
                    edge_points=prediction.spread_edge,
                    edge_probability=edge_prob,
                    recommended_side=recommended_side,
                    recommended_price=50 + (edge_prob / 2),  # Rough pricing
                    confidence=0.8 if home_match and away_match else 0.6
                )
                matches.append(match)
            
            # Check for total edge
            if (market_type == "total" and 
                prediction.total_edge is not None and 
                prediction.total_edge >= 2.0):  # Minimum 2-point edge
                
                edge_prob = self._convert_edge_to_probability(prediction.total_edge, "total", prediction.sport)
                
                # Determine recommended side
                if prediction.fuku_total and prediction.book_total:
                    if prediction.fuku_total < prediction.book_total:
                        recommended_side = "no"  # Under
                    else:
                        recommended_side = "yes"  # Over
                else:
                    recommended_side = "yes"  # Default
                
                match = OpportunityMatch(
                    prediction=prediction,
                    kalshi_market=market,
                    market_type=market_type,
                    edge_type="total",
                    edge_points=prediction.total_edge,
                    edge_probability=edge_prob,
                    recommended_side=recommended_side,
                    recommended_price=50 + (edge_prob / 2),  # Rough pricing
                    confidence=0.7
                )
                matches.append(match)
        
        return matches

def format_opportunity(opp: OpportunityMatch) -> str:
    """Format opportunity for display."""
    pred = opp.prediction
    market = opp.kalshi_market
    
    game = f"{pred.away_team} @ {pred.home_team}"
    ticker = market.get("ticker", "")
    title = market.get("title", "")[:60]
    yes_price = market.get("yes_price", market.get("yes_ask", 50))
    
    edge_str = f"{opp.edge_points:.1f}pt"
    if opp.edge_probability:
        edge_str += f" ({opp.edge_probability:.1f}%)"
    
    side_price = yes_price if opp.recommended_side == "yes" else (100 - yes_price)
    
    return f"""
🎯 {game} ({pred.sport.upper()})
   Market: {ticker} - {title}
   Edge: {edge_str} {opp.edge_type}
   Rec: {opp.recommended_side.upper()} @ {side_price:.0f}¢
   Confidence: {opp.confidence:.0%}
"""

def main():
    """Scanner CLI interface."""
    parser = argparse.ArgumentParser(description="Kalshi Market Scanner")
    parser.add_argument("--sport", choices=["cbb", "nba", "nhl", "soccer"], 
                       help="Specific sport to scan")
    parser.add_argument("--date", help="Date to scan (YYYY-MM-DD, default today)")
    parser.add_argument("--min-edge", type=float, default=2.0,
                       help="Minimum point edge threshold")
    parser.add_argument("--output", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Setup
    scan_date = args.date or date.today().isoformat()
    sports = [args.sport] if args.sport else ["cbb", "nba", "nhl", "soccer"]
    
    print(f"🔍 Scanning for edges on {scan_date}")
    print(f"   Sports: {', '.join(sports)}")
    print(f"   Min Edge: {args.min_edge} points")
    print("-" * 60)
    
    # Fetch predictions
    fuku_api = FukuAPI()
    all_predictions = []
    
    for sport in sports:
        predictions = fuku_api.get_predictions(sport, scan_date)
        # Filter by edge threshold
        filtered = [p for p in predictions 
                   if (p.spread_edge and p.spread_edge >= args.min_edge) or
                      (p.total_edge and p.total_edge >= args.min_edge)]
        all_predictions.extend(filtered)
        print(f"📊 {sport.upper()}: {len(filtered)} games with {args.min_edge}+ point edges")
    
    if not all_predictions:
        print("❌ No predictions found with sufficient edge")
        return
    
    # Fetch player data for prop matching
    all_players = []
    for pred in all_predictions:
        if pred.sport in ("cbb", "nba"):
            for team in [pred.home_team, pred.away_team]:
                players = fuku_api.get_player_data(pred.sport, team)
                all_players.extend(players)
    
    if all_players:
        print(f"🏀 Loaded {len(all_players)} player stat lines for prop matching")
    
    # Match to Kalshi markets
    kalshi_client = KalshiClient()
    matcher = KalshiMatcher(kalshi_client)
    
    print(f"\n🔄 Matching {len(all_predictions)} predictions to Kalshi markets...")
    matches = matcher.find_matches(all_predictions, all_players if all_players else None)
    
    # Display results
    if matches:
        print(f"\n✅ Found {len(matches)} opportunities:")
        for opp in sorted(matches, key=lambda x: x.edge_probability, reverse=True):
            print(format_opportunity(opp))
        
        # Save to file if requested
        if args.output:
            output_data = []
            for opp in matches:
                output_data.append({
                    "sport": opp.prediction.sport,
                    "game": f"{opp.prediction.away_team} @ {opp.prediction.home_team}",
                    "kalshi_ticker": opp.kalshi_market.get("ticker"),
                    "market_type": opp.market_type,
                    "edge_type": opp.edge_type,
                    "edge_points": opp.edge_points,
                    "edge_probability": opp.edge_probability,
                    "recommended_side": opp.recommended_side,
                    "recommended_price": opp.recommended_price,
                    "confidence": opp.confidence,
                    "market_title": opp.kalshi_market.get("title"),
                    "current_yes_price": opp.kalshi_market.get("yes_price", 50),
                })
            
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Results saved to {args.output}")
    
    else:
        print("❌ No Kalshi markets found matching our predictions")

if __name__ == "__main__":
    main()