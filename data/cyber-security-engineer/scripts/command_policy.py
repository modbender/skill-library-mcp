#!/usr/bin/env python3
import json
import re
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Tuple


POLICY_PATH = Path.home() / ".openclaw" / "security" / "command-policy.json"


def _load_policy() -> Dict[str, object]:
    if not POLICY_PATH.exists():
        return {}
    try:
        raw = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _compile_patterns(items: object) -> List[re.Pattern]:
    if not isinstance(items, list):
        return []
    out: List[re.Pattern] = []
    for s in items:
        if not isinstance(s, str) or not s.strip():
            continue
        try:
            out.append(re.compile(s))
        except re.error:
            continue
    return out


def _match_any(patterns: List[re.Pattern], text: str) -> Optional[str]:
    for p in patterns:
        if p.search(text):
            return p.pattern
    return None


def evaluate_command(argv: List[str]) -> Dict[str, object]:
    """
    Evaluate the command argv against an optional allow/deny policy.

    Policy format (~/.openclaw/security/command-policy.json):
      {
        "allow": ["^apt\\b", "^brew\\b"],
        "deny":  ["\\brm\\s+-rf\\b"]
      }

    Behavior:
    - If policy file is missing: allow.
    - If deny matches: block.
    - If allow list is non-empty: require allow match.
    """
    cmd_str = shlex.join(argv) if argv else ""
    pol = _load_policy()
    allow = _compile_patterns(pol.get("allow"))
    deny = _compile_patterns(pol.get("deny"))

    deny_match = _match_any(deny, cmd_str)
    if deny_match:
        return {"allowed": False, "reason": "deny_match", "pattern": deny_match}

    if allow:
        allow_match = _match_any(allow, cmd_str)
        if not allow_match:
            return {"allowed": False, "reason": "not_in_allowlist", "pattern": None}
        return {"allowed": True, "reason": "allow_match", "pattern": allow_match}

    return {"allowed": True, "reason": "no_policy_or_allow_empty", "pattern": None}

