"""Skill-level runner: parses NL query and fetches public web pages."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def run(context: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
    from openclaw_automation.engine import AutomationEngine
    from openclaw_automation.nl import parse_query_to_run, resolve_script_dir

    query = str(inputs.get("query", ""))
    if not query:
        return {"ok": False, "error": "missing 'query' in inputs"}

    parsed = parse_query_to_run(query)
    engine = AutomationEngine(_REPO_ROOT)
    script_dir = resolve_script_dir(_REPO_ROOT, parsed.script_dir)

    result = engine.run(script_dir, parsed.inputs)
    result["parsed_notes"] = parsed.notes
    return result
