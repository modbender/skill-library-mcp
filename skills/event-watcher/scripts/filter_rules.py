from __future__ import annotations

import re
from typing import Any, Dict, List


def get_field(data: dict, path: str) -> Any:
    cur = data
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def eval_rule(event: dict, rule: Dict[str, Any]) -> bool:
    field = rule.get("field")
    op = rule.get("op")
    value = rule.get("value")
    actual = get_field(event, field) if field else None

    if op == "==":
        return actual == value
    if op == "!=":
        return actual != value
    if op == ">":
        return actual is not None and actual > value
    if op == "<":
        return actual is not None and actual < value
    if op == ">=":
        return actual is not None and actual >= value
    if op == "<=":
        return actual is not None and actual <= value
    if op == "in":
        return actual in value if isinstance(value, (list, tuple, set)) else False
    if op == "contains":
        return value in actual if isinstance(actual, (list, str)) else False
    if op == "regex":
        if actual is None:
            return False
        return re.search(str(value), str(actual)) is not None

    return False


def match_filter(event: dict, rule: Dict[str, Any] | None) -> bool:
    if not rule:
        return True

    if "all" in rule:
        rules = rule.get("all", [])
        return all(match_filter(event, r) for r in rules)

    if "any" in rule:
        rules = rule.get("any", [])
        return any(match_filter(event, r) for r in rules)

    return eval_rule(event, rule)
