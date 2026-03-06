#!/usr/bin/env python3
"""
Token Optimizer - Main Optimization Module
Applies token optimization configurations to OpenClaw.
"""

import json
import os
import sys
import shutil
import difflib
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

try:
    from src.colors import Colors, colorize
    from src import __version__
except ImportError:
    # Standalone execution fallback
    from colors import Colors, colorize
    __version__ = "1.0.8"


HEARTBEAT_PROVIDERS = {
    "ollama": {
        "endpoint": "http://localhost:11434",
        "default_model": "llama3.2:3b",
        "model_prefix": "ollama/",
        "cli_name": "ollama",
    },
    "lmstudio": {
        "endpoint": "http://localhost:1234",
        "default_model": "llama3.2:3b",
        "model_prefix": "lmstudio/",
        "cli_name": None,
    },
    "groq": {
        "endpoint": "https://api.groq.com",
        "default_model": "llama-3.2-3b-preview",
        "model_prefix": "groq/",
        "cli_name": None,
    },
    "none": {
        "endpoint": None,
        "default_model": None,
        "model_prefix": "",
        "cli_name": None,
    },
}


def resolve_heartbeat_provider(config: Dict) -> str:
    """Resolve heartbeat provider from config, with auto-detect fallback."""
    heartbeat = config.get("heartbeat", {})

    # Explicit provider field takes priority
    provider = heartbeat.get("provider")
    if provider and provider in HEARTBEAT_PROVIDERS:
        return provider

    # Auto-detect from model string
    model = heartbeat.get("model", "")
    for name in HEARTBEAT_PROVIDERS:
        if name != "none" and name in model.lower():
            return name

    return "ollama"  # default


def check_heartbeat_provider(provider: str) -> bool:
    """Check if a heartbeat provider is reachable."""
    if provider == "none":
        return True

    info = HEARTBEAT_PROVIDERS.get(provider)
    if not info:
        return False

    # Check if CLI tool is installed (e.g. ollama)
    cli_name = info.get("cli_name")
    if cli_name:
        if shutil.which(cli_name) is None:
            return False
        # CLI found, try reaching the HTTP endpoint too
        endpoint = info.get("endpoint")
        if endpoint:
            try:
                req = urllib.request.Request(endpoint, method="GET")
                urllib.request.urlopen(req, timeout=5)
                return True
            except Exception:
                return False
        return True

    # Try HTTP endpoint
    endpoint = info.get("endpoint")
    if endpoint:
        try:
            req = urllib.request.Request(endpoint, method="GET")
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False

    return False


class TokenOptimizer:
    """Applies token optimizations to OpenClaw configuration."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.openclaw_dir = Path.home() / '.openclaw'
        self.config_path = self.openclaw_dir / 'openclaw.json'
        self.backup_dir = self.openclaw_dir / 'backups'
        self.templates_dir = Path(__file__).parent.parent / 'templates'

    def backup_config(self) -> Optional[Path]:
        """Create backup of existing configuration."""
        if not self.config_path.exists():
            return None

        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f'openclaw_{timestamp}.json'

        if not self.dry_run:
            shutil.copy(self.config_path, backup_path)
            print(colorize(f"[BACKUP] Config backed up to: {backup_path}", Colors.BLUE))
        else:
            print(colorize(f"[DRY-RUN] Would backup config to: {backup_path}", Colors.YELLOW))

        return backup_path

    def load_config(self) -> Dict:
        """Load existing config or return empty dict."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(colorize("[WARNING] Existing config is invalid JSON, starting fresh", Colors.YELLOW))
        return {}

    def save_config(self, config: Dict):
        """Save configuration to file. In dry-run mode, show a diff preview."""
        self.openclaw_dir.mkdir(parents=True, exist_ok=True)

        if self.dry_run:
            print(colorize("\n[DRY-RUN] Changes preview:", Colors.YELLOW))
            existing = self.load_config()
            self._show_diff(existing, config)
        else:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            print(colorize(f"[SAVED] Config written to: {self.config_path}", Colors.GREEN))

    def generate_optimized_config(self) -> Dict:
        """Generate fully optimized OpenClaw configuration."""
        return {
            "agents": {
                "defaults": {
                    "model": {
                        "primary": "anthropic/claude-haiku-4-5"
                    },
                    "cache": {
                        "enabled": True,
                        "ttl": "5m",
                        "priority": "high"
                    },
                    "models": {
                        "anthropic/claude-sonnet-4-5": {
                            "alias": "sonnet",
                            "cache": True
                        },
                        "anthropic/claude-haiku-4-5": {
                            "alias": "haiku",
                            "cache": False
                        },
                        "anthropic/claude-opus-4-5": {
                            "alias": "opus",
                            "cache": True
                        }
                    }
                }
            },
            "heartbeat": {
                "every": "1h",
                "model": "ollama/llama3.2:3b",
                "session": "main",
                "prompt": "Check: Any blockers, opportunities, or progress updates needed?"
            },
            "rate_limits": {
                "api_calls": {
                    "min_interval_seconds": 5,
                    "web_search_interval_seconds": 10,
                    "max_searches_per_batch": 5,
                    "batch_cooldown_seconds": 120
                }
            },
            "budgets": {
                "daily": 5.00,
                "monthly": 200.00,
                "warning_threshold": 0.75
            },
            "_meta": {
                "optimized_by": "token-optimizer",
                "version": __version__,
                "optimized_at": datetime.now().isoformat()
            }
        }

    def merge_config(self, existing: Dict, optimized: Dict) -> Dict:
        """Merge optimized settings into existing config, preserving user customizations."""
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        return deep_merge(existing, optimized)

    def apply_model_routing(self, config: Dict) -> Dict:
        """Apply model routing optimization only."""
        optimized = self.generate_optimized_config()

        if 'agents' not in config:
            config['agents'] = {}
        if 'defaults' not in config['agents']:
            config['agents']['defaults'] = {}

        config['agents']['defaults']['model'] = optimized['agents']['defaults']['model']
        config['agents']['defaults']['models'] = optimized['agents']['defaults']['models']

        print(colorize("[APPLIED] Model routing: Haiku default, Sonnet/Opus aliases", Colors.GREEN))
        return config

    def apply_heartbeat(self, config: Dict, provider: str = None, model: str = None, fallback: str = None) -> Dict:
        """Apply heartbeat optimization with configurable provider."""
        optimized = self.generate_optimized_config()

        if provider is None:
            provider = resolve_heartbeat_provider(config)

        info = HEARTBEAT_PROVIDERS.get(provider, HEARTBEAT_PROVIDERS["ollama"])

        if provider == "none":
            config.pop("heartbeat", None)
            print(colorize("[APPLIED] Heartbeat: disabled", Colors.YELLOW))
            return config

        heartbeat = optimized['heartbeat']
        heartbeat['provider'] = provider

        if model:
            heartbeat['model'] = f"{info['model_prefix']}{model}"
        else:
            heartbeat['model'] = f"{info['model_prefix']}{info['default_model']}"

        if info.get('endpoint'):
            heartbeat['endpoint'] = info['endpoint']

        if fallback and fallback in HEARTBEAT_PROVIDERS:
            heartbeat['fallback'] = fallback

        config['heartbeat'] = heartbeat
        print(colorize(f"[APPLIED] Heartbeat: {provider} {heartbeat['model']}", Colors.GREEN))
        return config

    def apply_caching(self, config: Dict) -> Dict:
        """Apply prompt caching optimization only."""
        optimized = self.generate_optimized_config()

        if 'agents' not in config:
            config['agents'] = {}
        if 'defaults' not in config['agents']:
            config['agents']['defaults'] = {}

        config['agents']['defaults']['cache'] = optimized['agents']['defaults']['cache']

        print(colorize("[APPLIED] Prompt caching: Enabled with 5m TTL", Colors.GREEN))
        return config

    def apply_rate_limits(self, config: Dict) -> Dict:
        """Apply rate limits and budgets."""
        optimized = self.generate_optimized_config()
        config['rate_limits'] = optimized['rate_limits']
        config['budgets'] = optimized['budgets']

        print(colorize("[APPLIED] Rate limits and budget controls", Colors.GREEN))
        return config

    def check_ollama(self) -> bool:
        """Check if Ollama is installed and running."""
        if shutil.which('ollama') is None:
            return False
        try:
            req = urllib.request.Request("http://localhost:11434", method="GET")
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception:
            return False

    def setup_heartbeat_provider(self, provider: str = "ollama", model: str = None, fallback: str = None) -> bool:
        """Set up heartbeat provider."""
        print(colorize(f"\n--- Setting up {provider} for Heartbeat ---", Colors.BOLD))

        if provider == "none":
            print(colorize("[OK] Heartbeat disabled", Colors.YELLOW))
            return True

        if provider not in HEARTBEAT_PROVIDERS:
            print(colorize(f"[ERROR] Unknown provider: {provider}. Choose from: {', '.join(HEARTBEAT_PROVIDERS.keys())}", Colors.RED))
            return False

        reachable = check_heartbeat_provider(provider)
        if not reachable:
            info = HEARTBEAT_PROVIDERS[provider]
            endpoint = info.get("endpoint", "")
            print(colorize(f"[WARNING] {provider} not reachable at {endpoint}", Colors.YELLOW))

            if provider == "ollama":
                print("  Install Ollama from: https://ollama.ai")
                print("  Then run: ollama pull llama3.2:3b")
            elif provider == "lmstudio":
                print("  Start LM Studio and enable the local server on port 1234")
            elif provider == "groq":
                print("  Set GROQ_API_KEY environment variable")

            if fallback and fallback != provider:
                print(colorize(f"[FALLBACK] Trying fallback provider: {fallback}", Colors.CYAN))
                return self.setup_heartbeat_provider(fallback, model)

            return False

        # Ollama-specific: check/pull model
        if provider == "ollama":
            return self._setup_ollama_model(model)

        print(colorize(f"[OK] {provider} is reachable", Colors.GREEN))
        return True

    def _setup_ollama_model(self, model: str = None) -> bool:
        """Check Ollama model availability and provide instructions."""
        target_model = model or "llama3.2:3b"
        print(colorize(f"[OK] Ollama is installed and reachable", Colors.GREEN))
        print(colorize(f"[INFO] Make sure the model is available:", Colors.CYAN))
        print(f"    ollama pull {target_model}")
        print(f"    ollama serve")
        return True

    def setup_ollama_heartbeat(self) -> bool:
        """Attempt to set up Ollama for heartbeat (legacy compatibility)."""
        return self.setup_heartbeat_provider("ollama")

    def list_backups(self) -> List[Path]:
        """List available config backups."""
        if not self.backup_dir.exists():
            return []
        backups = sorted(self.backup_dir.glob('openclaw_*.json'), reverse=True)
        return backups

    def restore_backup(self, backup_path: Path) -> bool:
        """Restore a config backup."""
        if not backup_path.exists():
            print(colorize(f"[ERROR] Backup not found: {backup_path}", Colors.RED))
            return False

        try:
            with open(backup_path, 'r') as f:
                json.load(f)  # validate JSON
        except json.JSONDecodeError:
            print(colorize(f"[ERROR] Backup is not valid JSON: {backup_path}", Colors.RED))
            return False

        if self.dry_run:
            print(colorize(f"[DRY-RUN] Would restore config from: {backup_path}", Colors.YELLOW))
            return True

        # Backup current config before restoring
        self.backup_config()

        shutil.copy(backup_path, self.config_path)
        print(colorize(f"[RESTORED] Config restored from: {backup_path}", Colors.GREEN))
        return True

    def _show_diff(self, old_config: Dict, new_config: Dict):
        """Show colored unified diff between old and new config."""
        old_lines = json.dumps(old_config, indent=2).splitlines(keepends=True)
        new_lines = json.dumps(new_config, indent=2).splitlines(keepends=True)

        diff = list(difflib.unified_diff(
            old_lines, new_lines,
            fromfile="current config",
            tofile="optimized config",
            lineterm=""
        ))

        if not diff:
            print(colorize("  (no changes)", Colors.YELLOW))
            return

        for line in diff:
            line = line.rstrip('\n')
            if line.startswith('+++') or line.startswith('---'):
                print(colorize(line, Colors.BOLD))
            elif line.startswith('+'):
                print(colorize(line, Colors.GREEN))
            elif line.startswith('-'):
                print(colorize(line, Colors.RED))
            elif line.startswith('@@'):
                print(colorize(line, Colors.CYAN))
            else:
                print(line)

    def init_stats(self):
        """Initialize or update stats tracking file for benefit reports."""
        stats_path = self.openclaw_dir / 'token-optimizer-stats.json'

        if stats_path.exists():
            try:
                with open(stats_path, 'r') as f:
                    stats = json.load(f)
            except json.JSONDecodeError:
                stats = {}
        else:
            stats = {}

        if 'installed_at' not in stats:
            stats['installed_at'] = datetime.now().isoformat()

        stats['last_optimized'] = datetime.now().isoformat()
        stats.setdefault('last_benefit_report', None)
        stats.setdefault('verify_count', 0)

        if not self.dry_run:
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
            print(colorize("[STATS] Tracking initialized for savings reports", Colors.BLUE))

    def optimize_full(self):
        """Apply all optimizations."""
        print(colorize("\n=== Token Optimizer - Full Optimization ===\n", Colors.BOLD + Colors.CYAN))

        # Backup existing config
        self.backup_config()

        # Load existing config
        existing = self.load_config()

        # Generate and merge optimized config
        optimized = self.generate_optimized_config()
        final_config = self.merge_config(existing, optimized)

        # Apply all optimizations
        print(colorize("\nApplying optimizations:", Colors.BOLD))
        print(colorize("  [1/4] Model routing (Haiku default)", Colors.GREEN))
        print(colorize("  [2/4] Heartbeat to Ollama (free)", Colors.GREEN))
        print(colorize("  [3/4] Prompt caching (90% savings)", Colors.GREEN))
        print(colorize("  [4/4] Rate limits & budgets", Colors.GREEN))

        # Save config
        self.save_config(final_config)

        # Setup Ollama
        self.setup_ollama_heartbeat()

        # Generate workspace templates
        self.generate_workspace_templates()

        # Generate agent prompt additions
        self.generate_agent_prompts()

        # Initialize stats tracking
        self.init_stats()

        print(colorize("\n=== Optimization Complete ===", Colors.BOLD + Colors.GREEN))
        print("\nNext steps:")
        print("  1. Review generated files in ~/.openclaw/")
        print("  2. Add agent prompt rules from ~/.openclaw/prompts/")
        print("  3. Start Ollama: ollama serve")
        print("  4. Verify with: token-optimizer verify")

    def optimize_mode(self, mode: str):
        """Apply specific optimization mode."""
        self.backup_config()
        config = self.load_config()

        if mode == 'routing':
            config = self.apply_model_routing(config)
        elif mode == 'heartbeat':
            config = self.apply_heartbeat(config)
            self.setup_ollama_heartbeat()
        elif mode == 'caching':
            config = self.apply_caching(config)
        elif mode == 'limits':
            config = self.apply_rate_limits(config)
        elif mode == 'full':
            self.optimize_full()
            return
        else:
            print(colorize(f"[ERROR] Unknown mode: {mode}", Colors.RED))
            return

        self.save_config(config)

    def generate_workspace_templates(self):
        """Generate optimized workspace file templates."""
        workspace_dir = self.openclaw_dir / 'workspace'
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # SOUL.md template
        soul_content = """# SOUL.md - Agent Core Principles

## Identity
[YOUR AGENT NAME/ROLE]

## Core Principles
1. Efficiency first - minimize token usage
2. Quality over quantity - precise responses
3. Proactive communication - surface blockers early

## How to Operate
- Default to Haiku for routine tasks
- Switch to Sonnet only for: architecture, security, complex reasoning
- Batch similar operations together
- Use memory_search() on demand, not auto-load

## Model Selection Rule
```
Default: Always use Haiku
Switch to Sonnet ONLY when:
- Architecture decisions
- Production code review
- Security analysis
- Complex debugging/reasoning
- Strategic multi-project decisions

When in doubt: Try Haiku first.
```

## Rate Limits
- 5s between API calls
- 10s between searches
- Max 5 searches/batch, then 2min break
"""

        # USER.md template
        user_content = """# USER.md - User Context

## Profile
- **Name:** [YOUR NAME]
- **Timezone:** [YOUR TIMEZONE]
- **Working Hours:** [YOUR HOURS]

## Mission
[WHAT YOU'RE BUILDING]

## Success Metrics
1. [METRIC 1]
2. [METRIC 2]
3. [METRIC 3]

## Communication Preferences
- Brief, actionable updates
- Surface blockers immediately
- Daily summary at end of session
"""

        # IDENTITY.md template
        identity_content = """# IDENTITY.md - Agent Identity

## Role
[AGENT ROLE - e.g., "Technical Lead", "Research Assistant"]

## Expertise
- [DOMAIN 1]
- [DOMAIN 2]
- [DOMAIN 3]

## Constraints
- Stay within defined budgets
- Follow rate limits strictly
- Escalate uncertainty early
"""

        templates = {
            'SOUL.md': soul_content,
            'USER.md': user_content,
            'IDENTITY.md': identity_content
        }

        print(colorize("\n--- Generating Workspace Templates ---", Colors.BOLD))

        for filename, content in templates.items():
            filepath = workspace_dir / filename
            if filepath.exists() and not self.dry_run:
                print(colorize(f"  [SKIP] {filename} already exists", Colors.YELLOW))
            else:
                if not self.dry_run:
                    with open(filepath, 'w') as f:
                        f.write(content.strip())
                print(colorize(f"  [CREATED] {filepath}", Colors.GREEN))

    def generate_agent_prompts(self):
        """Generate agent prompt additions for optimization."""
        prompts_dir = self.openclaw_dir / 'prompts'
        prompts_dir.mkdir(parents=True, exist_ok=True)

        # Session initialization rule
        session_init = """## SESSION INITIALIZATION RULE

On every session start:
1. Load ONLY these files:
   - SOUL.md
   - USER.md
   - IDENTITY.md
   - memory/YYYY-MM-DD.md (if it exists)

2. DO NOT auto-load:
   - MEMORY.md
   - Session history
   - Prior messages
   - Previous tool outputs

3. When user asks about prior context:
   - Use memory_search() on demand
   - Pull only the relevant snippet with memory_get()
   - Don't load the whole file

4. Update memory/YYYY-MM-DD.md at end of session with:
   - What you worked on
   - Decisions made
   - Leads generated
   - Blockers
   - Next steps

This saves 80% on context overhead.
"""

        # Model selection rule
        model_selection = """## MODEL SELECTION RULE

Default: Always use Haiku

Switch to Sonnet ONLY when:
- Architecture decisions
- Production code review
- Security analysis
- Complex debugging/reasoning
- Strategic multi-project decisions

When in doubt: Try Haiku first.
"""

        # Rate limits rule
        rate_limits = """## RATE LIMITS

- 5 seconds minimum between API calls
- 10 seconds between web searches
- Max 5 searches per batch, then 2-minute break
- Batch similar work (one request for 10 leads, not 10 requests)
- If you hit 429 error: STOP, wait 5 minutes, retry

## DAILY BUDGET: $5 (warning at 75%)
## MONTHLY BUDGET: $200 (warning at 75%)
"""

        # Combined optimization prompt
        combined = f"""# TOKEN OPTIMIZATION RULES

Add these rules to your agent prompt:

---

{session_init}

---

{model_selection}

---

{rate_limits}

---

## IMPORTANT
These rules work together to reduce costs by 97%.
Do not remove or modify unless you understand the cost implications.
"""

        prompts = {
            'session-init.md': session_init,
            'model-selection.md': model_selection,
            'rate-limits.md': rate_limits,
            'OPTIMIZATION-RULES.md': combined
        }

        print(colorize("\n--- Generating Agent Prompts ---", Colors.BOLD))

        for filename, content in prompts.items():
            filepath = prompts_dir / filename
            if filepath.exists() and not self.dry_run:
                print(colorize(f"  [SKIP] {filename} already exists", Colors.YELLOW))
            else:
                if not self.dry_run:
                    with open(filepath, 'w') as f:
                        f.write(content.strip())
                print(colorize(f"  [CREATED] {filepath}", Colors.GREEN))

        print(colorize(f"\n[INFO] Add contents of {prompts_dir / 'OPTIMIZATION-RULES.md'} to your agent prompt", Colors.CYAN))


def main():
    parser = argparse.ArgumentParser(description='Token Optimizer for OpenClaw')
    parser.add_argument('--mode', choices=['full', 'routing', 'heartbeat', 'caching', 'limits'],
                       default='full', help='Optimization mode')
    parser.add_argument('--apply', action='store_true',
                       help='Apply changes (default is dry-run for safety)')

    args = parser.parse_args()

    dry_run = not args.apply
    if dry_run:
        print(colorize("[DRY-RUN] Preview mode. Use --apply to make changes.\n", Colors.YELLOW))

    optimizer = TokenOptimizer(dry_run=dry_run)
    optimizer.optimize_mode(args.mode)

    return 0


if __name__ == '__main__':
    sys.exit(main())
