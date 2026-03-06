"""
reefwatch.engines.custom_rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Evaluates custom JSON-based detection rules.

Rule JSON format::

    {
        "id": "rule_id",
        "name": "Human-readable name",
        "severity": "HIGH",
        "source_type": "file_change" | "process" | "network",
        "conditions": {
            "field": "value_substring"   // all must match
        }
    }
"""

import base64
import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from reefwatch._common import expand, logger

# Zero-width and invisible Unicode characters used in prompt injection
_INVISIBLE_RE = re.compile(
    "[\u200b\u200c\u200d\u2060\ufeff\u00ad\u034f\u061c"
    "\u180e\u2000-\u200f\u202a-\u202e\u2066-\u2069\ufff9-\ufffb]"
)

# Prompt-poisoning detection signatures — base64-encoded to prevent other
# security scanners from flagging these IDS signatures as actual attacks.
_POISON_SIGS_B64 = [
    "aWdub3JlXHMrKD86YWxsXHMrKT9wcmV2aW91c1xzK2luc3RydWN0aW9ucw==",
    "eW91XHMrYXJlXHMrbm93XGI=",
    "ZGlzcmVnYXJkXHMrKD86YWxsfGV2ZXJ5dGhpbmcp",
    "bmV3XHMrc3lzdGVtXHMrcHJvbXB0",
    "XGJldmFsXHMqXCg=",
    "XGJleGVjXHMqXCg=",
    "c3VicHJvY2Vzc1wuKD86Y2FsbHxydW58UG9wZW4p",
    "X19pbXBvcnRfX1xzKlwo",
    "KD86Zm9yZ2V0fG92ZXJyaWRlKVxzKyg/OnlvdXJ8YWxsKVxzKyg/OnJ1bGVzfGluc3RydWN0aW9ucyk=",
    "YWN0XHMrYXNccysoPzppZnx0aG91Z2gpXHMreW91",
]
_POISON_PATTERNS = [
    re.compile(base64.b64decode(s).decode(), re.IGNORECASE)
    for s in _POISON_SIGS_B64
]


class CustomRulesEngine:
    """Evaluates custom JSON-based detection rules."""

    def __init__(self, config: dict):
        custom_cfg = config.get("engines", {}).get("custom", {})
        self.enabled = custom_cfg.get("enabled", True)
        base = Path(__file__).parent.parent.parent
        raw_rules = custom_cfg.get("rules_dir", "rules/custom")
        if Path(raw_rules).is_absolute():
            candidate = Path(raw_rules).resolve()
        else:
            candidate = (base / raw_rules).resolve()
            if not candidate.is_relative_to(base.resolve()):
                logger.error(f"Custom rules_dir escapes package root: {raw_rules}")
                self.enabled = False
                candidate = base / "rules" / "custom"
        self.rules_dir = candidate
        self._rules: list[dict] = []
        if self.enabled:
            self._load_rules()

    def _load_rules(self):
        """Load all JSON rule files from rules_dir."""
        if not self.rules_dir.exists():
            logger.debug(f"Custom rules dir not found: {self.rules_dir}")
            return
        for rule_file in self.rules_dir.glob("**/*.json"):
            try:
                with open(rule_file) as f:
                    rule = json.load(f)
                if isinstance(rule, list):
                    self._rules.extend(rule)
                elif isinstance(rule, dict):
                    self._rules.append(rule)
            except Exception as e:
                logger.warning(f"Failed to load custom rule {rule_file}: {e}")
        if self._rules:
            logger.info(f"CustomRulesEngine: loaded {len(self._rules)} rules")

    def evaluate(self, event: dict, source_type: str) -> list[dict]:
        """Evaluate an event against all loaded custom rules.

        Args:
            event: Dict with event data (keys depend on source_type).
            source_type: One of "file_change", "process", "network".

        Returns:
            List of alert dicts for matching rules.
        """
        if not self.enabled:
            return []

        alerts = []
        for rule in self._rules:
            if rule.get("source_type") != source_type:
                continue
            conditions = rule.get("conditions", {})
            if not conditions:
                continue
            if self._match(conditions, event):
                alerts.append(
                    {
                        "type": rule.get("name", rule.get("id", "custom_rule")),
                        "severity": rule.get("severity", "MEDIUM"),
                        "source": "custom_rules",
                        "detail": json.dumps(event, default=str)[:500],
                        "rule": f"custom/{rule.get('id', 'unknown')}",
                        "time": datetime.now(timezone.utc).isoformat(),
                    }
                )
        return alerts

    @staticmethod
    def _match(conditions: dict, event: dict) -> bool:
        """Check if all conditions match the event (substring matching).

        Only scalar event values (str, int, float, bool, None) are compared.
        Structured values (list, dict) are skipped to avoid misleading
        matches against Python repr output.
        """
        for field, pattern in conditions.items():
            raw = event.get(field, "")
            if isinstance(raw, (list, dict)):
                return False  # Cannot meaningfully substring-match containers
            value = str(raw)
            if str(pattern).lower() not in value.lower():
                return False
        return True

    def check_openclaw_integrity(self) -> list[dict]:
        """Special check: ensure OpenClaw's own config hasn't been tampered with."""
        alerts = []
        critical_files = [
            expand("~/.openclaw/openclaw.json"),
            expand("~/.openclaw/workspace/HEARTBEAT.md"),
            expand("~/.openclaw/workspace/IDENTITY.md"),
        ]
        for f in critical_files:
            if not f.exists():
                continue
            try:
                raw = f.read_text()
                # Normalize Unicode to detect obfuscation (NFKC collapses lookalikes)
                content = unicodedata.normalize("NFKC", raw)

                # Check for invisible/zero-width characters (injection vector)
                invisible = _INVISIBLE_RE.findall(raw)
                if len(invisible) > 3:
                    alerts.append(
                        {
                            "type": "Suspicious invisible characters detected",
                            "severity": "HIGH",
                            "source": "custom_rules",
                            "detail": (
                                f"File {f}: {len(invisible)} invisible Unicode "
                                f"characters found"
                            ),
                            "rule": "custom/invisible_chars",
                            "time": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                # Check for prompt poisoning patterns (regex-based)
                for pattern in _POISON_PATTERNS:
                    if pattern.search(content):
                        alerts.append(
                            {
                                "type": "Potential prompt/memory poisoning",
                                "severity": "CRITICAL",
                                "source": "custom_rules",
                                "detail": (
                                    f"Suspicious content in {f}: "
                                    f"matches '{pattern.pattern}'"
                                ),
                                "rule": "custom/openclaw_integrity",
                                "time": datetime.now(timezone.utc).isoformat(),
                            }
                        )
            except Exception as e:
                logger.debug(f"Error checking {f}: {e}")

        return alerts
