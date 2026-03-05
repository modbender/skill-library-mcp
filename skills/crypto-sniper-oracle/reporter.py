#!/usr/bin/env python3
"""
Crypto Sniper Oracle - Report Generator & Telegram Delivery
Version: 3.3.0
Author: Georges Andronescu (Wesley Armando)
License: MIT

Generates formatted market reports and optionally sends via Telegram.
Supports: daily reports, hourly checks, anomaly alerts, and cron jobs.
"""

import sys
import json
import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error

# ==========================================
# CONFIGURATION
# ==========================================
ORACLE_SCRIPT = Path("/workspace/skills/crypto-sniper-oracle/crypto_oracle.py")
TEMPLATES_DIR = Path("/workspace/skills/crypto-sniper-oracle/templates")
REPORTS_DIR = Path("/workspace/reports")
LOGS_FILE = Path("/workspace/TRADING_LOGS.md")

# Telegram (optional)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_ENABLED = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)

# ==========================================
# REPORT GENERATOR
# ==========================================

class MarketReporter:
    """Generates market analysis reports from oracle data."""
    
    def __init__(self, symbols):
        self.symbols = symbols if isinstance(symbols, list) else [symbols]
        self.data = {}
    
    def fetch_all_data(self):
        """Fetch data for all symbols using crypto_oracle.py"""
        print(f"[INFO] Fetching data for {len(self.symbols)} symbols...")
        
        for symbol in self.symbols:
            try:
                # Call oracle script
                result = subprocess.run(
                    [sys.executable, str(ORACLE_SCRIPT), "--symbol", symbol],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    self.data[symbol] = json.loads(result.stdout)
                    print(f"[OK] {symbol}: Success")
                else:
                    print(f"[ERROR] {symbol}: Failed")
                    self.data[symbol] = {"status": "error", "asset": symbol}
            
            except Exception as e:
                print(f"[ERROR] {symbol}: {e}")
                self.data[symbol] = {"status": "error", "asset": symbol}
    
    def generate_daily_report(self):
        """Generate comprehensive daily market report."""
        
        # Categorize pairs
        bullish = []
        bearish = []
        neutral = []
        
        liquidity_excellent = 0
        liquidity_good = 0
        liquidity_poor = 0
        
        for symbol, data in self.data.items():
            if data.get("status") != "success":
                continue
            
            obi = data.get("order_book", {}).get("imbalance_ratio", 0)
            spread_bps = data.get("order_book", {}).get("spread_bps", 0)
            price_vs_vwap = data.get("quant_signals", {}).get("price_vs_vwap_pct", 0)
            price_change = data.get("ticker", {}).get("price_change_pct", 0)
            
            # Categorize by OBI
            if obi > 0.15:
                bullish.append({
                    "symbol": symbol,
                    "obi": obi,
                    "spread_bps": spread_bps,
                    "price_vs_vwap": price_vs_vwap,
                    "price_change": price_change
                })
            elif obi < -0.15:
                bearish.append({
                    "symbol": symbol,
                    "obi": obi,
                    "spread_bps": spread_bps,
                    "price_vs_vwap": price_vs_vwap,
                    "price_change": price_change
                })
            else:
                neutral.append(symbol)
            
            # Categorize liquidity
            if spread_bps < 5:
                liquidity_excellent += 1
            elif spread_bps < 10:
                liquidity_good += 1
            else:
                liquidity_poor += 1
        
        # Build report
        report = f"""📊 CRYPTO MARKET DAILY REPORT
{datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | Powered by Wesley

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 MARKET OVERVIEW ({len(self.symbols)} pairs analyzed)

"""
        
        # Bullish section
        if bullish:
            report += "🟢 BULLISH SETUPS (OBI > +0.15)\n"
            for pair in bullish:
                report += f"• {pair['symbol']}: OBI {pair['obi']:.2f}, Spread {pair['spread_bps']:.1f} bps\n"
                report += f"  Price vs VWAP: {pair['price_vs_vwap']:+.2f}%\n"
                report += f"  24h Change: {pair['price_change']:+.2f}%\n"
                report += f"  Signal: Strong buying pressure\n\n"
        else:
            report += "🟢 BULLISH SETUPS: None\n\n"
        
        # Bearish section
        if bearish:
            report += "🔴 BEARISH SETUPS (OBI < -0.15)\n"
            for pair in bearish:
                report += f"• {pair['symbol']}: OBI {pair['obi']:.2f}, Spread {pair['spread_bps']:.1f} bps\n"
                report += f"  Price vs VWAP: {pair['price_vs_vwap']:+.2f}%\n"
                report += f"  24h Change: {pair['price_change']:+.2f}%\n"
                report += f"  Signal: Selling pressure\n\n"
        else:
            report += "🔴 BEARISH SETUPS: None\n\n"
        
        # Liquidity summary
        report += "💰 LIQUIDITY QUALITY\n"
        report += f"Excellent (< 5 bps): {liquidity_excellent} pairs\n"
        report += f"Good (5-10 bps): {liquidity_good} pairs\n"
        report += f"Poor (> 10 bps): {liquidity_poor} pairs\n\n"
        
        # Top movers
        all_pairs = bullish + bearish
        if all_pairs:
            sorted_pairs = sorted(all_pairs, key=lambda x: abs(x['price_change']), reverse=True)[:3]
            report += "📈 TOP MOVERS (24h)\n"
            for pair in sorted_pairs:
                report += f"{pair['price_change']:+.1f}% {pair['symbol']}\n"
            report += "\n"
        
        # Trading opportunities
        report += "🎯 TRADING OPPORTUNITIES\n"
        if bullish:
            top_bullish = max(bullish, key=lambda x: x['obi'])
            report += f"→ {top_bullish['symbol']}: Bullish setup confirmed (OBI {top_bullish['obi']:+.2f})\n"
        if bearish:
            top_bearish = min(bearish, key=lambda x: x['obi'])
            report += f"→ {top_bearish['symbol']}: Avoid - selling pressure (OBI {top_bearish['obi']:.2f})\n"
        if not bullish and not bearish:
            report += "→ No strong setups detected. Markets neutral.\n"
        
        report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        report += f"Next report: Tomorrow 09:00 UTC\n"
        
        return report
    
    def generate_hourly_summary(self):
        """Generate brief hourly check."""
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for symbol, data in self.data.items():
            if data.get("status") != "success":
                continue
            
            obi = data.get("order_book", {}).get("imbalance_ratio", 0)
            
            if obi > 0.15:
                bullish_count += 1
            elif obi < -0.15:
                bearish_count += 1
            else:
                neutral_count += 1
        
        report = f"""⚡ HOURLY MARKET CHECK
{datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

🔍 Scanned: {len(self.symbols)} pairs
🟢 Bullish: {bullish_count}
🔴 Bearish: {bearish_count}
⚪ Neutral: {neutral_count}

⚠️ Alerts: None
Next check: {datetime.now().strftime('%H')}:00 UTC
"""
        
        return report
    
    def check_anomalies(self):
        """Check for market anomalies and generate alerts."""
        
        alerts = []
        
        for symbol, data in self.data.items():
            if data.get("status") != "success":
                continue
            
            obi = data.get("order_book", {}).get("imbalance_ratio", 0)
            spread_bps = data.get("order_book", {}).get("spread_bps", 0)
            price_vs_vwap = data.get("quant_signals", {}).get("price_vs_vwap_pct", 0)
            
            # Check for OBI spike (strong signal)
            if abs(obi) > 0.20:
                alert = f"""🚨 MARKET ANOMALY DETECTED

Time: {datetime.now().strftime('%H:%M:%S UTC')}
Asset: {symbol}

📊 Anomaly Type: {"OBI SPIKE (BUY)" if obi > 0 else "OBI SPIKE (SELL)"}
• Current OBI: {obi:.2f}
• Threshold: ±0.20

💰 Liquidity: {"EXCELLENT" if spread_bps < 5 else "GOOD" if spread_bps < 10 else "POOR"} ({spread_bps:.1f} bps)
📈 Price vs VWAP: {price_vs_vwap:+.2f}%

💡 Implication:
{"Strong buying pressure detected." if obi > 0 else "Strong selling pressure detected."}
{"Potential upward movement." if obi > 0 else "Potential downward movement."}

🎯 Suggested Action:
{"Consider LONG entry if other signals align." if obi > 0 else "Consider exiting LONG positions or wait."}
"""
                alerts.append(alert)
        
        return alerts


# ==========================================
# TELEGRAM SENDER
# ==========================================

class TelegramSender:
    """Handles Telegram message delivery."""
    
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_message(self, text):
        """Send message to Telegram."""
        
        # Split if too long (Telegram 4096 char limit)
        if len(text) > 4000:
            parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
        else:
            parts = [text]
        
        for part in parts:
            try:
                data = {
                    "chat_id": self.chat_id,
                    "text": part,
                    "parse_mode": "Markdown"
                }
                
                req = urllib.request.Request(
                    self.api_url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req, timeout=10) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if result.get("ok"):
                        print(f"[OK] Telegram message sent")
                    else:
                        print(f"[ERROR] Telegram API error: {result}")
            
            except Exception as e:
                print(f"[ERROR] Failed to send Telegram: {e}")


# ==========================================
# MAIN
# ==========================================

def main():
    parser = argparse.ArgumentParser(description="Crypto Market Reporter")
    parser.add_argument("--mode", choices=["daily", "hourly", "alerts", "test"], required=True)
    parser.add_argument("--symbols", default="BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,ADAUSDT")
    
    args = parser.parse_args()
    
    symbols = args.symbols.split(",")
    
    # Create reporter
    reporter = MarketReporter(symbols)
    reporter.fetch_all_data()
    
    # Generate report based on mode
    if args.mode == "daily":
        report = reporter.generate_daily_report()
    elif args.mode == "hourly":
        report = reporter.generate_hourly_summary()
    elif args.mode == "alerts":
        alerts = reporter.check_anomalies()
        if alerts:
            report = "\n\n".join(alerts)
        else:
            print("[INFO] No anomalies detected")
            return
    elif args.mode == "test":
        report = "✅ Crypto Sniper Oracle - Telegram Test\n\nIf you see this, Telegram is configured correctly!"
    
    # Save report locally
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / f"{args.mode}_{datetime.now().strftime('%Y-%m-%d')}.md"
    
    with open(report_file, "w") as f:
        f.write(report)
    
    print(f"[OK] Report saved to {report_file}")
    
    # Send via Telegram if enabled
    if TELEGRAM_ENABLED:
        sender = TelegramSender(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        sender.send_message(report)
    else:
        print("[INFO] Telegram not configured - report saved locally only")
    
    # Log execution
    log_entry = f"\n## {datetime.now().isoformat()}\n"
    log_entry += f"Mode: {args.mode}\n"
    log_entry += f"Symbols: {args.symbols}\n"
    log_entry += f"Telegram: {'Sent' if TELEGRAM_ENABLED else 'Disabled'}\n"
    log_entry += f"Report: {report_file}\n"
    
    with open(LOGS_FILE, "a") as f:
        f.write(log_entry)


if __name__ == "__main__":
    main()
