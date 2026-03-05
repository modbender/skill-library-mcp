#!/usr/bin/env python3
"""
Kalshi Portfolio Tracker

Tracks positions, P&L, and trading performance from Kalshi API and local trade history.

Usage:
    python portfolio.py                # Full portfolio summary
    python portfolio.py --positions    # Current positions only
    python portfolio.py --history      # Trade history only
    python portfolio.py --summary      # Quick summary
"""

import os
import sys
import json
import argparse
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import defaultdict

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Missing dependency: python-dotenv")
    print("Install with: pip install python-dotenv")
    sys.exit(1)

from kalshi_client import KalshiClient

# Load environment variables
load_dotenv()

@dataclass
class TradeRecord:
    """Local trade record."""
    timestamp: str
    ticker: str
    side: str
    action: str
    count: int
    price: float
    amount: float
    game: str
    sport: str
    edge_points: float
    edge_probability: float
    strategy: str
    order_id: Optional[str] = None
    status: str = "placed"
    realized_pnl: Optional[float] = None

@dataclass
class Position:
    """Current position summary."""
    ticker: str
    title: str
    side: str
    contracts: int
    avg_price: float
    invested: float
    current_value: float
    unrealized_pnl: float
    market_price: float
    last_updated: str

@dataclass
class PerformanceMetrics:
    """Trading performance metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_invested: float
    total_realized_pnl: float
    total_unrealized_pnl: float
    net_pnl: float
    roi: float
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    by_sport: Dict[str, Dict]
    by_strategy: Dict[str, Dict]

class PortfolioTracker:
    """Tracks Kalshi trading portfolio and performance."""
    
    def __init__(self, trades_path: str = "../trades.json"):
        self.trades_path = self._resolve_path(trades_path)
        self.kalshi_client = KalshiClient()
        self.debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")
    
    def _resolve_path(self, path: str) -> str:
        """Resolve path relative to script directory."""
        if os.path.isabs(path):
            return path
        return os.path.join(os.path.dirname(__file__), path)
    
    def _debug_log(self, message: str):
        if self.debug:
            print(f"[PORTFOLIO] {message}")
    
    def _load_trades(self) -> List[TradeRecord]:
        """Load trade history from local file."""
        if not os.path.exists(self.trades_path):
            return []
        
        try:
            with open(self.trades_path) as f:
                data = json.load(f)
                return [TradeRecord(**trade) for trade in data]
        except Exception as e:
            print(f"⚠️  Error loading trades: {e}")
            return []
    
    def _save_trades(self, trades: List[TradeRecord]):
        """Save trades back to file."""
        try:
            trade_data = []
            for trade in trades:
                trade_dict = {
                    "timestamp": trade.timestamp,
                    "ticker": trade.ticker,
                    "side": trade.side,
                    "action": trade.action,
                    "count": trade.count,
                    "price": trade.price,
                    "amount": trade.amount,
                    "game": trade.game,
                    "sport": trade.sport,
                    "edge_points": trade.edge_points,
                    "edge_probability": trade.edge_probability,
                    "strategy": trade.strategy,
                    "order_id": trade.order_id,
                    "status": trade.status,
                    "realized_pnl": trade.realized_pnl,
                }
                trade_data.append(trade_dict)
                
            with open(self.trades_path, "w") as f:
                json.dump(trade_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving trades: {e}")
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get current account balance."""
        if not self.kalshi_client.is_configured():
            return {"success": False, "error": "Kalshi client not configured"}
        
        return self.kalshi_client.get_balance()
    
    def get_current_positions(self) -> List[Position]:
        """Get current positions from Kalshi API."""
        if not self.kalshi_client.is_configured():
            print("❌ Kalshi client not configured")
            return []
        
        positions = []
        raw_positions = self.kalshi_client.get_positions()
        
        for pos in raw_positions:
            ticker = pos.get("ticker", "")
            position_count = pos.get("position", 0)
            
            if position_count == 0:
                continue
            
            # Get current market price
            market = self.kalshi_client.get_market(ticker)
            if not market:
                continue
            
            # Calculate position details
            side = "yes" if position_count > 0 else "no"
            contracts = abs(position_count)
            
            # Try to find our trades to calculate avg price
            trades = self._load_trades()
            relevant_trades = [t for t in trades if t.ticker == ticker and t.status in ["placed", "filled"]]
            
            if relevant_trades:
                total_cost = sum(t.amount for t in relevant_trades)
                total_contracts = sum(t.count for t in relevant_trades)
                avg_price = (total_cost / total_contracts) * 100 if total_contracts > 0 else 0
                invested = total_cost
            else:
                # Estimate if no local trade data
                avg_price = market.get("yes_price", 50) if side == "yes" else (100 - market.get("yes_price", 50))
                invested = contracts * (avg_price / 100)
            
            # Current market value
            current_price = market.get("yes_price", 50) if side == "yes" else (100 - market.get("yes_price", 50))
            current_value = contracts * (current_price / 100)
            
            position = Position(
                ticker=ticker,
                title=market.get("title", ""),
                side=side,
                contracts=contracts,
                avg_price=avg_price,
                invested=invested,
                current_value=current_value,
                unrealized_pnl=current_value - invested,
                market_price=current_price,
                last_updated=datetime.now().isoformat()
            )
            positions.append(position)
        
        return positions
    
    def update_trade_statuses(self):
        """Update trade statuses from Kalshi API."""
        if not self.kalshi_client.is_configured():
            print("❌ Kalshi client not configured")
            return
        
        trades = self._load_trades()
        updated = False
        
        # Get recent orders from Kalshi
        recent_orders = self.kalshi_client.get_orders(status="executed", limit=100)
        recent_orders.extend(self.kalshi_client.get_orders(status="cancelled", limit=100))
        
        order_lookup = {order.get("order_id"): order for order in recent_orders}
        
        for trade in trades:
            if not trade.order_id or trade.status in ["filled", "cancelled"]:
                continue
            
            kalshi_order = order_lookup.get(trade.order_id)
            if kalshi_order:
                old_status = trade.status
                trade.status = kalshi_order.get("status", trade.status)
                
                # Calculate realized P&L for executed orders
                if trade.status == "executed" and not trade.realized_pnl:
                    # This is simplified - real P&L needs market resolution
                    trade.realized_pnl = 0.0  # Placeholder
                
                if trade.status != old_status:
                    self._debug_log(f"Updated {trade.ticker} status: {old_status} → {trade.status}")
                    updated = True
        
        if updated:
            self._save_trades(trades)
    
    def calculate_performance(self, days: int = None) -> PerformanceMetrics:
        """Calculate trading performance metrics."""
        trades = self._load_trades()
        
        # Filter by date if specified
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            trades = [t for t in trades if t.timestamp >= cutoff_date]
        
        if not trades:
            return PerformanceMetrics(
                total_trades=0, winning_trades=0, losing_trades=0, win_rate=0.0,
                total_invested=0.0, total_realized_pnl=0.0, total_unrealized_pnl=0.0,
                net_pnl=0.0, roi=0.0, avg_win=0.0, avg_loss=0.0,
                largest_win=0.0, largest_loss=0.0, by_sport={}, by_strategy={}
            )
        
        # Basic metrics
        total_trades = len([t for t in trades if t.status in ["placed", "filled", "executed"]])
        total_invested = sum(t.amount for t in trades if t.status in ["placed", "filled", "executed"])
        
        # Realized P&L (from completed trades)
        realized_trades = [t for t in trades if t.realized_pnl is not None]
        total_realized_pnl = sum(t.realized_pnl for t in realized_trades)
        
        winning_trades = len([t for t in realized_trades if t.realized_pnl > 0])
        losing_trades = len([t for t in realized_trades if t.realized_pnl < 0])
        win_rate = winning_trades / len(realized_trades) * 100 if realized_trades else 0.0
        
        # Win/Loss averages
        wins = [t.realized_pnl for t in realized_trades if t.realized_pnl > 0]
        losses = [t.realized_pnl for t in realized_trades if t.realized_pnl < 0]
        
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        largest_win = max(wins) if wins else 0.0
        largest_loss = min(losses) if losses else 0.0
        
        # Unrealized P&L (from current positions)
        positions = self.get_current_positions()
        total_unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        
        # Net P&L and ROI
        net_pnl = total_realized_pnl + total_unrealized_pnl
        roi = (net_pnl / total_invested * 100) if total_invested > 0 else 0.0
        
        # Performance by sport
        by_sport = defaultdict(lambda: {"trades": 0, "invested": 0.0, "pnl": 0.0})
        for trade in trades:
            sport = trade.sport
            by_sport[sport]["trades"] += 1
            by_sport[sport]["invested"] += trade.amount
            if trade.realized_pnl is not None:
                by_sport[sport]["pnl"] += trade.realized_pnl
        
        # Performance by strategy
        by_strategy = defaultdict(lambda: {"trades": 0, "invested": 0.0, "pnl": 0.0})
        for trade in trades:
            strategy = trade.strategy
            by_strategy[strategy]["trades"] += 1
            by_strategy[strategy]["invested"] += trade.amount
            if trade.realized_pnl is not None:
                by_strategy[strategy]["pnl"] += trade.realized_pnl
        
        return PerformanceMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            total_invested=total_invested,
            total_realized_pnl=total_realized_pnl,
            total_unrealized_pnl=total_unrealized_pnl,
            net_pnl=net_pnl,
            roi=roi,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            by_sport=dict(by_sport),
            by_strategy=dict(by_strategy)
        )
    
    def get_trade_history(self, days: int = 30, sport: str = None) -> List[TradeRecord]:
        """Get recent trade history."""
        trades = self._load_trades()
        
        # Filter by date
        if days:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            trades = [t for t in trades if t.timestamp >= cutoff_date]
        
        # Filter by sport
        if sport:
            trades = [t for t in trades if t.sport.lower() == sport.lower()]
        
        # Sort by timestamp (newest first)
        return sorted(trades, key=lambda t: t.timestamp, reverse=True)
    
    def print_summary(self):
        """Print portfolio summary."""
        print("💰 Portfolio Summary")
        print("=" * 50)
        
        # Account balance
        balance_result = self.get_account_balance()
        if balance_result["success"]:
            balance = balance_result["balance_dollars"]
            print(f"💵 Account Balance: ${balance:,.2f}")
        else:
            print(f"❌ Could not get balance: {balance_result['error']}")
            balance = 0.0
        
        # Current positions
        positions = self.get_current_positions()
        if positions:
            total_invested = sum(p.invested for p in positions)
            total_value = sum(p.current_value for p in positions)
            total_unrealized = sum(p.unrealized_pnl for p in positions)
            
            print(f"\n📈 Current Positions ({len(positions)}):")
            print(f"   Total Invested: ${total_invested:,.2f}")
            print(f"   Current Value:  ${total_value:,.2f}")
            print(f"   Unrealized P&L: ${total_unrealized:+,.2f}")
            
            unrealized_pct = (total_unrealized / total_invested * 100) if total_invested > 0 else 0
            emoji = "📈" if total_unrealized >= 0 else "📉"
            print(f"   Return: {emoji} {unrealized_pct:+.1f}%")
        else:
            print("\n📈 No current positions")
        
        # Performance metrics
        perf = self.calculate_performance()
        if perf.total_trades > 0:
            print(f"\n📊 Performance:")
            print(f"   Total Trades: {perf.total_trades}")
            print(f"   Win Rate: {perf.win_rate:.1f}% ({perf.winning_trades}W-{perf.losing_trades}L)")
            print(f"   Total Invested: ${perf.total_invested:,.2f}")
            print(f"   Realized P&L: ${perf.total_realized_pnl:+,.2f}")
            print(f"   Net P&L: ${perf.net_pnl:+,.2f}")
            print(f"   ROI: {perf.roi:+.1f}%")
        else:
            print("\n📊 No trading history yet")
    
    def print_positions(self):
        """Print detailed positions table."""
        positions = self.get_current_positions()
        
        if not positions:
            print("📈 No current positions")
            return
        
        print(f"📈 Current Positions ({len(positions)}):")
        print("-" * 100)
        print(f"{'Ticker':<20} {'Side':<4} {'Contracts':<9} {'Avg Price':<9} {'Current':<8} {'P&L':<12} {'Title'}")
        print("-" * 100)
        
        total_invested = 0
        total_value = 0
        
        for pos in sorted(positions, key=lambda p: p.unrealized_pnl, reverse=True):
            pnl_str = f"${pos.unrealized_pnl:+.2f}"
            pnl_pct = (pos.unrealized_pnl / pos.invested * 100) if pos.invested > 0 else 0
            pnl_str += f" ({pnl_pct:+.1f}%)"
            
            title_short = pos.title[:30] + "..." if len(pos.title) > 30 else pos.title
            
            print(f"{pos.ticker:<20} {pos.side.upper():<4} {pos.contracts:<9} "
                  f"{pos.avg_price:<9.1f} {pos.market_price:<8.1f} {pnl_str:<12} {title_short}")
            
            total_invested += pos.invested
            total_value += pos.current_value
        
        print("-" * 100)
        total_unrealized = total_value - total_invested
        total_pct = (total_unrealized / total_invested * 100) if total_invested > 0 else 0
        print(f"{'TOTAL':<45} ${total_invested:.2f} → ${total_value:.2f} "
              f"(${total_unrealized:+.2f} / {total_pct:+.1f}%)")
    
    def print_history(self, days: int = 30):
        """Print trade history."""
        trades = self.get_trade_history(days)
        
        if not trades:
            print(f"📋 No trades in last {days} days")
            return
        
        print(f"📋 Trade History (Last {days} Days): {len(trades)} trades")
        print("-" * 120)
        print(f"{'Date':<10} {'Sport':<4} {'Ticker':<20} {'Side':<4} {'Count':<5} {'Price':<6} {'Status':<8} {'Game'}")
        print("-" * 120)
        
        for trade in trades:
            date_str = trade.timestamp[:10]  # Just date part
            game_short = trade.game[:40] + "..." if len(trade.game) > 40 else trade.game
            
            print(f"{date_str} {trade.sport.upper():<4} {trade.ticker:<20} "
                  f"{trade.side.upper():<4} {trade.count:<5} {trade.price:<6.0f} "
                  f"{trade.status:<8} {game_short}")

def main():
    """Portfolio CLI interface."""
    parser = argparse.ArgumentParser(description="Kalshi Portfolio Tracker")
    parser.add_argument("--positions", action="store_true", help="Show current positions")
    parser.add_argument("--history", action="store_true", help="Show trade history")
    parser.add_argument("--summary", action="store_true", help="Show summary only")
    parser.add_argument("--days", type=int, default=30, help="History timeframe")
    parser.add_argument("--sport", help="Filter by sport")
    parser.add_argument("--update", action="store_true", help="Update trade statuses from API")
    
    args = parser.parse_args()
    
    tracker = PortfolioTracker()
    
    # Update statuses if requested
    if args.update:
        print("🔄 Updating trade statuses...")
        tracker.update_trade_statuses()
    
    # Show requested information
    if args.summary:
        tracker.print_summary()
    elif args.positions:
        tracker.print_positions()
    elif args.history:
        tracker.print_history(args.days)
    else:
        # Full report
        tracker.print_summary()
        print("\n")
        tracker.print_positions()
        print("\n")
        tracker.print_history(args.days)

if __name__ == "__main__":
    main()