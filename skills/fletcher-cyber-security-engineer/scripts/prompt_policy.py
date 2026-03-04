#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict


POLICY_PATH = Path.home() / ".openclaw" / "security" / "prompt-policy.json"


def load_policy() -> Dict[str, object]:
    if not POLICY_PATH.exists():
        return {"require_confirmation_for_untrusted": False}
    try:
        raw = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {"require_confirmation_for_untrusted": False}
        return {
            "require_confirmation_for_untrusted": bool(
                raw.get("require_confirmation_for_untrusted", False)
            )
        }
    except Exception:
        return {"require_confirmation_for_untrusted": False}

