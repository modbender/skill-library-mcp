#!/usr/bin/env python3
"""
Token Optimizer - Verification Module
Verifies optimization setup and estimates savings.
"""

import json
import os
import sys
import shutil
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

try:
    from src.colors import Colors, colorize
except ImportError:
    from colors import Colors, colorize


class OptimizationVerifier:
    """Verifies token optimization setup."""

    def __init__(self):
        self.openclaw_dir = Path.home() / '.openclaw'
        self.config_path = self.openclaw_dir / 'openclaw.json'
        self.checks: List[Tuple[str, bool, str]] = []

    def load_config(self) -> Dict:
        """Load OpenClaw configuration."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def check_config_exists(self) -> bool:
        """Check if config file exists."""
        exists = self.config_path.exists()
        self.checks.append(("Config file exists", exists, str(self.config_path)))
        return exists

    def check_model_routing(self, config: Dict) -> bool:
        """Check model routing is optimized."""
        try:
            primary = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', '')
            is_haiku = 'haiku' in primary.lower()
            self.checks.append(("Default model is Haiku", is_haiku, primary or "not set"))
            return is_haiku
        except Exception:
            self.checks.append(("Default model is Haiku", False, "config error"))
            return False

    def check_model_aliases(self, config: Dict) -> bool:
        """Check model aliases are configured."""
        try:
            models = config.get('agents', {}).get('defaults', {}).get('models', {})
            has_aliases = any('alias' in m for m in models.values())
            alias_list = [m.get('alias', '') for m in models.values() if m.get('alias')]
            self.checks.append(("Model aliases configured", has_aliases, ', '.join(alias_list) or "none"))
            return has_aliases
        except Exception:
            self.checks.append(("Model aliases configured", False, "config error"))
            return False

    def check_heartbeat_provider(self, config: Dict) -> bool:
        """Check heartbeat provider is configured and reachable."""
        try:
            heartbeat = config.get('heartbeat', {})
            if not heartbeat:
                self.checks.append(("Heartbeat provider configured", False, "not configured"))
                return False

            provider = heartbeat.get('provider', '')
            model = heartbeat.get('model', '')

            # Auto-detect provider from model string if not explicit
            if not provider:
                for name in ('ollama', 'lmstudio', 'groq'):
                    if name in model.lower():
                        provider = name
                        break
                if not provider:
                    provider = 'ollama'

            is_free = provider in ('ollama', 'lmstudio', 'none')
            label = f"{provider} ({model})" if model else provider
            self.checks.append(("Heartbeat provider configured", True, label))

            if provider != 'none':
                reachable = self.check_provider_reachable(provider, heartbeat.get('endpoint'))
                self.checks.append(("Heartbeat provider reachable", reachable,
                                    f"{provider} {'OK' if reachable else 'not reachable'}"))
            return True
        except Exception:
            self.checks.append(("Heartbeat provider configured", False, "config error"))
            return False

    def check_provider_reachable(self, provider: str, endpoint: str = None) -> bool:
        """Check if a heartbeat provider is reachable."""
        if provider == "ollama":
            if shutil.which("ollama") is None:
                return False
            try:
                req = urllib.request.Request("http://localhost:11434", method="GET")
                urllib.request.urlopen(req, timeout=5)
                return True
            except Exception:
                return False
        elif provider in ("lmstudio", "groq"):
            url = endpoint or ("http://localhost:1234" if provider == "lmstudio" else "https://api.groq.com")
            try:
                req = urllib.request.Request(url, method="GET")
                urllib.request.urlopen(req, timeout=5)
                return True
            except Exception:
                return False
        return False

    def check_caching_enabled(self, config: Dict) -> bool:
        """Check prompt caching is enabled."""
        try:
            cache = config.get('agents', {}).get('defaults', {}).get('cache', {})
            enabled = cache.get('enabled', False)
            ttl = cache.get('ttl', 'not set')
            self.checks.append(("Prompt caching enabled", enabled, f"TTL: {ttl}"))
            return enabled
        except Exception:
            self.checks.append(("Prompt caching enabled", False, "config error"))
            return False

    def check_rate_limits(self, config: Dict) -> bool:
        """Check rate limits are configured."""
        try:
            rate_limits = config.get('rate_limits', {})
            has_limits = bool(rate_limits)
            details = "configured" if has_limits else "not configured"
            self.checks.append(("Rate limits configured", has_limits, details))
            return has_limits
        except Exception:
            self.checks.append(("Rate limits configured", False, "config error"))
            return False

    def check_budgets(self, config: Dict) -> bool:
        """Check budgets are configured."""
        try:
            budgets = config.get('budgets', {})
            daily = budgets.get('daily')
            monthly = budgets.get('monthly')
            has_budgets = daily is not None or monthly is not None
            details = f"daily: ${daily}, monthly: ${monthly}" if has_budgets else "not configured"
            self.checks.append(("Budget limits configured", has_budgets, details))
            return has_budgets
        except Exception:
            self.checks.append(("Budget limits configured", False, "config error"))
            return False

    def check_workspace_files(self) -> bool:
        """Check workspace files exist and are optimized."""
        workspace_dir = self.openclaw_dir / 'workspace'
        required_files = ['SOUL.md', 'USER.md']

        found = []
        total_size = 0

        for filename in required_files:
            filepath = workspace_dir / filename
            if filepath.exists():
                found.append(filename)
                total_size += filepath.stat().st_size

        all_found = len(found) == len(required_files)
        size_kb = total_size / 1024
        is_lean = size_kb < 15  # Less than 15KB is considered lean

        self.checks.append(("Workspace files exist", all_found, ', '.join(found) or "none found"))
        self.checks.append(("Workspace files are lean", is_lean, f"{size_kb:.1f}KB total"))

        return all_found and is_lean

    def check_prompts_exist(self) -> bool:
        """Check agent prompt files exist."""
        prompts_dir = self.openclaw_dir / 'prompts'
        optimization_rules = prompts_dir / 'OPTIMIZATION-RULES.md'

        exists = optimization_rules.exists()
        self.checks.append(("Optimization prompts generated", exists, str(optimization_rules) if exists else "not found"))
        return exists

    def calculate_savings(self, config: Dict) -> Dict:
        """Calculate estimated monthly savings."""
        savings = {
            'model_routing': 0,
            'heartbeat': 0,
            'caching': 0,
            'session': 0,
            'total': 0
        }

        # Model routing savings (Sonnet -> Haiku)
        primary = config.get('agents', {}).get('defaults', {}).get('model', {}).get('primary', '')
        if 'haiku' in primary.lower():
            # Assume 100 calls/day, 2000 tokens each
            # Sonnet: 0.003 * 200 = $0.60/day
            # Haiku: 0.00025 * 200 = $0.05/day
            savings['model_routing'] = (0.60 - 0.05) * 30  # ~$16.50/month

        # Heartbeat savings
        heartbeat = config.get('heartbeat', {})
        if 'ollama' in heartbeat.get('model', '').lower():
            # 24 heartbeats/day * 500 tokens * $0.00025/1K
            savings['heartbeat'] = 24 * 0.5 * 0.00025 * 30  # ~$0.09/month (small but free)

        # Caching savings (90% on repeated content)
        cache = config.get('agents', {}).get('defaults', {}).get('cache', {})
        if cache.get('enabled'):
            # 5KB agent prompt * 100 calls/day * 0.003/1K * 0.9 savings
            savings['caching'] = 5 * 100 * 0.003 * 0.9 * 30  # ~$40.50/month

        # Session management (estimated from lean context)
        savings['session'] = 12.00  # Estimated from guide

        savings['total'] = sum(v for k, v in savings.items() if k != 'total')

        return savings

    def check_benefit_report(self, savings: Dict):
        """Show benefit report every 7 days with donation CTA."""
        stats_path = self.openclaw_dir / 'token-optimizer-stats.json'

        if not stats_path.exists():
            return

        try:
            with open(stats_path, 'r') as f:
                stats = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        installed_at = stats.get('installed_at')
        if not installed_at:
            return

        try:
            install_date = datetime.fromisoformat(installed_at)
        except ValueError:
            return

        now = datetime.now()
        days_active = (now - install_date).days

        if days_active < 7:
            return

        # Check if 7 days since last report
        last_report = stats.get('last_benefit_report')
        if last_report:
            try:
                last_report_date = datetime.fromisoformat(last_report)
                days_since_report = (now - last_report_date).days
                if days_since_report < 7:
                    return
            except ValueError:
                pass

        # Calculate accumulated savings
        weekly_savings = savings['total'] / 4.33  # monthly to weekly
        total_savings = (savings['total'] / 30) * days_active
        yearly_projection = savings['total'] * 12

        # Show benefit report
        print(colorize("\n  +--------------------------------------------------+", Colors.BOLD + Colors.GREEN))
        print(colorize("  |         Your Savings Report                      |", Colors.BOLD + Colors.GREEN))
        print(colorize("  +--------------------------------------------------+", Colors.GREEN))
        print(colorize(f"  |  Active for: {days_active} days                              ", Colors.GREEN))
        print(colorize(f"  |                                                  ", Colors.GREEN))
        print(colorize(f"  |  Savings this week:       ~${weekly_savings:>8.2f}          ", Colors.GREEN))
        print(colorize(f"  |  Savings since install:   ~${total_savings:>8.2f}          ", Colors.GREEN))
        print(colorize(f"  |  Projected yearly:        ~${yearly_projection:>8.2f}          ", Colors.GREEN))
        print(colorize(f"  |                                                  ", Colors.GREEN))
        print(colorize(f"  |  Token Optimizer is saving you real money.       ", Colors.GREEN))
        print(colorize(f"  |  If it helps, consider a small thank-you:       ", Colors.GREEN))
        print(colorize(f"  |                                                  ", Colors.GREEN))
        print(colorize(f"  |  -> https://ko-fi.com/smartpeopleconnected       ", Colors.CYAN + Colors.BOLD))
        print(colorize(f"  |                                                  ", Colors.GREEN))
        print(colorize("  +--------------------------------------------------+", Colors.GREEN))

        # Update last report timestamp
        stats['last_benefit_report'] = now.isoformat()
        stats['verify_count'] = stats.get('verify_count', 0) + 1
        try:
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
        except IOError:
            pass

    def run_verification(self):
        """Run all verification checks."""
        print(colorize("\n=== Token Optimizer - Verification ===\n", Colors.BOLD + Colors.CYAN))

        # Load config
        config = self.load_config()

        # Run checks
        self.check_config_exists()
        self.check_model_routing(config)
        self.check_model_aliases(config)
        self.check_heartbeat_provider(config)
        self.check_caching_enabled(config)
        self.check_rate_limits(config)
        self.check_budgets(config)
        self.check_workspace_files()
        self.check_prompts_exist()

        # Print results
        print(colorize("VERIFICATION RESULTS:", Colors.BOLD))
        print("-" * 60)

        passed = 0
        failed = 0

        for name, status, details in self.checks:
            if status:
                icon = colorize("[PASS]", Colors.GREEN)
                passed += 1
            else:
                icon = colorize("[FAIL]", Colors.RED)
                failed += 1

            print(f"  {icon} {name}")
            print(colorize(f"         {details}", Colors.BLUE))

        print("-" * 60)

        # Summary
        total = passed + failed
        score = (passed / total) * 100 if total > 0 else 0

        if score == 100:
            status_color = Colors.GREEN
            status_text = "FULLY OPTIMIZED"
        elif score >= 70:
            status_color = Colors.YELLOW
            status_text = "PARTIALLY OPTIMIZED"
        else:
            status_color = Colors.RED
            status_text = "NEEDS OPTIMIZATION"

        print(colorize(f"\nStatus: {status_text}", Colors.BOLD + status_color))
        print(f"Score: {passed}/{total} checks passed ({score:.0f}%)")

        # Calculate and show savings
        savings = self.calculate_savings(config)

        print(colorize("\n--- ESTIMATED MONTHLY SAVINGS ---", Colors.BOLD))
        print(f"  Model Routing:    ${savings['model_routing']:.2f}")
        print(f"  Heartbeat:        ${savings['heartbeat']:.2f}")
        print(f"  Prompt Caching:   ${savings['caching']:.2f}")
        print(f"  Session Mgmt:     ${savings['session']:.2f}")
        print(colorize(f"  TOTAL:            ${savings['total']:.2f}/month", Colors.BOLD + Colors.GREEN))
        print(colorize(f"  YEARLY:           ${savings['total'] * 12:.2f}/year", Colors.GREEN))

        # Recommendations
        if failed > 0:
            print(colorize("\n--- RECOMMENDATIONS ---", Colors.BOLD + Colors.YELLOW))
            for name, status, details in self.checks:
                if not status:
                    print(f"  - Fix: {name}")
            print(colorize("\nRun 'token-optimizer optimize' to apply missing optimizations", Colors.CYAN))

        # Show benefit report (every 7 days)
        self.check_benefit_report(savings)

        return failed == 0


def main():
    verifier = OptimizationVerifier()
    success = verifier.run_verification()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
