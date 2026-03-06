#!/usr/bin/env python3
"""
AI Economic Tracker - ClawHub Skill
Track daily costs, income, and net worth for AI agents with economic pressure-driven decision making.

Inspired by HKUDS/ClawWork research on economic incentives for AI agents.
Adapted for OpenClaw agent systems.
"""

import json
import os
from datetime import datetime
from pathlib import Path

# Configurable via environment variables
DATA_DIR = Path(os.getenv("ECONOMIC_TRACKER_DATA_DIR", 
                          str(Path.home() / ".openclaw" / "workspace" / "data" / "economics")))
BALANCE_FILE = DATA_DIR / "balance.jsonl"
DAILY_LOG = DATA_DIR / "daily_log.jsonl"
INCOME_LOG = DATA_DIR / "income_log.jsonl"

# Configurable costs
COSTS = {
    "electricity_daily": float(os.getenv("ECONOMIC_TRACKER_ELECTRICITY_DAILY", "0.50")),
    "internet_daily": float(os.getenv("ECONOMIC_TRACKER_INTERNET_DAILY", "1.50")),
}

# BLS wage reference for service valuation (US Bureau of Labor Statistics)
BLS_WAGES = {
    "computer_systems_manager": 90.38,
    "financial_manager": 86.76,
    "software_developer": 69.50,
    "financial_analyst": 47.16,
    "market_research": 38.71,
    "customer_service": 22.00,
    "general_operations": 64.00,
    "data_analyst": 52.00,
    "compliance_officer": 44.96,
    "editor": 72.06,
}

# Survival status thresholds (configurable)
SURVIVAL_THRESHOLDS = {
    "thriving": float(os.getenv("ECONOMIC_TRACKER_THRIVING", "5000")),
    "stable": float(os.getenv("ECONOMIC_TRACKER_STABLE", "1500")),
    "struggling": float(os.getenv("ECONOMIC_TRACKER_STRUGGLING", "500")),
    "critical": float(os.getenv("ECONOMIC_TRACKER_CRITICAL", "0")),
}


class EconomicTracker:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.balance = 0.0
        self.total_income = 0.0
        self.total_cost = 0.0
        self.daily_cost = sum([
            COSTS["electricity_daily"],
            COSTS["internet_daily"],
        ])
        self._load_state()

    def _load_state(self):
        """Load latest state from balance file"""
        if BALANCE_FILE.exists():
            lines = BALANCE_FILE.read_text().strip().split("\n")
            if lines and lines[-1]:
                last = json.loads(lines[-1])
                self.balance = last.get("balance", 0.0)
                self.total_income = last.get("total_income", 0.0)
                self.total_cost = last.get("total_cost", 0.0)

    def get_status(self):
        """Get current economic status"""
        status = "bankrupt"
        for level, threshold in SURVIVAL_THRESHOLDS.items():
            if self.balance > threshold:
                status = level
                break
        
        return {
            "balance": round(self.balance, 2),
            "total_income": round(self.total_income, 2),
            "total_cost": round(self.total_cost, 2),
            "net_profit": round(self.total_income - self.total_cost, 2),
            "daily_burn": round(self.daily_cost, 2),
            "runway_days": int(self.balance / self.daily_cost) if self.daily_cost > 0 else 999,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }

    def add_income(self, amount, source, description=""):
        """Record income transaction"""
        self.balance += amount
        self.total_income += amount
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": "income",
            "amount": amount,
            "source": source,
            "description": description,
            "balance_after": round(self.balance, 2),
        }
        
        with open(INCOME_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        self._save_state()
        return record

    def add_cost(self, amount, category, description=""):
        """Record cost transaction"""
        self.balance -= amount
        self.total_cost += amount
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "type": "cost",
            "amount": amount,
            "category": category,
            "description": description,
            "balance_after": round(self.balance, 2),
        }
        
        with open(DAILY_LOG, "a") as f:
            f.write(json.dumps(record) + "\n")
        
        self._save_state()
        return record

    def set_balance(self, amount, reason="manual_set"):
        """Manually set balance (for initialization)"""
        self.balance = amount
        self._save_state(reason=reason)

    def daily_report(self):
        """Generate daily economic report"""
        s = self.get_status()
        
        emoji = {
            "thriving": "🟢",
            "stable": "🔵", 
            "struggling": "🟡",
            "critical": "🔴",
            "bankrupt": "💀",
        }
        
        report = f"""📊 Economic Daily Report | {datetime.now().strftime('%Y-%m-%d')}
{'='*40}
💰 Balance: ${s['balance']:.2f}
📈 Total Income: ${s['total_income']:.2f}
📉 Total Cost: ${s['total_cost']:.2f}
💵 Net Profit: ${s['net_profit']:.2f}
🔥 Daily Burn: ${s['daily_burn']:.2f}
⏳ Runway: {s['runway_days']} days
{emoji.get(s['status'], '❓')} Status: {s['status'].upper()}
{'='*40}"""
        
        return report

    def estimate_service_value(self, task_type, hours):
        """Estimate service value using BLS wage data"""
        wage = BLS_WAGES.get(task_type, BLS_WAGES["general_operations"])
        value = wage * hours
        return {
            "task_type": task_type,
            "hourly_wage": wage,
            "hours": hours,
            "estimated_value": round(value, 2),
            "pricing_range": {
                "low": round(value * 0.5, 2),
                "mid": round(value * 0.75, 2),
                "high": round(value * 1.0, 2),
            }
        }

    def _save_state(self, reason="auto"):
        """Save current state to balance file"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "balance": round(self.balance, 2),
            "total_income": round(self.total_income, 2),
            "total_cost": round(self.total_cost, 2),
            "status": self.get_status()["status"],
            "reason": reason,
        }
        
        with open(BALANCE_FILE, "a") as f:
            f.write(json.dumps(record) + "\n")


def work_or_learn(balance, pending_tasks=0, learning_value=0):
    """
    ClawWork core decision: work or learn?
    
    Rules:
    - critical/struggling → must work to earn money
    - stable → 70% work, 30% learn
    - thriving → 50% work, 50% learn
    """
    if balance < SURVIVAL_THRESHOLDS["struggling"]:
        return "work", "Balance below warning threshold, must prioritize earning"
    elif balance < SURVIVAL_THRESHOLDS["stable"]:
        if pending_tasks > 0:
            return "work", "Pending tasks exist, prioritize delivery and income"
        return "learn", "No urgent tasks, invest in learning to improve capabilities"
    else:
        if learning_value > 100:
            return "learn", f"High learning value (${learning_value}), invest in future"
        return "work", "Continue generating income for compound growth"


if __name__ == "__main__":
    import sys
    
    tracker = EconomicTracker()
    
    if len(sys.argv) < 2:
        print(tracker.daily_report())
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "status":
        print(json.dumps(tracker.get_status(), indent=2))
    
    elif cmd == "report":
        print(tracker.daily_report())
    
    elif cmd == "init":
        amount = float(sys.argv[2]) if len(sys.argv) > 2 else 1000.0
        tracker.set_balance(amount, "initial_setup")
        print(f"✅ Initial balance set: ${amount:.2f}")
    
    elif cmd == "income":
        if len(sys.argv) < 4:
            print("Usage: tracker.py income <amount> <source> [description]")
            sys.exit(1)
        amount = float(sys.argv[2])
        source = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        r = tracker.add_income(amount, source, desc)
        print(f"✅ Income +${amount:.2f} ({source}) → Balance ${r['balance_after']:.2f}")
    
    elif cmd == "cost":
        if len(sys.argv) < 4:
            print("Usage: tracker.py cost <amount> <category> [description]")
            sys.exit(1)
        amount = float(sys.argv[2])
        category = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        r = tracker.add_cost(amount, category, desc)
        print(f"✅ Cost -${amount:.2f} ({category}) → Balance ${r['balance_after']:.2f}")
    
    elif cmd == "estimate":
        task = sys.argv[2] if len(sys.argv) > 2 else "general_operations"
        hours = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        print(json.dumps(tracker.estimate_service_value(task, hours), indent=2))
    
    elif cmd == "decide":
        balance = tracker.balance
        pending = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        learning = float(sys.argv[3]) if len(sys.argv) > 3 else 0
        decision, reason = work_or_learn(balance, pending, learning)
        print(f"Decision: {decision.upper()} | Reason: {reason}")
    
    else:
        print(f"Usage: {sys.argv[0]} [status|report|init|income|cost|estimate|decide]")
        print("\nCommands:")
        print("  status              - Show current economic status (JSON)")
        print("  report              - Generate daily report")
        print("  init <amount>       - Initialize balance")
        print("  income <amt> <src> [desc] - Record income")
        print("  cost <amt> <cat> [desc]   - Record cost")
        print("  estimate <task> <hours>   - Estimate service value")
        print("  decide [pending] [learning] - Get work/learn decision")
