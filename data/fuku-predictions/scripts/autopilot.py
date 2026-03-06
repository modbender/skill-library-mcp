#!/usr/bin/env python3
"""
Kalshi Autopilot — Autonomous edge scanner and trader.

Designed to run via OpenClaw cron job. Scans all configured sports for edges,
applies risk limits, and either trades automatically or outputs recommendations
for the agent to relay to the user.

Modes:
  --dry-run     Log opportunities, don't trade (default)
  --approve     Output recommendations for agent to present to user
  --auto        Trade autonomously within risk limits

Output is plain text designed to be injected into an OpenClaw session as a
system event or agent turn message.
"""

import json
import os
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field

# Add script dir to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from kalshi_client import KalshiClient
from browse import (
    fetch_predictions, fetch_markets, match_pred_to_events,
    build_game_view, format_game, SERIES, SOCCER_SERIES,
)
from profile_engine import apply_profile, load_profile, format_scored_opportunity


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load config, falling back to defaults."""
    config_path = SCRIPT_DIR.parent / "config" / "config.json"
    default_path = SCRIPT_DIR.parent / "config" / "default-config.json"
    
    path = config_path if config_path.exists() else default_path
    with open(path) as f:
        return json.load(f)


def check_kill_switch() -> bool:
    """Check if kill switch file exists."""
    return (SCRIPT_DIR.parent / "KILL_SWITCH").exists()


def get_balance_dollars(client: KalshiClient) -> float:
    """Get balance as a float in dollars."""
    bal = client.get_balance()
    if isinstance(bal, dict):
        return bal.get("balance_dollars", 0.0)
    return float(bal)


def check_risk_limits_profile(risk_config: dict, balance: float) -> Optional[str]:
    """Check risk limits based on profile config."""
    today = todays_trades()
    
    # Max daily bets
    max_bets = risk_config.get("max_daily_bets", 10)
    if len(today) >= max_bets:
        return f"Daily bet limit reached ({max_bets})"
    
    # Max daily loss
    max_loss = risk_config.get("max_daily_loss_dollars", 10.0)
    daily_loss = sum(t.get("cost", 0) for t in today if t.get("status") == "placed")
    if daily_loss >= max_loss:
        return f"Daily loss limit reached (${daily_loss:.2f} / ${max_loss:.2f})"
    
    return None


def build_config_from_profile(profile: dict) -> dict:
    """Build a legacy config dict from a profile for compatibility with scan_all_sports."""
    sports_config = profile.get("sports", {})
    enabled_sports = [s for s, cfg in sports_config.items() if cfg.get("enabled", True)]
    
    return {
        "sports": enabled_sports,
        "min_edge_pct": profile.get("edge_requirements", {}).get("global_min_edge", 5.0),
        "sizing": {"method": "flat_amount", "flat_amount": profile.get("risk", {}).get("bet_size_dollars", 2.0)},
    }


# ---------------------------------------------------------------------------
# Trade log
# ---------------------------------------------------------------------------

TRADES_PATH = SCRIPT_DIR.parent / "trades.json"

def load_trades() -> list:
    if not TRADES_PATH.exists():
        return []
    with open(TRADES_PATH) as f:
        return json.load(f)

def save_trade(trade: dict):
    trades = load_trades()
    trades.append(trade)
    with open(TRADES_PATH, "w") as f:
        json.dump(trades, f, indent=2)


def todays_trades() -> list:
    today = date.today().isoformat()
    return [t for t in load_trades() if t.get("timestamp", "").startswith(today)]


# ---------------------------------------------------------------------------
# Risk checks
# ---------------------------------------------------------------------------

def check_risk_limits(config: dict, balance: float) -> Optional[str]:
    """Return a reason string if risk limits are breached, else None."""
    risk = config.get("risk", {})
    
    today = todays_trades()
    
    # Max daily bets
    max_bets = risk.get("max_daily_bets", 15)
    if len(today) >= max_bets:
        return f"Daily bet limit reached ({max_bets})"
    
    # Max daily loss
    max_loss_pct = risk.get("max_daily_loss_pct", 10.0)
    daily_pnl = sum(t.get("amount", 0) for t in today if t.get("status") == "placed")
    if balance > 0 and daily_pnl / balance * 100 > max_loss_pct:
        return f"Daily loss limit breached ({max_loss_pct}%)"
    
    return None


# ---------------------------------------------------------------------------
# Scanning
# ---------------------------------------------------------------------------

def scan_all_sports(config: dict, client: KalshiClient, dt: str) -> List[dict]:
    """
    Scan all configured sports.  Returns a list of opportunity dicts:
    {
        sport, game, ticker, title, side, price, edge, model_prob,
        contracts, cost, payout, view_text
    }
    """
    sports = config.get("sports", ["cbb", "nba", "nhl", "soccer"])
    min_edge = config.get("min_edge_pct", 3.0)
    opportunities: List[dict] = []
    
    dt_date = datetime.strptime(dt, "%Y-%m-%d")
    dt_short = dt_date.strftime("%y").upper() + dt_date.strftime("%b").upper()[:3] + dt_date.strftime("%d")

    for sport in sports:
        preds = fetch_predictions(sport, dt)
        if not preds:
            continue
        
        markets = fetch_markets(client, sport)
        
        # Event-based matching for CBB/NHL/soccer
        event_map: Dict[str, str] = {}
        if sport in ("cbb", "nhl", "soccer"):
            if sport == "soccer":
                all_events = []
                for league, lseries in SOCCER_SERIES.items():
                    spread_ticker = lseries.get("spread", "")
                    if spread_ticker:
                        evts = client.get_events(limit=200, series_ticker=spread_ticker)
                        all_events.extend(evts)
                events = all_events
            else:
                series_ticker = SERIES.get(sport, {}).get("spread", "")
                events = client.get_events(limit=200, series_ticker=series_ticker) if series_ticker else []
            
            for pred in preds:
                gk = match_pred_to_events(pred, events)
                if gk:
                    pk = f"{pred.get('away_team','')}@{pred.get('home_team','')}"
                    event_map[pk] = gk
        
        for pred in preds:
            pk = f"{pred.get('away_team','')}@{pred.get('home_team','')}"
            from browse import game_key_from_pred
            gk = event_map.get(pk) or game_key_from_pred(pred, dt_short)
            if not gk:
                continue
            
            view = build_game_view(pred, markets, gk, sport)
            if not view:
                continue
            
            # Extract best opportunities from the view's lines
            for key, line in view.get("lines", {}).items():
                if "_safe" in key or "_risky" in key:
                    continue  # Only consider main lines for autopilot
                edge = line.get("edge", 0)
                if edge < min_edge:
                    continue
                
                price = line.get("price", 50)
                model_prob = line.get("model_prob", 50)
                ticker = line.get("ticker", "")
                title = line.get("title", "")
                side = "yes"  # browse.py already picks the correct side
                
                # Position sizing
                balance = get_balance_dollars(client)
                sizing = config.get("sizing", {})
                method = sizing.get("method", "flat_amount")
                
                if method == "flat_amount":
                    cost = min(sizing.get("flat_amount", 5.0), balance * 0.05)
                elif method == "flat_pct":
                    cost = balance * (sizing.get("flat_pct", 2.0) / 100)
                elif method == "kelly":
                    # Quarter Kelly: f = (p*b - q) / b * fraction
                    p = model_prob / 100
                    q = 1 - p
                    b = (100 / price) - 1  # odds ratio
                    if b > 0:
                        kelly = ((p * b - q) / b) * sizing.get("kelly_fraction", 0.25)
                        cost = max(0, kelly * balance)
                    else:
                        cost = 0
                else:
                    cost = 5.0
                
                cost = round(cost, 2)
                if cost < 1.0:
                    continue  # Not worth it
                
                contracts = int(cost / (price / 100))
                if contracts < 1:
                    continue
                
                actual_cost = round(contracts * (price / 100), 2)
                payout = round(contracts * 1.0, 2)
                
                game = f"{view['away']} @ {view['home']}"
                
                opportunities.append({
                    "sport": sport,
                    "game": game,
                    "ticker": ticker,
                    "title": title,
                    "side": side,
                    "price": price,
                    "edge": edge,
                    "model_prob": model_prob,
                    "contracts": contracts,
                    "cost": actual_cost,
                    "payout": payout,
                    "view_text": format_game(view),
                })
    
    # Sort by edge descending
    opportunities.sort(key=lambda x: x["edge"], reverse=True)
    return opportunities


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def execute_trade(client: KalshiClient, scored) -> dict:
    """Place an order and return the trade record."""
    trade = {
        "timestamp": datetime.now().isoformat(),
        "sport": scored.sport,
        "game": scored.game,
        "ticker": scored.ticker,
        "title": scored.title,
        "side": scored.side,
        "contracts": scored.contracts,
        "price": scored.price,
        "cost": scored.cost,
        "payout": scored.payout,
        "edge": scored.edge,
        "model_prob": scored.model_prob,
        "status": "pending",
    }
    
    try:
        result = client.place_order(
            ticker=scored.ticker,
            side=scored.side,
            action="buy",
            count=scored.contracts,
            order_type="limit",
            yes_price=scored.price,
        )
        
        if result.get("success"):
            trade["order_id"] = result.get("order_id")
            trade["status"] = "placed"
        else:
            trade["status"] = "failed"
            trade["error"] = result.get("error", "Unknown error")
    except Exception as e:
        trade["status"] = "failed"
        trade["error"] = str(e)
    
    save_trade(trade)
    return trade


# ---------------------------------------------------------------------------
# Output formatting (for cron → agent message)
# ---------------------------------------------------------------------------

def format_scan_summary(opportunities: list, mode: str, balance: float, profile: dict, trades: list = None) -> str:
    """Format scan results as a message for the agent/user."""
    lines = []
    now = datetime.now().strftime("%I:%M %p")
    profile_name = profile.get("name", "Custom Profile")
    
    if not opportunities:
        return f"🔍 Kalshi scan ({now}): No opportunities match '{profile_name}' profile. Balance: ${balance:.2f}"
    
    lines.append(f"🔍 Kalshi Autopilot Scan — {now}")
    lines.append(f"📋 Profile: {profile_name}")
    lines.append(f"💰 Balance: ${balance:.2f} | Found {len(opportunities)} matching opportunities\n")
    
    if mode == "auto" and trades:
        # Show what was traded
        placed = [t for t in trades if t["status"] == "placed"]
        failed = [t for t in trades if t["status"] == "failed"]
        
        if placed:
            lines.append(f"✅ **Placed {len(placed)} trades:**")
            for t in placed:
                lines.append(f"  • {t['game']} — {t['title'][:50]}")
                lines.append(f"    {t['contracts']} contracts @ {t['price']}¢ = ${t['cost']:.2f} → ${t['payout']:.2f} if YES")
                lines.append(f"    Edge: +{t['edge']:.0f}% | Order: {t.get('order_id', '?')}")
        if failed:
            lines.append(f"\n❌ {len(failed)} trades failed:")
            for t in failed:
                lines.append(f"  • {t['game']}: {t.get('error', '?')}")
    
    elif mode == "approve":
        # Show recommendations with profile context
        lines.append("📋 **Top opportunities matching your profile:**\n")
        for i, scored in enumerate(opportunities[:5], 1):
            lines.append(format_scored_opportunity(scored, profile, i))
            lines.append("")
        
        lines.append("Reply with numbers to approve (e.g., '1 3 5') or 'pass' to skip all.")
    
    elif mode == "dry_run":
        lines.append("🔍 **Profile-matched opportunities:**\n")
        for i, scored in enumerate(opportunities[:5], 1):
            lines.append(format_scored_opportunity(scored, profile, i))
            lines.append("")
        
        total_cost = sum(getattr(s, 'cost', 0) for s in opportunities[:5])
        lines.append(f"Total: {len(opportunities)} opportunities | Would risk: ${total_cost:.2f}")
    
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Kalshi Autopilot Scanner")
    parser.add_argument("--mode", default="dry_run", choices=["dry_run", "approve", "auto"],
                       help="Operating mode")
    parser.add_argument("--profile", default="default", help="Profile name or path")
    parser.add_argument("--date", help="Date to scan (YYYY-MM-DD)")
    parser.add_argument("--max-trades", type=int, default=5, help="Max trades per scan")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()
    
    # Kill switch
    if check_kill_switch():
        print("🛑 KILL SWITCH ACTIVE — autopilot halted")
        sys.exit(0)
    
    try:
        profile = load_profile(args.profile)
    except FileNotFoundError:
        print(f"❌ Profile '{args.profile}' not found")
        sys.exit(1)
    
    dt = args.date or date.today().isoformat()
    
    client = KalshiClient()
    if not client.is_configured():
        print("❌ Kalshi not configured")
        sys.exit(1)
    
    balance = get_balance_dollars(client)
    
    # Risk check using profile settings
    risk_config = profile.get("risk", {})
    risk_msg = check_risk_limits_profile(risk_config, balance)
    if risk_msg:
        print(f"⚠️ {risk_msg}")
        sys.exit(0)
    
    # Build config from profile for scanning
    config = build_config_from_profile(profile)
    
    # Scan using legacy function, then apply profile scoring
    raw_opportunities = scan_all_sports(config, client, dt)
    
    # Fetch predictions for profile analysis
    all_predictions = []
    for sport in config["sports"]:
        preds = fetch_predictions(sport, dt)
        all_predictions.extend(preds)
    
    # Apply profile scoring and filtering
    opportunities = apply_profile(raw_opportunities, all_predictions, profile)
    
    # Cap at max trades
    opportunities = opportunities[:args.max_trades]
    
    if args.json:
        print(json.dumps({"balance": balance, "opportunities": opportunities}, indent=2))
        client.close()
        return
    
    # Execute based on mode
    trades = []
    if args.mode == "auto" and opportunities:
        for scored in opportunities:
            trade = execute_trade(client, scored)
            trades.append(trade)
            if trade["status"] == "failed":
                break  # Stop on first failure
    
    # Output summary
    summary = format_scan_summary(opportunities, args.mode, balance, profile, trades)
    print(summary)
    
    client.close()


if __name__ == "__main__":
    main()
