#!/usr/bin/env python3
"""
Conversational Profile Builder — Users define their trading preferences through natural conversation.

Examples:
- "I only want home dogs getting 7+ points in conference games"  
- "Show me games where the favorite's best player is ranked 50+ spots higher in FPR"
- "I like overs when both teams are in the top 50 for pace"
- "Find me revenge games where the underdog lost by 15+ last time"
- "I want CBB unders in letdown spots after big wins"

The agent uses this to build/update user profiles that capture exactly what they care about.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# Profile Templates & Intent Recognition
# ---------------------------------------------------------------------------

@dataclass
class UserIntent:
    """Parsed user preferences from natural language."""
    sport_prefs: Dict[str, Any] = None
    situation_prefs: Dict[str, Any] = None  
    stat_filters: Dict[str, Any] = None
    player_filters: Dict[str, Any] = None
    market_prefs: Dict[str, Any] = None
    risk_prefs: Dict[str, Any] = None
    examples: List[str] = None

# Common patterns users express
INTENT_PATTERNS = {
    "home_dogs": [
        r"home\s+(dogs?|underdogs?)",
        r"home\s+teams?\s+(getting|catching)\s+points",
        r"dogs?\s+at\s+home",
    ],
    "road_favorites": [
        r"road\s+(favorites?|favs?)",
        r"away\s+teams?\s+laying\s+points",
        r"favorites?\s+on\s+the\s+road",
    ],
    "large_spread": [
        r"spreads?\s+(over|above|bigger than)\s+(\d+)",
        r"blowouts?",
        r"big\s+spreads?",
    ],
    "close_games": [
        r"close\s+games?",
        r"spreads?\s+(under|below)\s+(\d+)",
        r"tight\s+lines?",
        r"pick\s*'?em",
    ],
    "unders": [
        r"unders?",
        r"under\s+bets?",
        r"low\s+scoring",
        r"defensive\s+games?",
    ],
    "overs": [
        r"overs?", 
        r"over\s+bets?",
        r"high\s+scoring",
        r"fast\s+paced?",
    ],
    "player_mismatch": [
        r"player\s+(mismatch|advantage|gap)",
        r"best\s+player\s+(ranked|fpr)",
        r"star\s+player",
        r"key\s+player\s+(out|injured|missing)",
    ],
    "fpr_gap": [
        r"fpr\s+(gap|difference|mismatch)",
        r"ranked\s+(\d+)\s*\+?\s+(spots?|ranks?)\s+(higher|better)",
        r"team\s+(ranked|fpr)\s+#?(\d+)",
    ],
    "pace": [
        r"pace",
        r"tempo",
        r"fast\s+teams?",
        r"slow\s+teams?",
    ],
    "defense": [
        r"defensive?\s+(teams?|matchups?)",
        r"top\s+(\d+)\s+(defense|defensive)",
        r"good\s+defense",
    ],
    "conference": [
        r"conference\s+games?",
        r"in\s+conference",
        r"league\s+games?",
    ],
    "letdown": [
        r"letdown\s+(games?|spots?)",
        r"after\s+(big\s+)?wins?",
        r"emotional\s+letdown",
        r"hangover\s+games?",
    ],
    "revenge": [
        r"revenge\s+(games?|spots?)",
        r"rematches?",
        r"lost\s+last\s+time",
        r"rematch",
    ],
    "back_to_back": [
        r"back\s*to\s*back",
        r"b2b",
        r"second\s+game\s+in\s+\d+\s+(days?|nights?)",
        r"tired\s+teams?",
    ],
    "rest_advantage": [
        r"rest\s+(advantage|edge)",
        r"extra\s+rest",
        r"days?\s+off",
        r"fresh\s+teams?",
    ],
}

# Sport detection
SPORT_PATTERNS = {
    "cbb": [r"college\s+(basketball|ball)", r"cbb", r"ncaa\s+(basketball|ball)", r"march\s+madness"],
    "nba": [r"nba", r"pro\s+(basketball|ball)", r"professional\s+basketball"],
    "nhl": [r"nhl", r"hockey", r"ice\s+hockey"],
    "soccer": [r"soccer", r"football", r"epl", r"premier\s+league", r"champions\s+league", r"ucl", r"mls"],
}

# Numeric extraction
NUMERIC_PATTERNS = {
    "spread_threshold": r"(\d+)\+?\s*points?",
    "fpr_gap": r"(\d+)\+?\s*(spots?|ranks?)",
    "bet_amount": r"\$(\d+(?:\.\d{2})?)",
    "percentage": r"(\d+)%",
    "top_ranked": r"top\s+(\d+)",
}

def extract_user_intent(user_text: str) -> UserIntent:
    """Parse user preferences from natural language."""
    text = user_text.lower()
    intent = UserIntent()
    
    # Initialize containers
    intent.sport_prefs = {}
    intent.situation_prefs = {}
    intent.stat_filters = {}
    intent.player_filters = {}
    intent.market_prefs = {}
    intent.risk_prefs = {}
    intent.examples = []
    
    # Detect sports
    for sport, patterns in SPORT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                intent.sport_prefs[sport] = {"enabled": True, "weight": 1.5}
    
    # Default to CBB if no sport specified
    if not intent.sport_prefs:
        intent.sport_prefs["cbb"] = {"enabled": True, "weight": 1.0}
    
    # Detect situations
    for situation, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                if situation in ["unders", "overs"]:
                    intent.market_prefs["totals"] = True
                    intent.stat_filters["over_under_trends"] = {
                        "bias": "under" if situation == "unders" else "over",
                        "min_trend_games": 1
                    }
                elif situation == "player_mismatch":
                    intent.player_filters["fpr_matchup_check"] = True
                elif situation in ["home_dogs", "road_favorites", "large_spread", "close_games"]:
                    boost = 1.3 if situation in ["home_dogs", "revenge", "letdown"] else 1.0
                    intent.situation_prefs[situation] = {"enabled": True, "boost": boost}
                else:
                    intent.situation_prefs[situation] = {"enabled": True, "boost": 1.2}
    
    # Extract numeric thresholds
    spread_match = re.search(r"(\d+)\+?\s*points?", text)
    if spread_match:
        threshold = int(spread_match.group(1))
        if "over" in text or "above" in text or "bigger" in text:
            intent.stat_filters["min_spread"] = threshold
        elif "under" in text or "below" in text:
            intent.stat_filters["max_spread"] = threshold
    
    # FPR gaps - multiple patterns
    fpr_patterns = [
        r"(\d+)\+?\s*(spots?|ranks?)\s+(higher|better)",
        r"(\d+)\+?\s*fpr\s+(gap|difference|mismatch)",
        r"fpr\s+(gap|difference)\s+(\d+)\+?",
    ]
    for pattern in fpr_patterns:
        fpr_match = re.search(pattern, text)
        if fpr_match:
            gap = int(fpr_match.group(1) if fpr_match.group(1).isdigit() else fpr_match.group(2))
            intent.player_filters["min_player_fpr_gap"] = gap
            intent.stat_filters["min_fpr_gap"] = gap
            break
    
    # Top N rankings
    top_match = re.search(r"top\s+(\d+)", text)
    if top_match:
        top_n = int(top_match.group(1))
        if "defense" in text:
            intent.stat_filters["max_defense_rank"] = top_n
        elif "pace" in text or "tempo" in text:
            intent.stat_filters["max_pace_rank"] = top_n
    
    # Bet sizing - handle escaped dollar signs
    bet_patterns = [r"\$(\d+(?:\.\d{2})?)", r"(\d+)\s*dollars?", r"bet\s+(\d+)"]
    for pattern in bet_patterns:
        bet_match = re.search(pattern, text)
        if bet_match:
            amount = float(bet_match.group(1))
            intent.risk_prefs["bet_size_dollars"] = amount
            break
    
    # Market preferences
    if "spreads?" in text or "ats" in text:
        intent.market_prefs["spreads"] = True
    if "totals?" in text or "overs?" in text or "unders?" in text:
        intent.market_prefs["totals"] = True
    if "moneylines?" in text or "ml" in text or "straight up" in text:
        intent.market_prefs["moneylines"] = True
    if "props?" in text or "player props?" in text:
        intent.market_prefs["player_props"] = True
    
    return intent

def build_profile_from_intent(intent: UserIntent, base_profile: Dict = None) -> Dict:
    """Convert UserIntent to a full profile dict."""
    if base_profile is None:
        base_profile = {
            "name": "Custom Profile",
            "description": f"Built from user preferences on {datetime.now().strftime('%Y-%m-%d')}",
            "sports": {"cbb": {"enabled": True, "weight": 1.0}},
            "situations": {},
            "stats": {},
            "players": {"fpr_matchup_check": True, "injury_awareness": True},
            "market_types": {"spreads": True, "totals": True, "moneylines": True},
            "edge_requirements": {"global_min_edge": 5.0, "spread_min_edge": 10.0, "total_min_edge": 10.0},
            "risk": {"bet_size_dollars": 2.0, "max_daily_bets": 10},
            "presentation": {"show_model_reasoning": True, "show_player_data": True, "show_team_stats": True},
        }
    
    profile = base_profile.copy()
    
    # Apply intent to profile
    if intent.sport_prefs:
        profile["sports"] = intent.sport_prefs
    
    if intent.situation_prefs:
        profile["situations"].update(intent.situation_prefs)
    
    if intent.stat_filters:
        profile["stats"].update(intent.stat_filters)
    
    if intent.player_filters:
        profile["players"].update(intent.player_filters)
    
    if intent.market_prefs:
        # If user specified markets, disable others unless they mentioned them
        all_markets = ["spreads", "totals", "moneylines", "player_props", "btts"]
        for market in all_markets:
            if market in intent.market_prefs:
                profile["market_types"][market] = intent.market_prefs[market]
            elif len(intent.market_prefs) > 0:
                profile["market_types"][market] = False
    
    if intent.risk_prefs:
        profile["risk"].update(intent.risk_prefs)
    
    return profile

# ---------------------------------------------------------------------------
# Interactive Profile Building
# ---------------------------------------------------------------------------

def analyze_preferences(user_input: str) -> Dict[str, Any]:
    """Analyze user input and return structured feedback."""
    intent = extract_user_intent(user_input)
    profile = build_profile_from_intent(intent)
    
    analysis = {
        "understood": [],
        "profile_updates": profile,
        "clarifying_questions": [],
        "examples": [],
    }
    
    # What we understood
    if intent.sport_prefs:
        sports = list(intent.sport_prefs.keys())
        analysis["understood"].append(f"Sports: {', '.join(sports).upper()}")
    
    if intent.situation_prefs:
        situations = []
        for sit, config in intent.situation_prefs.items():
            boost_str = f" (×{config.get('boost', 1.0)})" if config.get('boost', 1.0) != 1.0 else ""
            situations.append(f"{sit.replace('_', ' ')}{boost_str}")
        analysis["understood"].append(f"Situations: {', '.join(situations)}")
    
    if intent.market_prefs:
        markets = [k for k, v in intent.market_prefs.items() if v]
        analysis["understood"].append(f"Markets: {', '.join(markets)}")
    
    if intent.player_filters:
        if intent.player_filters.get("min_player_fpr_gap"):
            gap = intent.player_filters["min_player_fpr_gap"]
            analysis["understood"].append(f"Player FPR gap: ≥{gap} ranks")
    
    if intent.stat_filters:
        filters = []
        for k, v in intent.stat_filters.items():
            if k == "min_fpr_gap":
                filters.append(f"Team FPR gap ≥{v}")
            elif k == "max_defense_rank":
                filters.append(f"Defense top {v}")
            elif k.startswith("min_spread"):
                filters.append(f"Spread ≥{v}")
            elif k.startswith("max_spread"):
                filters.append(f"Spread ≤{v}")
        if filters:
            analysis["understood"].append(f"Filters: {', '.join(filters)}")
    
    if intent.risk_prefs:
        if "bet_size_dollars" in intent.risk_prefs:
            amt = intent.risk_prefs["bet_size_dollars"]
            analysis["understood"].append(f"Bet size: ${amt}")
    
    # Generate clarifying questions
    if not intent.market_prefs:
        analysis["clarifying_questions"].append("Which bet types? (spreads, totals, moneylines, player props)")
    
    if not intent.risk_prefs.get("bet_size_dollars"):
        analysis["clarifying_questions"].append("How much per bet? (e.g., '$2', '$5')")
    
    # Examples of what this profile would find
    examples = []
    if "home_dogs" in intent.situation_prefs:
        examples.append("Duke @ Wake Forest, Wake +7.5 (home dog)")
    if "unders" in intent.stat_filters.get("over_under_trends", {}).get("bias", ""):
        examples.append("Virginia vs Syracuse Under 135.5 (defensive game)")
    if intent.player_filters.get("min_player_fpr_gap"):
        gap = intent.player_filters["min_player_fpr_gap"]
        examples.append(f"#1 FPR player vs #{gap}+ FPR player matchup")
    
    analysis["examples"] = examples
    
    return analysis

def refine_profile(current_profile: Dict, refinement: str) -> Dict:
    """Update an existing profile based on user refinement."""
    intent = extract_user_intent(refinement)
    
    # Apply incremental updates
    updated = current_profile.copy()
    
    if intent.situation_prefs:
        updated["situations"].update(intent.situation_prefs)
    
    if intent.stat_filters:
        updated["stats"].update(intent.stat_filters)
    
    # Handle exclusions (e.g., "exclude games over 10 points")
    if "exclude" in refinement.lower() or "not" in refinement.lower() or "don't want" in refinement.lower():
        spread_match = re.search(r"(over|above)\s+(\d+)", refinement)
        if spread_match:
            threshold = int(spread_match.group(2))
            updated["stats"]["max_spread"] = threshold
    
    return updated

# ---------------------------------------------------------------------------
# Profile Management
# ---------------------------------------------------------------------------

def save_user_profile(profile: Dict, name: str) -> str:
    """Save a profile with the given name."""
    profiles_dir = SCRIPT_DIR.parent / "config" / "profiles"
    profiles_dir.mkdir(exist_ok=True)
    
    # Clean filename
    filename = re.sub(r'[^\w\s-]', '', name.lower())
    filename = re.sub(r'[-\s]+', '-', filename)
    path = profiles_dir / f"{filename}.json"
    
    with open(path, "w") as f:
        json.dump(profile, f, indent=2)
    
    return str(path)

def load_user_profiles() -> List[Dict]:
    """Load all available profiles."""
    profiles_dir = SCRIPT_DIR.parent / "config" / "profiles"
    profiles = []
    
    if profiles_dir.exists():
        for path in sorted(profiles_dir.glob("*.json")):
            try:
                with open(path) as f:
                    profile = json.load(f)
                    profile["_filename"] = path.stem
                    profiles.append(profile)
            except Exception:
                pass
    
    return profiles

# ---------------------------------------------------------------------------
# Conversational Interface
# ---------------------------------------------------------------------------

def interactive_profile_builder():
    """Interactive CLI for building profiles."""
    print("🏗️  Kalshi Autopilot Profile Builder")
    print("   Tell me what you're looking for in trading opportunities...\n")
    
    examples = [
        "I want home dogs getting 7+ points in college basketball",
        "Show me CBB unders in letdown spots after big wins", 
        "I like NBA spreads when the best player has a 30+ FPR gap",
        "Find me soccer overs with both teams averaging 2+ goals",
        "I want $5 bets on close games (spreads under 3 points)",
    ]
    
    print("💡 Examples:")
    for ex in examples:
        print(f"   • {ex}")
    print()
    
    while True:
        user_input = input("What are you looking for? ").strip()
        if not user_input or user_input.lower() in ['quit', 'exit', 'done']:
            break
        
        analysis = analyze_preferences(user_input)
        
        print(f"\n✅ Here's what I understood:")
        for item in analysis["understood"]:
            print(f"   • {item}")
        
        if analysis["examples"]:
            print(f"\n💡 This would find:")
            for ex in analysis["examples"]:
                print(f"   • {ex}")
        
        if analysis["clarifying_questions"]:
            print(f"\n❓ To refine further:")
            for q in analysis["clarifying_questions"]:
                print(f"   • {q}")
        
        print(f"\nProfile preview:")
        print(json.dumps(analysis["profile_updates"], indent=2)[:500] + "...")
        
        save = input("\nSave this profile? (y/N): ").strip().lower()
        if save in ['y', 'yes']:
            name = input("Profile name: ").strip() or f"custom-{datetime.now().strftime('%m%d')}"
            path = save_user_profile(analysis["profile_updates"], name)
            print(f"✅ Saved to {path}")
            break
        
        refine = input("\nRefine further? (or 'done'): ").strip()
        if not refine or refine.lower() == 'done':
            break
        
        # Apply refinement
        updated = refine_profile(analysis["profile_updates"], refine)
        analysis["profile_updates"] = updated

def format_profile_summary(profile: Dict) -> str:
    """Format a profile as a human-readable summary."""
    lines = []
    
    name = profile.get("name", "Unnamed")
    desc = profile.get("description", "")
    lines.append(f"📋 {name}")
    if desc:
        lines.append(f"   {desc}")
    
    # Sports
    sports = [s.upper() for s, cfg in profile.get("sports", {}).items() if cfg.get("enabled")]
    if sports:
        lines.append(f"🏀 Sports: {', '.join(sports)}")
    
    # Situations  
    situations = []
    for sit, cfg in profile.get("situations", {}).items():
        if cfg.get("enabled"):
            boost = cfg.get("boost", 1.0)
            boost_str = f" (×{boost})" if boost != 1.0 else ""
            situations.append(f"{sit.replace('_', ' ')}{boost_str}")
    if situations:
        lines.append(f"🎯 Situations: {', '.join(situations)}")
    
    # Markets
    markets = [k for k, v in profile.get("market_types", {}).items() if v]
    if markets:
        lines.append(f"💰 Markets: {', '.join(markets)}")
    
    # Edge requirements
    edges = profile.get("edge_requirements", {})
    edge_parts = []
    for k, v in edges.items():
        if k != "global_min_edge":
            mtype = k.replace("_min_edge", "")
            edge_parts.append(f"{mtype} {v}%+")
    if edge_parts:
        lines.append(f"📈 Min edges: {', '.join(edge_parts)}")
    
    # Risk
    risk = profile.get("risk", {})
    risk_parts = []
    if "bet_size_dollars" in risk:
        risk_parts.append(f"${risk['bet_size_dollars']}/bet")
    if "max_daily_bets" in risk:
        risk_parts.append(f"max {risk['max_daily_bets']}/day")
    if risk_parts:
        lines.append(f"💵 Risk: {', '.join(risk_parts)}")
    
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# Main CLI
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Conversational Profile Builder")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--analyze", "-a", help="Analyze user input text")
    parser.add_argument("--list", "-l", action="store_true", help="List profiles")
    parser.add_argument("--show", "-s", help="Show profile details")
    args = parser.parse_args()
    
    if args.list:
        profiles = load_user_profiles()
        print("📋 Available Profiles:\n")
        for p in profiles:
            print(format_profile_summary(p))
            print()
        return
    
    if args.show:
        profiles = load_user_profiles()
        for p in profiles:
            if p.get("_filename") == args.show or p.get("name", "").lower() == args.show.lower():
                print(format_profile_summary(p))
                print(f"\nFull config:\n{json.dumps(p, indent=2)}")
                return
        print(f"Profile '{args.show}' not found")
        return
    
    if args.analyze:
        analysis = analyze_preferences(args.analyze)
        print("✅ Understood:")
        for item in analysis["understood"]:
            print(f"   • {item}")
        if analysis["examples"]:
            print("\n💡 Would find:")
            for ex in analysis["examples"]:
                print(f"   • {ex}")
        return
    
    if args.interactive:
        interactive_profile_builder()
        return
    
    # Default: show usage
    print("🏗️  Profile Builder — Define what you care about")
    print("\nUsage:")
    print("  python profile_builder.py --interactive    # Build a profile conversationally")  
    print("  python profile_builder.py --analyze 'text' # Test intent parsing")
    print("  python profile_builder.py --list           # Show all profiles")
    print("  python profile_builder.py --show name      # Show profile details")


if __name__ == "__main__":
    main()