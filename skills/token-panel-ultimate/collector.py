#!/usr/bin/env python3
"""
Budget Collector Daemon

Periodically collects usage data from:
1. OpenClaw transcript files (local)
2. Anthropic Usage API (if configured)
3. Manus task tracking (manual + polling)

Run with: python collector.py
Or as service: systemctl start budget-collector
"""

import asyncio
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

import db
from parsers.transcript import TranscriptParser
from parsers.anthropic import AnthropicParser
from parsers.manus import ManusParser
from parsers.gemini import GeminiParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("budget-collector")


class BudgetCollector:
    """Main collector daemon."""
    
    def __init__(self):
        self.conn = db.get_connection()
        self.transcript_parser = TranscriptParser()
        self.anthropic_parser = AnthropicParser()
        self.manus_parser = ManusParser()
        self.gemini_parser = GeminiParser()
        
        # Track last scan time
        self.last_scan = None
        self.state_file = Path.home() / ".openclaw" / "data" / "collector-state.json"
    
    def scan_transcripts(self):
        """Scan OpenClaw transcripts for new usage data."""
        logger.info("Scanning transcripts...")
        
        # Only scan files modified since last scan
        since = self.last_scan
        count = 0
        
        for usage in self.transcript_parser.scan_all_sessions(since=since):
            # Calculate cost if not present
            if usage.get("cost_usd", 0) == 0:
                if usage["provider"] == "anthropic":
                    usage["cost_usd"] = self.anthropic_parser.calculate_cost(
                        usage["model"],
                        usage["input_tokens"],
                        usage["output_tokens"],
                        usage.get("cache_read_tokens", 0),
                        usage.get("cache_write_tokens", 0),
                    )
                elif usage["provider"] == "gemini":
                    usage["cost_usd"] = self.gemini_parser.calculate_cost(
                        usage["model"],
                        usage["input_tokens"],
                        usage["output_tokens"],
                    )
            
            # Record to database
            db.record_usage(
                self.conn,
                provider=usage["provider"],
                model=usage["model"],
                input_tokens=usage["input_tokens"],
                output_tokens=usage["output_tokens"],
                cost_usd=usage.get("cost_usd", 0),
                cache_read=usage.get("cache_read_tokens", 0),
                cache_write=usage.get("cache_write_tokens", 0),
                recorded_at=usage.get("timestamp"),
            )
            count += 1
        
        logger.info(f"Recorded {count} usage events from transcripts")
        self.last_scan = datetime.utcnow()
        return count
    
    async def fetch_anthropic_usage(self, days: int = 1):
        """Fetch usage from Anthropic API."""
        if not self.anthropic_parser.is_configured():
            logger.info("Anthropic API not configured, skipping")
            return 0
        
        logger.info(f"Fetching Anthropic usage for last {days} days...")
        count = 0
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=i)
            records = await self.anthropic_parser.fetch_daily_usage(date)
            
            for record in records:
                cost = self.anthropic_parser.calculate_cost(
                    record["model"],
                    record["input_tokens"],
                    record["output_tokens"],
                    record.get("cache_read_tokens", 0),
                    record.get("cache_write_tokens", 0),
                )
                
                db.record_usage(
                    self.conn,
                    provider="anthropic",
                    model=record["model"],
                    input_tokens=record["input_tokens"],
                    output_tokens=record["output_tokens"],
                    cost_usd=cost,
                    cache_read=record.get("cache_read_tokens", 0),
                    cache_write=record.get("cache_write_tokens", 0),
                    recorded_at=datetime.fromisoformat(record["date"]),
                )
                count += 1
        
        logger.info(f"Recorded {count} Anthropic usage records")
        return count
    
    def print_status(self):
        """Print current budget status."""
        budgets = db.get_budget_status(self.conn)
        
        print("\n" + "=" * 60)
        print("BUDGET STATUS")
        print("=" * 60)
        
        for b in budgets:
            status_icon = "🔴" if b["status"] == "critical" else \
                         "🟠" if b["status"] == "warning" else "🟢"
            
            if b["provider"] == "manus":
                print(f"{status_icon} {b['provider']:12} {b['percent']:5.1f}% | "
                      f"{b['used']:>6} / {b['limit']:>6} credits | "
                      f"remaining: {b['remaining']}")
            else:
                print(f"{status_icon} {b['provider']:12} {b['percent']:5.1f}% | "
                      f"${b['used']:>7.2f} / ${b['limit']:>7.2f} | "
                      f"remaining: ${b['remaining']:.2f}")
        
        print("=" * 60 + "\n")
    
    async def run_once(self):
        """Run a single collection cycle."""
        logger.info("Starting collection cycle...")
        
        # Scan local transcripts
        self.scan_transcripts()
        
        # Fetch from APIs if configured
        await self.fetch_anthropic_usage(days=1)
        
        # Print status
        self.print_status()
        
        logger.info("Collection cycle complete")
    
    async def run_daemon(self, interval_minutes: int = 30):
        """Run as a daemon, collecting periodically."""
        logger.info(f"Starting daemon (interval: {interval_minutes} min)")
        
        while True:
            try:
                await self.run_once()
            except Exception as e:
                logger.error(f"Collection error: {e}")
            
            await asyncio.sleep(interval_minutes * 60)


def main():
    parser = argparse.ArgumentParser(description="Budget Collector")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=30, help="Daemon interval (minutes)")
    parser.add_argument("--init-budgets", action="store_true", help="Initialize default budgets")
    args = parser.parse_args()
    
    collector = BudgetCollector()
    
    if args.init_budgets:
        logger.info("Initializing default budgets...")
        db.set_budget(collector.conn, "anthropic", 100.0, 0.8)
        db.set_budget(collector.conn, "gemini", 50.0, 0.8)
        db.set_budget(collector.conn, "manus", 500, 0.8)
        db.set_budget(collector.conn, "openai", 50.0, 0.8)
        logger.info("Default budgets set")
    
    if args.daemon:
        asyncio.run(collector.run_daemon(args.interval))
    else:
        asyncio.run(collector.run_once())


if __name__ == "__main__":
    main()
