"""
reefwatch.engines.sigma_engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Evaluates Sigma rules against log entries with proper condition parsing.
"""

import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from reefwatch._common import logger

_NOT_OF = object()  # Sentinel: expression is not an "of" construct


def _tokenize_condition(condition: str) -> list[str]:
    """Tokenize a Sigma condition string into operators and operands."""
    # Handle "1 of xxx*" and "all of xxx" as single tokens
    condition = re.sub(r'\b(1 of \S+)', lambda m: f'__OF_{m.group(1)}__', condition)
    condition = re.sub(r'\b(all of \S+)', lambda m: f'__OF_{m.group(1)}__', condition)
    # Tokenize
    tokens = []
    for part in re.split(r'(\band\b|\bor\b|\bnot\b|\(|\))', condition):
        part = part.strip()
        if part:
            # Restore "of" expressions
            if part.startswith('__OF_') and part.endswith('__'):
                part = part[5:-2]
            tokens.append(part)
    return tokens


def _eval_tokens(tokens: list[str], item_results: dict[str, bool], resolve_of) -> bool:  # noqa: E501
    """Simple recursive-descent boolean evaluator for Sigma conditions."""
    pos = [0]  # mutable index

    def peek():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def consume():
        t = tokens[pos[0]]
        pos[0] += 1
        return t

    def parse_expr() -> bool:
        result = parse_and()
        while peek() == "or":
            consume()
            right = parse_and()  # Must evaluate (consume tokens) before combining
            result = result or right
        return result

    def parse_and() -> bool:
        result = parse_not()
        while peek() == "and":
            consume()
            right = parse_not()  # Must evaluate (consume tokens) before combining
            result = result and right
        return result

    def parse_not() -> bool:
        if peek() == "not":
            consume()
            return not parse_atom()
        return parse_atom()

    def parse_atom() -> bool:
        t = peek()
        if t == "(":
            consume()
            result = parse_expr()
            if peek() == ")":
                consume()
            return result
        consume()
        # Check if it's an "of" expression
        of_result = resolve_of(t)
        if of_result is not _NOT_OF:
            return of_result
        # Otherwise it's a named detection item
        return item_results.get(t, False)

    if not tokens:
        return False
    return parse_expr()


class SigmaEngine:
    """Evaluates Sigma rules against log entries with proper condition parsing."""

    SEVERITY_MAP = {
        "informational": "LOW",
        "low": "LOW",
        "medium": "MEDIUM",
        "high": "HIGH",
        "critical": "CRITICAL",
    }

    # Map log entry sources to Sigma logsource categories
    _SOURCE_CATEGORIES = {
        "auth.log": {"auth", "authentication"},
        "syslog": {"syslog"},
        "kern.log": {"kernel"},
        "daemon.log": {"daemon", "syslog"},
        "system.log": {"syslog"},
        "journald": {"syslog", "auth", "process_creation"},
        "unified_log": {"syslog", "process_creation"},
    }

    def __init__(self, config: dict):
        sigma_cfg = config.get("engines", {}).get("sigma", {})
        self.enabled = sigma_cfg.get("enabled", True)
        self.log_sources = set(sigma_cfg.get("log_sources", []))
        base = Path(__file__).parent.parent.parent
        raw_rules = sigma_cfg.get("rules_dir", "rules/sigma")
        if Path(raw_rules).is_absolute():
            candidate = Path(raw_rules).resolve()
        else:
            candidate = (base / raw_rules).resolve()
            if not candidate.is_relative_to(base.resolve()):
                logger.error(f"Sigma rules_dir escapes package root: {raw_rules}")
                self.enabled = False
                candidate = base / "rules" / "sigma"
        self.rules_dir = candidate
        self._rules_data: list[dict] = []

        if self.enabled:
            self._load_rules()

    def _load_rules(self):
        """Load sigma rules as YAML."""
        if not self.rules_dir.exists():
            logger.warning(f"Sigma rules dir not found: {self.rules_dir}")
            self.enabled = False
            return

        rule_files = list(self.rules_dir.glob("**/*.yml")) + list(
            self.rules_dir.glob("**/*.yaml")
        )

        for rf in rule_files:
            try:
                with open(rf) as f:
                    docs = list(yaml.safe_load_all(f))
                    for doc in docs:
                        if doc and "detection" in doc:
                            logsource = doc.get("logsource", {})
                            self._rules_data.append(
                                {
                                    "file": str(rf),
                                    "title": doc.get("title", rf.stem),
                                    "level": doc.get("level", "medium"),
                                    "description": doc.get("description", ""),
                                    "detection": doc["detection"],
                                    "logsource_category": logsource.get("category", ""),
                                }
                            )
            except Exception as e:
                logger.debug(f"Failed to load sigma rule {rf}: {e}")

        logger.info(f"SigmaEngine: loaded {len(self._rules_data)} rules")

    @staticmethod
    def _match_detection_item(item, line: str, log_entry: dict | None = None) -> bool:
        """Check if a single detection item (list or dict) matches the log line.

        When *log_entry* is provided (structured data), field names in selection
        dicts are matched against entry keys for field-aware evaluation.
        Falls back to substring matching against the raw line when the field is
        not present in the entry.
        """
        if isinstance(item, list):
            # Keyword list -- any keyword matches (OR)
            return any(
                str(kw).lower() in line
                for kw in item
            )
        elif isinstance(item, dict):
            # Selection dict -- all field patterns must match (AND across fields)
            for field, patterns in item.items():
                # Determine the value to match against
                field_value = None
                if log_entry:
                    # Try exact field name, then common Sigma mappings
                    field_value = log_entry.get(field) or log_entry.get(
                        field.lower()
                    )
                # Normalise to string for comparison
                target = str(field_value).lower() if field_value is not None else line

                if isinstance(patterns, list):
                    if not any(
                        str(p).lower() in target
                        for p in patterns
                    ):
                        return False
                elif isinstance(patterns, str):
                    if patterns.lower() not in target:
                        return False
            return True
        return False

    @staticmethod
    def _evaluate_condition(
        condition: str,
        detection: dict,
        line: str,
        log_entry: dict | None = None,
    ) -> bool:
        """Evaluate a Sigma condition expression against named detection items.

        Supports: named items, 'and', 'or', 'not', '1 of <prefix>*',
        'all of <prefix>*', 'all of them', '1 of them', parentheses.
        """
        # Build a map of resolved detection item results
        item_results: dict[str, bool] = {}
        for key, value in detection.items():
            if key == "condition":
                continue
            item_results[key] = SigmaEngine._match_detection_item(
                value, line, log_entry
            )

        # Handle "1 of <prefix>*" and "all of <prefix>*" / "all of them"
        def resolve_of_expr(expr: str) -> bool:
            expr = expr.strip()
            if expr.startswith("1 of "):
                target = expr[5:].strip()
                return _match_of("any", target, item_results)
            if expr.startswith("all of "):
                target = expr[7:].strip()
                return _match_of("all", target, item_results)
            return _NOT_OF  # Not an "of" expression

        def _match_of(mode: str, target: str, results: dict) -> bool:
            if target == "them":
                values = list(results.values())
            elif target.endswith("*"):
                prefix = target[:-1]
                values = [v for k, v in results.items() if k.startswith(prefix)]
            else:
                values = [results.get(target, False)]
            if not values:
                return False
            if mode == "any":
                return any(values)
            return all(values)

        # Tokenize the condition for boolean evaluation
        # Replace known item names with their boolean results
        tokens = _tokenize_condition(condition)
        return _eval_tokens(tokens, item_results, resolve_of_expr)

    def _entry_categories(self, log_entry: dict) -> set[str]:
        """Derive Sigma logsource categories applicable to a log entry."""
        source = log_entry.get("source", "")
        cats = self._SOURCE_CATEGORIES.get(source, set())
        # If log_sources configured, intersect; otherwise allow all
        if self.log_sources:
            return cats & self.log_sources
        return cats

    def evaluate(self, log_entry: dict) -> list[dict]:
        """Check a log entry against all sigma rules using condition evaluation."""
        if not self.enabled:
            return []

        alerts = []
        line = log_entry.get("line", "").lower()
        entry_cats = self._entry_categories(log_entry)

        for rule in self._rules_data:
            # Skip rules whose logsource category doesn't match this entry
            rule_cat = rule.get("logsource_category", "")
            if rule_cat and entry_cats and rule_cat not in entry_cats:
                continue

            detection = rule["detection"]
            condition = detection.get("condition", "")

            try:
                if not condition:
                    # No condition: match if any detection item matches (legacy behavior)
                    matched = any(
                        self._match_detection_item(v, line, log_entry)
                        for k, v in detection.items()
                        if k != "condition"
                    )
                else:
                    matched = self._evaluate_condition(
                        condition, detection, line, log_entry
                    )
            except Exception as e:
                logger.debug(
                    f"Error evaluating Sigma rule '{rule['title']}': {e}"
                )
                continue

            if matched:
                alerts.append(
                    {
                        "type": rule["title"],
                        "severity": self.SEVERITY_MAP.get(
                            rule["level"].lower(), "MEDIUM"
                        ),
                        "source": log_entry.get("source", "logs"),
                        "detail": line[:300],
                        "rule": f"sigma/{Path(rule['file']).stem}",
                        "time": log_entry.get(
                            "timestamp", datetime.now(timezone.utc).isoformat()
                        ),
                    }
                )

        return alerts
