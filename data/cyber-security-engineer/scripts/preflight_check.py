#!/usr/bin/env python3
"""
Preflight validation for the cyber-security-engineer skill.

This is intentionally conservative: it does not modify system state. It validates
that required files and tooling exist before enabling runtime hooks or enforcing
privileged execution.
"""

from __future__ import annotations

import json
import os
import shutil
import stat
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _exists_any(names: List[str]) -> Tuple[bool, List[str]]:
    found = [n for n in names if shutil.which(n)]
    return (len(found) > 0), found


def _mode_str(path: Path) -> str:
    try:
        return oct(path.stat().st_mode & 0o777)
    except Exception:
        return "unknown"


def _is_hardened(path: Path) -> bool:
    try:
        mode = path.stat().st_mode & 0o777
        return (mode & 0o077) == 0
    except Exception:
        return False


def main() -> int:
    home = Path.home()
    oc = home / ".openclaw"
    sec = oc / "security"

    required_policy_files = [
        sec / "command-policy.json",
        sec / "approved_ports.json",
        sec / "egress_allowlist.json",
    ]

    optional_files = [
        oc / "openclaw.json",
        oc / "env",
        sec / "prompt-policy.json",
        sec / "root-session-state.json",
    ]

    ok_openclaw, found_openclaw = _exists_any(["openclaw"])
    ok_python, found_python = _exists_any(["python3", "python"])
    ok_ports, found_ports = _exists_any(["lsof", "ss", "netstat"])

    hook = oc / "bin" / "sudo"
    hook_ok = hook.exists() and os.access(str(hook), os.X_OK)

    missing_required = [str(p) for p in required_policy_files if not p.exists()]
    missing_optional = [str(p) for p in optional_files if not p.exists()]

    env_path = oc / "env"
    env_perms_ok = True
    env_perms_mode = "missing"
    if env_path.exists():
        env_perms_mode = _mode_str(env_path)
        env_perms_ok = _is_hardened(env_path)

    config_path = oc / "openclaw.json"
    config_perms_ok = True
    config_perms_mode = "missing"
    if config_path.exists():
        config_perms_mode = _mode_str(config_path)
        config_perms_ok = _is_hardened(config_path)

    require_policy = os.environ.get("OPENCLAW_REQUIRE_POLICY_FILES") == "1"
    critical_fail = []
    if not ok_openclaw:
        critical_fail.append("openclaw_not_found")
    if not ok_python:
        critical_fail.append("python_not_found")
    if not ok_ports:
        critical_fail.append("no_port_discovery_tool")
    if require_policy and missing_required:
        critical_fail.append("missing_required_policy_files")

    report: Dict[str, Any] = {
        "status": "ok" if not critical_fail else "fail",
        "critical": critical_fail,
        "require_policy_files": require_policy,
        "tools": {
            "openclaw": {"ok": ok_openclaw, "found": found_openclaw},
            "python": {"ok": ok_python, "found": found_python},
            "port_discovery": {"ok": ok_ports, "found": found_ports},
        },
        "paths": {
            "openclaw_dir": str(oc),
            "security_dir": str(sec),
            "runtime_hook": {"path": str(hook), "installed": hook_ok},
        },
        "policy_files": {
            "required": [str(p) for p in required_policy_files],
            "missing_required": missing_required,
        },
        "optional_files": {
            "missing_optional": missing_optional,
        },
        "permissions": {
            "env": {"path": str(env_path), "mode": env_perms_mode, "hardened": env_perms_ok},
            "openclaw_json": {"path": str(config_path), "mode": config_perms_mode, "hardened": config_perms_ok},
        },
        "next_steps": [
            "Run bootstrap script if OpenClaw is not configured.",
            "Generate and prune approved ports baseline via generate_approved_ports.py.",
            "Review and customize command-policy.json and egress_allowlist.json templates.",
            "Install runtime hook only after policy files are reviewed.",
        ],
    }

    sys.stdout.write(json.dumps(report, indent=2, sort_keys=True))
    sys.stdout.write("\n")

    return 0 if not critical_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())

