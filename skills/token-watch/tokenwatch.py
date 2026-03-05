#!/usr/bin/env python3
"""
TokenWatch v1.2.3
Track, analyze, and optimize token usage and costs across AI providers.

Free and open-source (MIT Licensed)
No external dependencies. Works locally with any provider.

Supported providers and their latest models (Feb 2026):
  Anthropic:  claude-opus-4-6, claude-opus-4-5, claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001
  OpenAI:     gpt-5.2-pro, gpt-5.2, gpt-5, gpt-4.1, gpt-4.1-mini, gpt-4.1-nano, o3, o4-mini
  Google:     gemini-3-pro, gemini-3-flash, gemini-2.5-pro, gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.0-flash
  Mistral:    mistral-large-2411, mistral-medium-3, mistral-small, mistral-nemo, devstral-2
  xAI:        grok-4, grok-3, grok-4.1-fast
  Kimi:       kimi-k2.5, kimi-k2, kimi-k2-turbo
  Qwen:       qwen3.5-plus, qwen3-max, qwen3-vl-32b
  DeepSeek:   deepseek-v3.2, deepseek-r1, deepseek-v3
  Meta:       llama-4-maverick, llama-4-scout, llama-3.3-70b
  MiniMax:    minimax-m2.5, minimax-m1, minimax-text-01
"""

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Pricing table — cost per 1M tokens (input / output) in USD
# Updated: February 16, 2026
# Sources: official provider pricing pages
# ---------------------------------------------------------------------------
PROVIDER_PRICING: Dict[str, Dict] = {
    # ── Anthropic ──────────────────────────────────────────────────────────
    "claude-opus-4-6":              {"input": 5.00,  "output": 25.00, "provider": "anthropic"},
    "claude-opus-4-5":              {"input": 5.00,  "output": 25.00, "provider": "anthropic"},
    "claude-sonnet-4-5-20250929":   {"input": 3.00,  "output": 15.00, "provider": "anthropic"},
    "claude-haiku-4-5-20251001":    {"input": 1.00,  "output": 5.00,  "provider": "anthropic"},

    # ── OpenAI ─────────────────────────────────────────────────────────────
    "gpt-5.2-pro":                  {"input": 21.00, "output": 168.00,"provider": "openai"},
    "gpt-5.2":                      {"input": 1.75,  "output": 14.00, "provider": "openai"},
    "gpt-5":                        {"input": 1.25,  "output": 10.00, "provider": "openai"},
    "gpt-4.1":                      {"input": 2.00,  "output": 8.00,  "provider": "openai"},
    "gpt-4.1-mini":                 {"input": 0.40,  "output": 1.60,  "provider": "openai"},
    "gpt-4.1-nano":                 {"input": 0.10,  "output": 0.40,  "provider": "openai"},
    "o3":                           {"input": 10.00, "output": 40.00, "provider": "openai"},
    "o4-mini":                      {"input": 1.10,  "output": 4.40,  "provider": "openai"},

    # ── Google ─────────────────────────────────────────────────────────────
    "gemini-3-pro":                 {"input": 2.00,  "output": 12.00, "provider": "google"},
    "gemini-3-flash":               {"input": 0.50,  "output": 3.00,  "provider": "google"},
    "gemini-2.5-pro":               {"input": 1.25,  "output": 10.00, "provider": "google"},
    "gemini-2.5-flash":             {"input": 0.30,  "output": 2.50,  "provider": "google"},
    "gemini-2.5-flash-lite":        {"input": 0.10,  "output": 0.40,  "provider": "google"},
    "gemini-2.0-flash":             {"input": 0.10,  "output": 0.40,  "provider": "google"},

    # ── Mistral ────────────────────────────────────────────────────────────
    "mistral-large-2411":           {"input": 2.00,  "output": 6.00,  "provider": "mistral"},
    "mistral-medium-3":             {"input": 0.40,  "output": 2.00,  "provider": "mistral"},
    "mistral-small":                {"input": 0.10,  "output": 0.30,  "provider": "mistral"},
    "mistral-nemo":                 {"input": 0.02,  "output": 0.10,  "provider": "mistral"},
    "devstral-2":                   {"input": 0.40,  "output": 2.00,  "provider": "mistral"},

    # ── xAI Grok ───────────────────────────────────────────────────────────
    "grok-4":                       {"input": 3.00,  "output": 15.00, "provider": "xai"},
    "grok-3":                       {"input": 3.00,  "output": 15.00, "provider": "xai"},
    "grok-4.1-fast":                {"input": 0.20,  "output": 0.50,  "provider": "xai"},

    # ── Kimi (Moonshot AI) ─────────────────────────────────────────────────
    "kimi-k2.5":                    {"input": 0.60,  "output": 3.00,  "provider": "kimi"},
    "kimi-k2":                      {"input": 0.60,  "output": 2.50,  "provider": "kimi"},
    "kimi-k2-turbo":                {"input": 1.15,  "output": 8.00,  "provider": "kimi"},

    # ── Qwen (Alibaba) ─────────────────────────────────────────────────────
    "qwen3.5-plus":                 {"input": 0.11,  "output": 0.44,  "provider": "qwen"},
    "qwen3-max":                    {"input": 0.40,  "output": 1.60,  "provider": "qwen"},
    "qwen3-vl-32b":                 {"input": 0.91,  "output": 3.64,  "provider": "qwen"},

    # ── DeepSeek ───────────────────────────────────────────────────────────
    "deepseek-v3.2":                {"input": 0.14,  "output": 0.28,  "provider": "deepseek"},
    "deepseek-r1":                  {"input": 0.55,  "output": 2.19,  "provider": "deepseek"},
    "deepseek-v3":                  {"input": 0.27,  "output": 1.10,  "provider": "deepseek"},

    # ── Meta Llama ─────────────────────────────────────────────────────────
    "llama-4-maverick":             {"input": 0.27,  "output": 0.85,  "provider": "meta"},
    "llama-4-scout":                {"input": 0.18,  "output": 0.59,  "provider": "meta"},
    "llama-3.3-70b":                {"input": 0.23,  "output": 0.40,  "provider": "meta"},

    # ── MiniMax ────────────────────────────────────────────────────────────
    "minimax-m2.5":                 {"input": 0.30,  "output": 1.20,  "provider": "minimax"},
    "minimax-m1":                   {"input": 0.43,  "output": 1.93,  "provider": "minimax"},
    "minimax-text-01":              {"input": 0.20,  "output": 1.10,  "provider": "minimax"},
}


@dataclass
class TokenUsageRecord:
    """A single recorded API call with token usage"""
    id: str
    timestamp: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    task_label: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class BudgetAlert:
    """A budget threshold alert"""
    id: str
    timestamp: str
    alert_type: str       # "daily", "weekly", "monthly", "session", "per_call"
    threshold_usd: float
    current_spend_usd: float
    model: Optional[str] = None
    message: str = ""


@dataclass
class Budget:
    """User-defined budget thresholds"""
    daily_usd: Optional[float] = None
    weekly_usd: Optional[float] = None
    monthly_usd: Optional[float] = None
    per_call_usd: Optional[float] = None
    alert_at_percent: float = 80.0  # Alert when % of budget is reached


class TokenWatch:
    """
    Track, analyze, and optimize token usage and costs across AI providers.

    Features:
    - Record token usage per API call with automatic cost calculation
    - Set daily/weekly/monthly budgets with threshold alerts
    - Analyze spending by model, provider, time period
    - Get optimization suggestions to reduce costs
    - Export usage reports as JSON or plain text
    - All data stored locally — no external services
    """

    def __init__(self, storage_path: str = ".tokenwatch"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        self.usage_file = self.storage_path / "usage.json"
        self.alerts_file = self.storage_path / "alerts.json"
        self.budget_file = self.storage_path / "budget.json"

        self.records: List[TokenUsageRecord] = self._load_records()
        self.alerts: List[BudgetAlert] = self._load_alerts()
        self.budget: Budget = self._load_budget()

    # ------------------------------------------------------------------
    # Core recording
    # ------------------------------------------------------------------

    def record_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        task_label: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> TokenUsageRecord:
        """
        Record a single API call's token usage.

        Args:
            model: Model name (e.g. "claude-haiku-4-5-20251001")
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens
            task_label: Optional human-readable label for this call
            session_id: Optional session grouping identifier

        Returns:
            TokenUsageRecord with calculated cost
        """
        pricing = PROVIDER_PRICING.get(model)
        if pricing:
            cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
            provider = pricing["provider"]
        else:
            cost = 0.0
            provider = "unknown"
            print(f"⚠️  Unknown model '{model}' — cost recorded as $0.00. Add to PROVIDER_PRICING.")

        record = TokenUsageRecord(
            id=self._generate_id("usage"),
            timestamp=datetime.now().isoformat(),
            model=model,
            provider=provider,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_usd=round(cost, 8),
            task_label=task_label,
            session_id=session_id,
        )

        self.records.append(record)
        self._save_records()
        self._check_budget_alerts(record)

        return record

    def set_budget(
        self,
        daily_usd: Optional[float] = None,
        weekly_usd: Optional[float] = None,
        monthly_usd: Optional[float] = None,
        per_call_usd: Optional[float] = None,
        alert_at_percent: float = 80.0,
    ) -> Budget:
        """
        Set spending budget thresholds.

        Args:
            daily_usd: Max daily spend in USD
            weekly_usd: Max weekly spend in USD
            monthly_usd: Max monthly spend in USD
            per_call_usd: Max cost per single API call
            alert_at_percent: Alert when this % of budget is reached (default 80%)
        """
        self.budget = Budget(
            daily_usd=daily_usd,
            weekly_usd=weekly_usd,
            monthly_usd=monthly_usd,
            per_call_usd=per_call_usd,
            alert_at_percent=alert_at_percent,
        )
        self._save_budget()
        print(f"✅ Budget set: daily=${daily_usd}, weekly=${weekly_usd}, monthly=${monthly_usd}")
        return self.budget

    # ------------------------------------------------------------------
    # Spending analysis
    # ------------------------------------------------------------------

    def get_spend(self, period: str = "today") -> Dict:
        """
        Get total spend for a time period.

        Args:
            period: "today", "week", "month", "all", or "YYYY-MM-DD" for specific date

        Returns:
            Dict with total_cost, total_tokens, call_count, by_model breakdown
        """
        records = self._filter_by_period(period)
        return self._aggregate_records(records, period)

    def get_spend_by_model(self, period: str = "month") -> Dict[str, Dict]:
        """Get spending broken down by model for a period."""
        records = self._filter_by_period(period)
        by_model: Dict[str, List] = {}
        for r in records:
            by_model.setdefault(r.model, []).append(r)

        result = {}
        for model, recs in sorted(by_model.items(), key=lambda x: -sum(r.cost_usd for r in x[1])):
            result[model] = {
                "total_cost_usd": round(sum(r.cost_usd for r in recs), 6),
                "total_tokens": sum(r.total_tokens for r in recs),
                "call_count": len(recs),
                "avg_cost_per_call": round(sum(r.cost_usd for r in recs) / len(recs), 6),
                "provider": recs[0].provider,
            }
        return result

    def get_spend_by_provider(self, period: str = "month") -> Dict[str, Dict]:
        """Get spending broken down by provider for a period."""
        records = self._filter_by_period(period)
        by_provider: Dict[str, List] = {}
        for r in records:
            by_provider.setdefault(r.provider, []).append(r)

        result = {}
        for provider, recs in sorted(by_provider.items(), key=lambda x: -sum(r.cost_usd for r in x[1])):
            result[provider] = {
                "total_cost_usd": round(sum(r.cost_usd for r in recs), 6),
                "total_tokens": sum(r.total_tokens for r in recs),
                "call_count": len(recs),
            }
        return result

    def get_recent_calls(self, limit: int = 10) -> List[TokenUsageRecord]:
        """Get the most recent API calls."""
        return sorted(self.records, key=lambda x: x.timestamp, reverse=True)[:limit]

    def get_alerts(self, unacknowledged_only: bool = False) -> List[BudgetAlert]:
        """Get budget alerts."""
        return self.alerts if not unacknowledged_only else [
            a for a in self.alerts if "acknowledged" not in a.alert_type
        ]

    # ------------------------------------------------------------------
    # Cost optimization
    # ------------------------------------------------------------------

    def get_optimization_suggestions(self) -> List[Dict]:
        """
        Analyze usage and suggest ways to reduce costs.

        Returns list of actionable suggestions with estimated savings.
        """
        suggestions = []
        monthly = self._filter_by_period("month")
        if not monthly:
            return [{"type": "info", "message": "No usage data yet. Record some calls first."}]

        by_model = self.get_spend_by_model("month")
        total_monthly = sum(r.cost_usd for r in monthly)

        for model, stats in by_model.items():
            pricing = PROVIDER_PRICING.get(model, {})
            provider = pricing.get("provider", "")

            # Suggest cheaper alternatives
            if model == "claude-opus-4-6" and stats["call_count"] > 10:
                sonnet_cost = stats["total_tokens"] * PROVIDER_PRICING["claude-sonnet-4-5-20250929"]["input"] / 1_000_000
                savings = stats["total_cost_usd"] - sonnet_cost
                suggestions.append({
                    "type": "model_swap",
                    "priority": "high",
                    "current_model": model,
                    "suggested_model": "claude-sonnet-4-5-20250929",
                    "message": f"Swap Opus → Sonnet for non-reasoning tasks",
                    "estimated_monthly_savings_usd": round(savings, 4),
                })

            if model == "gpt-4o" and stats["call_count"] > 10:
                mini_cost = stats["total_tokens"] * PROVIDER_PRICING["gpt-4o-mini"]["input"] / 1_000_000
                savings = stats["total_cost_usd"] - mini_cost
                suggestions.append({
                    "type": "model_swap",
                    "priority": "high",
                    "current_model": model,
                    "suggested_model": "gpt-4o-mini",
                    "message": f"Swap GPT-4o → GPT-4o-mini for simple tasks",
                    "estimated_monthly_savings_usd": round(savings, 4),
                })

            # Flag high average cost per call
            if stats["avg_cost_per_call"] > 0.05:
                suggestions.append({
                    "type": "prompt_length",
                    "priority": "medium",
                    "model": model,
                    "message": f"High avg cost/call (${stats['avg_cost_per_call']:.4f}) on {model} — consider reducing prompt length or batching",
                    "avg_cost_per_call_usd": stats["avg_cost_per_call"],
                })

        # Gemini flash suggestion if using pricier models heavily
        expensive_spend = sum(
            stats["total_cost_usd"] for m, stats in by_model.items()
            if PROVIDER_PRICING.get(m, {}).get("input", 0) > 1.0
        )
        if expensive_spend > 5.0:
            suggestions.append({
                "type": "provider_swap",
                "priority": "medium",
                "message": "Consider Gemini 2.5 Flash for high-volume tasks — $0.075/1M input tokens",
                "suggested_model": "gemini-2.5-flash",
            })

        if not suggestions:
            suggestions.append({
                "type": "info",
                "priority": "low",
                "message": f"✅ Spending looks efficient. Monthly total: ${total_monthly:.4f}",
            })

        return sorted(suggestions, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.get("priority", "low"), 2))

    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> Dict:
        """
        Estimate the cost of a hypothetical API call before making it.

        Args:
            model: Model name
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens
        """
        pricing = PROVIDER_PRICING.get(model)
        if not pricing:
            return {"error": f"Unknown model: {model}. Check PROVIDER_PRICING."}

        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
        return {
            "model": model,
            "provider": pricing["provider"],
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(cost, 8),
            "input_rate_per_1m": pricing["input"],
            "output_rate_per_1m": pricing["output"],
        }

    def compare_models(self, input_tokens: int, output_tokens: int) -> List[Dict]:
        """
        Compare costs across all known models for a given token count.
        Returns sorted list from cheapest to most expensive.
        """
        results = []
        for model, pricing in PROVIDER_PRICING.items():
            cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
            results.append({
                "model": model,
                "provider": pricing["provider"],
                "cost_usd": round(cost, 8),
                "input_rate_per_1m": pricing["input"],
                "output_rate_per_1m": pricing["output"],
            })
        return sorted(results, key=lambda x: x["cost_usd"])

    # ------------------------------------------------------------------
    # Export & reporting
    # ------------------------------------------------------------------

    def export_report(self, output_file: str = "token_usage_report.json", period: str = "month"):
        """Export a usage report to JSON."""
        records = self._filter_by_period(period)
        data = {
            "report_period": period,
            "generated_at": datetime.now().isoformat(),
            "summary": self._aggregate_records(records, period),
            "by_model": self.get_spend_by_model(period),
            "by_provider": self.get_spend_by_provider(period),
            "optimization_suggestions": self.get_optimization_suggestions(),
            "records": [asdict(r) for r in records],
        }
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"📁 Report exported to {output_file}")

    def format_dashboard(self, period: str = "today") -> str:
        """Format a human-readable spending dashboard."""
        today = self._aggregate_records(self._filter_by_period("today"), "today")
        week = self._aggregate_records(self._filter_by_period("week"), "week")
        month = self._aggregate_records(self._filter_by_period("month"), "month")
        by_model = self.get_spend_by_model("month")
        suggestions = self.get_optimization_suggestions()

        budget_lines = self._format_budget_status(today, week, month)

        output = f"""
╔═══════════════════════════════════════════════════════════════╗
║              TOKEN BUDGET MONITOR — DASHBOARD                 ║
╚═══════════════════════════════════════════════════════════════╝

💰 SPENDING SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Today:   ${today['total_cost_usd']:.4f}  ({today['call_count']} calls, {today['total_tokens']:,} tokens)
  Week:    ${week['total_cost_usd']:.4f}  ({week['call_count']} calls, {week['total_tokens']:,} tokens)
  Month:   ${month['total_cost_usd']:.4f}  ({month['call_count']} calls, {month['total_tokens']:,} tokens)

{budget_lines}
📊 THIS MONTH BY MODEL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for model, stats in list(by_model.items())[:5]:
            bar = "█" * min(int(stats["total_cost_usd"] / max(month["total_cost_usd"], 0.001) * 20), 20)
            output += f"  {model[:35]:<35} ${stats['total_cost_usd']:.4f}  {bar}\n"

        output += f"""
💡 OPTIMIZATION TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        for i, s in enumerate(suggestions[:3], 1):
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(s.get("priority", "low"), "•")
            savings = s.get("estimated_monthly_savings_usd")
            savings_str = f" (save ~${savings:.4f}/mo)" if savings else ""
            output += f"  {priority_icon} {s['message']}{savings_str}\n"

        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _filter_by_period(self, period: str) -> List[TokenUsageRecord]:
        now = datetime.now()
        if period == "today":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == "week":
            cutoff = now - timedelta(days=7)
        elif period == "month":
            cutoff = now - timedelta(days=30)
        elif period == "all":
            return self.records
        else:
            # Try parsing as YYYY-MM-DD
            try:
                cutoff = datetime.strptime(period, "%Y-%m-%d")
                end = cutoff + timedelta(days=1)
                return [r for r in self.records if cutoff <= datetime.fromisoformat(r.timestamp) < end]
            except ValueError:
                return self.records

        return [r for r in self.records if datetime.fromisoformat(r.timestamp) >= cutoff]

    def _aggregate_records(self, records: List[TokenUsageRecord], period: str) -> Dict:
        return {
            "period": period,
            "total_cost_usd": round(sum(r.cost_usd for r in records), 6),
            "total_tokens": sum(r.total_tokens for r in records),
            "input_tokens": sum(r.input_tokens for r in records),
            "output_tokens": sum(r.output_tokens for r in records),
            "call_count": len(records),
            "avg_cost_per_call": round(sum(r.cost_usd for r in records) / len(records), 6) if records else 0,
        }

    def _check_budget_alerts(self, record: TokenUsageRecord):
        """Check budget thresholds and fire alerts if exceeded."""
        now_str = datetime.now().isoformat()

        if self.budget.per_call_usd and record.cost_usd > self.budget.per_call_usd:
            self._fire_alert("per_call", self.budget.per_call_usd, record.cost_usd,
                             f"Single call ${record.cost_usd:.6f} exceeded limit ${self.budget.per_call_usd}")

        for period_key, budget_val in [
            ("daily", self.budget.daily_usd),
            ("weekly", self.budget.weekly_usd),
            ("monthly", self.budget.monthly_usd),
        ]:
            if not budget_val:
                continue
            period_map = {"daily": "today", "weekly": "week", "monthly": "month"}
            spend = self._aggregate_records(self._filter_by_period(period_map[period_key]), period_map[period_key])
            pct = (spend["total_cost_usd"] / budget_val) * 100
            threshold = self.budget.alert_at_percent
            if pct >= 100:
                self._fire_alert(period_key, budget_val, spend["total_cost_usd"],
                                 f"⛔ {period_key.title()} budget EXCEEDED: ${spend['total_cost_usd']:.4f} / ${budget_val}")
            elif pct >= threshold:
                self._fire_alert(f"{period_key}_warning", budget_val, spend["total_cost_usd"],
                                 f"⚠️  {period_key.title()} budget at {pct:.0f}%: ${spend['total_cost_usd']:.4f} / ${budget_val}")

    def _fire_alert(self, alert_type: str, threshold: float, current: float, message: str):
        alert = BudgetAlert(
            id=self._generate_id("alert"),
            timestamp=datetime.now().isoformat(),
            alert_type=alert_type,
            threshold_usd=threshold,
            current_spend_usd=current,
            message=message,
        )
        self.alerts.append(alert)
        self._save_alerts()
        print(f"\n🚨 BUDGET ALERT: {message}\n")

    def _format_budget_status(self, today, week, month) -> str:
        if not any([self.budget.daily_usd, self.budget.weekly_usd, self.budget.monthly_usd]):
            return "📋 BUDGET\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n  No budget set. Use set_budget() to configure limits.\n"

        lines = "📋 BUDGET STATUS\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for label, spend, limit in [
            ("Daily", today["total_cost_usd"], self.budget.daily_usd),
            ("Weekly", week["total_cost_usd"], self.budget.weekly_usd),
            ("Monthly", month["total_cost_usd"], self.budget.monthly_usd),
        ]:
            if limit:
                pct = (spend / limit) * 100
                bar_fill = int(pct / 5)
                bar = "█" * bar_fill + "░" * (20 - bar_fill)
                status = "⛔" if pct >= 100 else "⚠️ " if pct >= self.budget.alert_at_percent else "✅"
                lines += f"  {label}: [{bar}] {pct:.0f}% ${spend:.4f} / ${limit:.2f} {status}\n"
        return lines

    def _load_records(self) -> List[TokenUsageRecord]:
        if not self.usage_file.exists():
            return []
        try:
            with open(self.usage_file) as f:
                return [TokenUsageRecord(**item) for item in json.load(f)]
        except Exception as e:
            print(f"Warning: Could not load usage records: {e}")
            return []

    def _load_alerts(self) -> List[BudgetAlert]:
        if not self.alerts_file.exists():
            return []
        try:
            with open(self.alerts_file) as f:
                return [BudgetAlert(**item) for item in json.load(f)]
        except Exception as e:
            print(f"Warning: Could not load alerts: {e}")
            return []

    def _load_budget(self) -> Budget:
        if not self.budget_file.exists():
            return Budget()
        try:
            with open(self.budget_file) as f:
                return Budget(**json.load(f))
        except Exception as e:
            print(f"Warning: Could not load budget: {e}")
            return Budget()

    def _save_records(self):
        with open(self.usage_file, "w") as f:
            json.dump([asdict(r) for r in self.records], f, indent=2)

    def _save_alerts(self):
        with open(self.alerts_file, "w") as f:
            json.dump([asdict(a) for a in self.alerts], f, indent=2)

    def _save_budget(self):
        with open(self.budget_file, "w") as f:
            json.dump(asdict(self.budget), f, indent=2)

    def _generate_id(self, prefix: str) -> str:
        import uuid
        return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ---------------------------------------------------------------------------
# Anthropic usage hook — auto-record from response object
# ---------------------------------------------------------------------------

def record_from_anthropic_response(monitor: TokenWatch, response, task_label: str = None):
    """
    Auto-record token usage from an Anthropic API response object.

    SECURITY: This function ONLY extracts model name and token counts from the
    response object. It does NOT access, log, or persist API keys, full response
    content, or any other metadata. Only `response.model`, `usage.input_tokens`,
    and `usage.output_tokens` are read.

    Usage:
        response = client.messages.create(...)
        record_from_anthropic_response(monitor, response, task_label="summarize doc")
    """
    usage = response.usage
    return monitor.record_usage(
        model=response.model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        task_label=task_label,
    )


def record_from_openai_response(monitor: TokenWatch, response, task_label: str = None):
    """
    Auto-record token usage from an OpenAI API response object.

    SECURITY: This function ONLY extracts model name and token counts from the
    response object. It does NOT access, log, or persist API keys, full response
    content, or any other metadata. Only `response.model`, `usage.prompt_tokens`,
    and `usage.completion_tokens` are read.

    Usage:
        response = client.chat.completions.create(...)
        record_from_openai_response(monitor, response, task_label="draft email")
    """
    usage = response.usage
    model = response.model
    # Normalize model names (OpenAI sometimes returns e.g. "gpt-4o-2024-11-20")
    for known_model in PROVIDER_PRICING:
        if known_model in model:
            model = known_model
            break
    return monitor.record_usage(
        model=model,
        input_tokens=usage.prompt_tokens,
        output_tokens=usage.completion_tokens,
        task_label=task_label,
    )


# ---------------------------------------------------------------------------
# Example / demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    monitor = TokenWatch()

    # Set a monthly budget
    monitor.set_budget(daily_usd=1.00, weekly_usd=5.00, monthly_usd=15.00)

    # Simulate some API calls
    monitor.record_usage("claude-haiku-4-5-20251001", input_tokens=1200, output_tokens=400, task_label="summarize article")
    monitor.record_usage("claude-sonnet-4-5-20250929", input_tokens=3000, output_tokens=800, task_label="code review")
    monitor.record_usage("gpt-4o-mini", input_tokens=500, output_tokens=200, task_label="classify intent")
    monitor.record_usage("gemini-2.5-flash", input_tokens=8000, output_tokens=1200, task_label="long doc analysis")

    # Print dashboard
    print(monitor.format_dashboard())

    # Compare model costs for a typical call
    print("\n📊 MODEL COST COMPARISON (2000 input + 500 output tokens):")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    for m in monitor.compare_models(2000, 500)[:6]:
        print(f"  {m['model']:<40} ${m['cost_usd']:.6f}")
