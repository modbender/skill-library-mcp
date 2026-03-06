#!/usr/bin/env python3
"""
Kalshi Trading Executor

Executes trades based on scanner opportunities and strategy configuration.
Applies risk management, position sizing, and strategy rules.

Usage:
    python executor.py              # Full auto mode
    python executor.py --dry-run    # Show what would be traded
    python executor.py --approve    # Manual approval for each trade
"""

import os
import sys
import json
import argparse
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing dependency: python-dotenv")
    print("Install with: pip install python-dotenv")
    sys.exit(1)

from kalshi_client import KalshiClient
from scanner import FukuAPI, KalshiMatcher, OpportunityMatch

# Load environment variables
load_dotenv()

@dataclass
class StrategyConfig:
    """Strategy configuration."""
    name: str
    sports: List[str]
    min_edge_pct: float
    sizing_method: str  # "flat_pct", "kelly", "flat_amount"
    flat_pct: float = 2.0
    flat_amount: float = 100.0
    kelly_fraction: float = 0.25
    max_position_pct: float = 5.0
    max_daily_loss_pct: float = 10.0
    max_open_positions: int = 10
    max_daily_bets: int = 15
    stop_loss_enabled: bool = True

@dataclass
class RiskLimits:
    """Current risk tracking."""
    daily_bets_made: int = 0
    daily_loss_realized: float = 0.0
    open_positions: int = 0
    total_invested: float = 0.0

@dataclass
class Trade:
    """Trade record."""
    timestamp: str
    ticker: str
    side: str  # "yes" or "no"
    action: str  # "buy" or "sell"
    count: int
    price: float
    amount: float
    game: str
    sport: str
    edge_points: float
    edge_probability: float
    strategy: str
    order_id: Optional[str] = None
    status: str = "placed"  # "placed", "filled", "cancelled", "failed"
    realized_pnl: Optional[float] = None

class TradingExecutor:
    """Executes trades based on opportunities and strategy."""
    
    def __init__(self, config_path: str = "../config/config.json"):
        self.config_path = self._resolve_path(config_path)
        self.trades_path = self._resolve_path("../trades.json")
        self.kill_switch_path = self._resolve_path("../KILL_SWITCH")
        
        self.config = self._load_config()
        self.kalshi_client = KalshiClient()
        self.fuku_api = FukuAPI()
        self.matcher = KalshiMatcher(self.kalshi_client)
        
        self.debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
        
    def _resolve_path(self, path: str) -> str:
        """Resolve path relative to script directory."""
        if os.path.isabs(path):
            return path
        return os.path.join(os.path.dirname(__file__), path)
    
    def _debug_log(self, message: str):
        if self.debug:
            print(f"[EXECUTOR] {message}")
    
    def _load_config(self) -> StrategyConfig:
        """Load strategy configuration."""
        try:
            with open(self.config_path) as f:
                data = json.load(f)
                
            return StrategyConfig(
                name=data.get("strategy", "model_follower"),
                sports=data.get("sports", ["cbb", "nba", "nhl", "soccer"]),
                min_edge_pct=data.get("min_edge_pct", 3.0),
                sizing_method=data["sizing"].get("method", "flat_pct"),
                flat_pct=data["sizing"].get("flat_pct", 2.0),
                flat_amount=data["sizing"].get("flat_amount", 100.0),
                kelly_fraction=data["sizing"].get("kelly_fraction", 0.25),
                max_position_pct=data["sizing"].get("max_position_pct", 5.0),
                max_daily_loss_pct=data["risk"].get("max_daily_loss_pct", 10.0),
                max_open_positions=data["risk"].get("max_open_positions", 10),
                max_daily_bets=data["risk"].get("max_daily_bets", 15),
                stop_loss_enabled=data["risk"].get("stop_loss_enabled", True),
            )
        except FileNotFoundError:
            print(f"❌ Config file not found: {self.config_path}")
            print("Run setup.py to create configuration")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            sys.exit(1)
    
    def _load_trades(self) -> List[Trade]:
        """Load trade history."""
        if not os.path.exists(self.trades_path):
            return []
        
        try:
            with open(self.trades_path) as f:
                data = json.load(f)
                return [Trade(**trade) for trade in data]
        except Exception as e:
            print(f"⚠️  Error loading trades: {e}")
            return []
    
    def _save_trade(self, trade: Trade):
        """Save trade to history."""
        trades = self._load_trades()
        trades.append(trade)
        
        try:
            with open(self.trades_path, "w") as f:
                json.dump([asdict(t) for t in trades], f, indent=2)
            self._debug_log(f"Saved trade: {trade.ticker} {trade.side} {trade.count}")
        except Exception as e:
            print(f"⚠️  Error saving trade: {e}")
    
    def _check_kill_switch(self) -> bool:
        """Check if kill switch is activated."""
        return os.path.exists(self.kill_switch_path)
    
    def _get_current_risk(self) -> RiskLimits:
        """Calculate current risk metrics."""
        trades = self._load_trades()
        today = date.today().isoformat()
        
        # Today's trades
        todays_trades = [t for t in trades if t.timestamp.startswith(today)]
        daily_bets = len(todays_trades)
        daily_loss = sum(t.realized_pnl or 0 for t in todays_trades if (t.realized_pnl or 0) < 0)
        
        # Open positions (approximate from recent trades)
        recent_trades = [t for t in trades if t.status in ["placed", "filled"]]
        open_positions = len(set(t.ticker for t in recent_trades))
        
        # Total invested (recent trades)
        total_invested = sum(t.amount for t in recent_trades if t.status in ["placed", "filled"])
        
        return RiskLimits(
            daily_bets_made=daily_bets,
            daily_loss_realized=abs(daily_loss),
            open_positions=open_positions,
            total_invested=total_invested,
        )
    
    def _get_account_balance(self) -> float:
        """Get account balance in dollars."""
        balance_result = self.kalshi_client.get_balance()
        if balance_result["success"]:
            return balance_result["balance_dollars"]
        else:
            print(f"⚠️  Could not get balance: {balance_result['error']}")
            return 1000.0  # Default assumption
    
    def _calculate_position_size(self, opportunity: OpportunityMatch, balance: float) -> int:
        """Calculate position size based on strategy."""
        if self.config.sizing_method == "flat_amount":
            amount = self.config.flat_amount
        elif self.config.sizing_method == "flat_pct":
            amount = balance * (self.config.flat_pct / 100)
        elif self.config.sizing_method == "kelly":
            # Kelly criterion: f = (bp - q) / b
            # where b = odds, p = probability of win, q = probability of loss
            prob_edge = opportunity.edge_probability / 100
            prob_win = 0.5 + (prob_edge / 2)  # Rough estimate
            prob_lose = 1 - prob_win
            
            market = opportunity.kalshi_market
            yes_price = market.get("yes_price", 50) / 100
            no_price = (100 - market.get("yes_price", 50)) / 100
            
            if opportunity.recommended_side == "yes":
                odds = (1 - yes_price) / yes_price  # Payout odds
                kelly_fraction = ((odds * prob_win) - prob_lose) / odds
            else:
                odds = (1 - no_price) / no_price
                kelly_fraction = ((odds * prob_win) - prob_lose) / odds
            
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap at 25%
            amount = balance * kelly_fraction * self.config.kelly_fraction
        else:
            amount = balance * 0.02  # Default 2%
        
        # Apply max position limit
        max_amount = balance * (self.config.max_position_pct / 100)
        amount = min(amount, max_amount)
        
        # Convert to number of contracts (Kalshi contracts are $1 each)
        contracts = int(amount)
        return max(1, contracts)  # At least 1 contract
    
    def _check_risk_limits(self, risk: RiskLimits, balance: float) -> Optional[str]:
        """Check if risk limits would be violated."""
        if risk.daily_bets_made >= self.config.max_daily_bets:
            return f"Daily bet limit reached ({self.config.max_daily_bets})"
        
        if risk.open_positions >= self.config.max_open_positions:
            return f"Open position limit reached ({self.config.max_open_positions})"
        
        daily_loss_pct = (risk.daily_loss_realized / balance) * 100
        if daily_loss_pct >= self.config.max_daily_loss_pct:
            return f"Daily loss limit reached ({self.config.max_daily_loss_pct}%)"
        
        return None
    
    def _should_trade_opportunity(self, opportunity: OpportunityMatch) -> Tuple[bool, str]:
        """Check if opportunity meets strategy criteria."""
        # Check sport filter
        if opportunity.prediction.sport not in self.config.sports:
            return False, f"Sport {opportunity.prediction.sport} not in strategy"
        
        # Check edge threshold
        if opportunity.edge_probability < self.config.min_edge_pct:
            return False, f"Edge {opportunity.edge_probability:.1f}% below threshold {self.config.min_edge_pct}%"
        
        # Check market type based on strategy
        if self.config.name == "spread_sniper" and opportunity.edge_type != "spread":
            return False, "Spread sniper only trades spreads"
        
        if self.config.name == "totals_specialist" and opportunity.edge_type != "total":
            return False, "Totals specialist only trades totals"
        
        # Conservative strategy requires higher edge
        if self.config.name == "conservative" and opportunity.edge_probability < 5.0:
            return False, "Conservative strategy requires 5%+ edge"
        
        return True, "Opportunity meets criteria"
    
    def _convert_probability_to_price(self, prob_edge: float, current_price: float, side: str) -> int:
        """Convert probability edge to Kalshi price."""
        if side == "yes":
            # If we think YES has higher probability, bid higher than current
            target_price = current_price + (prob_edge / 2)
        else:
            # If we think NO has higher probability, bid higher for NO
            no_price = 100 - current_price
            target_price = no_price + (prob_edge / 2)
        
        # Keep within Kalshi bounds (1-99 cents)
        return max(1, min(99, int(target_price)))
    
    def execute_trade(self, opportunity: OpportunityMatch, dry_run: bool = False, 
                     approve: bool = False) -> Optional[Trade]:
        """Execute a single trade."""
        market = opportunity.kalshi_market
        ticker = market.get("ticker", "")
        
        # Check if we should trade this opportunity
        should_trade, reason = self._should_trade_opportunity(opportunity)
        if not should_trade:
            self._debug_log(f"Skipping {ticker}: {reason}")
            return None
        
        # Get current risk and balance
        risk = self._get_current_risk()
        balance = self._get_account_balance()
        
        # Check risk limits
        risk_violation = self._check_risk_limits(risk, balance)
        if risk_violation:
            print(f"⚠️  Skipping {ticker}: {risk_violation}")
            return None
        
        # Calculate position size
        position_size = self._calculate_position_size(opportunity, balance)
        
        # Calculate price
        current_yes_price = market.get("yes_price", 50)
        bid_price = self._convert_probability_to_price(
            opportunity.edge_probability, 
            current_yes_price, 
            opportunity.recommended_side
        )
        
        # Create trade record
        trade = Trade(
            timestamp=datetime.now().isoformat(),
            ticker=ticker,
            side=opportunity.recommended_side,
            action="buy",
            count=position_size,
            price=bid_price,
            amount=position_size * (bid_price / 100),
            game=f"{opportunity.prediction.away_team} @ {opportunity.prediction.home_team}",
            sport=opportunity.prediction.sport,
            edge_points=opportunity.edge_points,
            edge_probability=opportunity.edge_probability,
            strategy=self.config.name,
        )
        
        # Display trade info
        print(f"\n💰 Trade Opportunity:")
        print(f"   Game: {trade.game} ({trade.sport.upper()})")
        print(f"   Market: {ticker}")
        print(f"   Title: {market.get('title', '')[:60]}")
        print(f"   Edge: {opportunity.edge_points:.1f} points ({opportunity.edge_probability:.1f}%)")
        print(f"   Recommended: {trade.side.upper()} @ {trade.price}¢")
        print(f"   Position: {trade.count} contracts (${trade.amount:.2f})")
        print(f"   Current Price: YES {current_yes_price}¢ / NO {100-current_yes_price}¢")
        
        if dry_run:
            print("   🔍 DRY RUN - No actual trade placed")
            return trade
        
        if approve:
            response = input("\n   Execute this trade? (y/N): ").strip().lower()
            if response not in ('y', 'yes'):
                print("   ❌ Trade cancelled by user")
                return None
        
        # Execute the trade
        print("   🚀 Placing order...")
        
        try:
            result = self.kalshi_client.place_order(
                ticker=ticker,
                side=trade.side,
                action=trade.action,
                count=trade.count,
                yes_price=trade.price if trade.side == "yes" else None
            )
            
            if result["success"]:
                trade.order_id = result.get("order_id")
                trade.status = "placed"
                print(f"   ✅ Order placed! ID: {trade.order_id}")
                
                self._save_trade(trade)
                return trade
            else:
                trade.status = "failed"
                print(f"   ❌ Order failed: {result['error']}")
                return None
                
        except Exception as e:
            print(f"   ❌ Order failed: {e}")
            return None
    
    def scan_and_execute(self, scan_date: str = None, dry_run: bool = False, 
                        approve: bool = False) -> List[Trade]:
        """Scan for opportunities and execute trades."""
        # Check kill switch
        if self._check_kill_switch():
            print("🛑 KILL SWITCH ACTIVATED - Trading halted")
            return []
        
        scan_date = scan_date or date.today().isoformat()
        
        print(f"🔍 Scanning for opportunities on {scan_date}")
        print(f"   Strategy: {self.config.name}")
        print(f"   Sports: {', '.join(self.config.sports)}")
        print(f"   Min Edge: {self.config.min_edge_pct}%")
        
        if dry_run:
            print("   🔍 DRY RUN MODE - No real trades")
        
        print("-" * 60)
        
        # Get predictions with edges
        all_predictions = []
        for sport in self.config.sports:
            predictions = self.fuku_api.get_predictions(sport, scan_date)
            # Filter by edge threshold
            min_edge_points = self.config.min_edge_pct / 2.0  # Rough conversion
            filtered = [p for p in predictions 
                       if (p.spread_edge and p.spread_edge >= min_edge_points) or
                          (p.total_edge and p.total_edge >= min_edge_points)]
            all_predictions.extend(filtered)
            print(f"📊 {sport.upper()}: {len(filtered)} games with sufficient edge")
        
        if not all_predictions:
            print("❌ No predictions found with sufficient edge")
            return []
        
        # Match to Kalshi markets
        print(f"\n🔄 Matching {len(all_predictions)} predictions to Kalshi markets...")
        opportunities = self.matcher.find_matches(all_predictions)
        
        if not opportunities:
            print("❌ No matching Kalshi markets found")
            return []
        
        # Execute trades
        print(f"\n💰 Found {len(opportunities)} opportunities:")
        executed_trades = []
        
        for opp in sorted(opportunities, key=lambda x: x.edge_probability, reverse=True):
            trade = self.execute_trade(opp, dry_run=dry_run, approve=approve)
            if trade:
                executed_trades.append(trade)
        
        if executed_trades:
            total_amount = sum(t.amount for t in executed_trades)
            print(f"\n✅ Executed {len(executed_trades)} trades totaling ${total_amount:.2f}")
        else:
            print("\n❌ No trades executed")
        
        return executed_trades

def main():
    """Executor CLI interface."""
    parser = argparse.ArgumentParser(description="Kalshi Trading Executor")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Show what would be traded without executing")
    parser.add_argument("--approve", action="store_true",
                       help="Require manual approval for each trade")
    parser.add_argument("--date", help="Date to scan (YYYY-MM-DD, default today)")
    parser.add_argument("--config", help="Config file path")
    
    args = parser.parse_args()
    
    try:
        executor = TradingExecutor(args.config) if args.config else TradingExecutor()
        trades = executor.scan_and_execute(
            scan_date=args.date,
            dry_run=args.dry_run,
            approve=args.approve
        )
        
        # Summary
        if trades:
            print(f"\n📋 Trade Summary:")
            for trade in trades:
                status_emoji = "✅" if trade.status == "placed" else "❌"
                print(f"   {status_emoji} {trade.ticker} {trade.side.upper()} {trade.count} @ {trade.price}¢")
    
    except KeyboardInterrupt:
        print("\n🛑 Execution interrupted by user")
    except Exception as e:
        print(f"\n❌ Execution failed: {e}")
        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()