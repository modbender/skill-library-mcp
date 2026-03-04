#!/usr/bin/env python3
"""
OpenClaw LaunchAgent Manager — List, classify, prune LaunchAgents; analyze config and gateway.

- Keeps only OpenClaw-related LaunchAgents; can unload/delete others.
- Analyzes openclaw.json: ensures the proper gateway LaunchAgent remains connected and tokens match.
- Can run gateway-guard status to verify running gateway auth matches config; suggests fixes.
"""

import json
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
OPENCLAW_HOME = Path(os.environ.get("OPENCLAW_HOME", str(Path.home() / ".openclaw")))


def openclaw_config_path():
    return Path(OPENCLAW_HOME) / "openclaw.json"


def load_openclaw_config():
    """Load openclaw.json; return (path, data) or (None, {})."""
    p = openclaw_config_path()
    if not p.exists():
        return None, {}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return p, json.load(f)
    except Exception:
        return p, {}


def gateway_config_from_openclaw(data: dict) -> dict:
    """Extract gateway.port and gateway.auth from openclaw.json data. Return dict with port, mode, secret_set, config_ok."""
    gateway = data.get("gateway") or {}
    auth = gateway.get("auth") or {}
    mode = auth.get("mode", "token")
    port = int(gateway.get("port", 18789))
    secret = auth.get("token") if mode == "token" else auth.get("password")
    return {
        "port": port,
        "mode": mode,
        "secret_set": bool(secret),
        "config_ok": True,
        "config_path": str(openclaw_config_path()),
    }


def find_gateway_plist(agents: list) -> Optional[dict]:
    """From list_agents() output, return the main gateway LaunchAgent (runs openclaw gateway), not guard/watchdog."""
    for a in agents:
        if not a.get("openclaw"):
            continue
        label = (a.get("label") or "").lower()
        if "guard" in label or "watchdog" in label:
            continue
        if "gateway" in label:
            return a
    return None


def gateway_guard_status_json() -> Optional[dict]:
    """Run gateway_guard.py status --json; return parsed dict or None."""
    guard_script = Path(OPENCLAW_HOME) / "workspace" / "skills" / "gateway-guard" / "scripts" / "gateway_guard.py"
    if not guard_script.exists():
        return None
    try:
        r = subprocess.run(
            [sys.executable, str(guard_script), "status", "--json"],
            env={**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)},
            capture_output=True,
            text=True,
            timeout=12,
            cwd=str(OPENCLAW_HOME),
        )
        if r.returncode is None or not r.stdout.strip():
            return None
        return json.loads(r.stdout.strip())
    except Exception:
        return None


def load_agent(plist_path: str) -> bool:
    """Load a LaunchAgent by plist path. Return True on success."""
    try:
        r = subprocess.run(
            ["launchctl", "load", plist_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.returncode == 0
    except Exception:
        return False


def is_openclaw_plist(plist_path: Path, data: dict) -> bool:
    """True if this plist is OpenClaw-related (keep it)."""
    label = (data.get("Label") or "").strip().lower()
    if "openclaw" in label or label.startswith("com.openclaw."):
        return True
    args = data.get("ProgramArguments") or []
    for a in args:
        if "openclaw" in str(a).lower():
            return True
    # Path of plist under openclaw workspace
    try:
        p = plist_path.resolve()
        if OPENCLAW_HOME.resolve() in p.parents or "openclaw" in str(p).lower():
            return True
    except Exception:
        pass
    return False


def load_plist_safe(path: Path) -> dict:
    """Load plist; return {} on error."""
    try:
        with open(path, "rb") as f:
            return plistlib.load(f)
    except Exception:
        return {}


def list_agents():
    """Scan LaunchAgents dir; return list of {path, label, openclaw: bool, loaded: bool}."""
    if not LAUNCH_AGENTS_DIR.exists():
        return []
    out = []
    for plist_path in sorted(LAUNCH_AGENTS_DIR.glob("*.plist")):
        data = load_plist_safe(plist_path)
        label = data.get("Label") or plist_path.stem
        openclaw = is_openclaw_plist(plist_path, data)
        # Check if loaded: launchctl list LABEL
        try:
            r = subprocess.run(
                ["launchctl", "list", label],
                capture_output=True,
                text=True,
                timeout=5,
            )
            loaded = r.returncode == 0 and label in (r.stdout or "")
        except Exception:
            loaded = False
        out.append({
            "path": str(plist_path),
            "label": label,
            "openclaw": openclaw,
            "loaded": loaded,
        })
    return out


def unload_agent(label: str) -> bool:
    """Unload one LaunchAgent by label. Return True on success."""
    try:
        r = subprocess.run(
            ["launchctl", "unload", str(LAUNCH_AGENTS_DIR / f"{label}.plist")],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return r.returncode == 0
    except Exception:
        return False


def run_config_check(agents: list, json_out: bool, fix: bool) -> int:
    """Analyze openclaw.json and gateway LaunchAgent; ensure proper gateway remains connected and tokens match. Return exit code."""
    cfg_path, cfg_data = load_openclaw_config()
    if not cfg_path or not cfg_data:
        if json_out:
            print(json.dumps({"ok": False, "error": "openclaw.json not found or invalid", "config_path": str(openclaw_config_path())}))
        else:
            print("Config:", openclaw_config_path(), "— not found or invalid.")
        return 2
    gcfg = gateway_config_from_openclaw(cfg_data)
    gateway_agent = find_gateway_plist(agents)
    guard_status = gateway_guard_status_json()
    # Build report
    report = {
        "ok": True,
        "config_path": gcfg["config_path"],
        "gateway": {
            "port": gcfg["port"],
            "auth_mode": gcfg["mode"],
            "token_set_in_config": gcfg["secret_set"],
            "config_ok": gcfg["config_ok"],
        },
        "gateway_launchagent": None,
        "gateway_loaded": False,
        "tokens_match": None,
        "recommendations": [],
    }
    if gateway_agent:
        report["gateway_launchagent"] = {"label": gateway_agent["label"], "path": gateway_agent["path"]}
        report["gateway_loaded"] = gateway_agent.get("loaded", False)
        if not gateway_agent.get("loaded"):
            report["ok"] = False
            report["recommendations"].append("Load gateway LaunchAgent: launchctl load " + gateway_agent["path"])
    else:
        report["ok"] = False
        report["recommendations"].append("No gateway LaunchAgent plist found (e.g. ai.openclaw.gateway). Install or create the gateway plist.")
    if guard_status is not None:
        report["tokens_match"] = guard_status.get("secretMatchesConfig", False)
        report["gateway_running"] = guard_status.get("running", False)
        if not guard_status.get("ok", False):
            report["ok"] = False
            if not report["gateway_loaded"] and gateway_agent:
                report["recommendations"].append("Load gateway: launchctl load " + gateway_agent["path"])
            guard_script_path = Path(OPENCLAW_HOME) / "workspace" / "skills" / "gateway-guard" / "scripts" / "gateway_guard.py"
            report["recommendations"].append("Sync auth: python3 " + str(guard_script_path) + " ensure --apply --json")
    if json_out:
        print(json.dumps(report, indent=2))
    else:
        print("Config:", report["config_path"])
        print("Gateway (openclaw.json): port", report["gateway"]["port"], "| auth", report["gateway"]["auth_mode"], "| token set:", report["gateway"]["token_set_in_config"])
        if report["gateway_launchagent"]:
            print("Gateway LaunchAgent:", report["gateway_launchagent"]["label"], "—", "loaded" if report["gateway_loaded"] else "NOT LOADED")
        else:
            print("Gateway LaunchAgent: (none found)")
        if report.get("gateway_running") is not None:
            print("Gateway process: running" if report["gateway_running"] else "not running")
        if report["tokens_match"] is not None:
            print("Tokens match (config vs running):", "yes" if report["tokens_match"] else "NO — run gateway-guard ensure --apply")
        for rec in report["recommendations"]:
            print("→", rec)
    if fix and report["recommendations"]:
        if not report["gateway_loaded"] and gateway_agent:
            load_agent(gateway_agent["path"])
            if not json_out:
                print("Loaded gateway LaunchAgent.")
        guard_script = Path(OPENCLAW_HOME) / "workspace" / "skills" / "gateway-guard" / "scripts" / "gateway_guard.py"
        if guard_script.exists() and report["tokens_match"] is False:
            subprocess.run(
                [sys.executable, str(guard_script), "ensure", "--apply", "--json"],
                env={**os.environ, "OPENCLAW_HOME": str(OPENCLAW_HOME)},
                cwd=str(OPENCLAW_HOME),
                timeout=25,
            )
            if not json_out:
                print("Ran gateway-guard ensure --apply.")
    return 0 if report["ok"] else 1


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Manage LaunchAgents: list OpenClaw vs others, prune non-OpenClaw; analyze config and gateway")
    ap.add_argument("--list", action="store_true", dest="do_list", help="List all LaunchAgents (default)")
    ap.add_argument("--json", action="store_true", help="Machine-readable output")
    ap.add_argument("--config", action="store_true", dest="do_config", help="Analyze openclaw.json and gateway LaunchAgent; ensure gateway connected and tokens match")
    ap.add_argument("--fix", action="store_true", help="With --config: load gateway plist if not loaded, run gateway-guard ensure --apply if tokens mismatch")
    ap.add_argument("--prune", action="store_true", dest="do_prune", help="Unload (and optionally delete) non-OpenClaw agents")
    ap.add_argument("--dry-run", action="store_true", help="With --prune: only show what would be done (default for --prune)")
    ap.add_argument("--apply", action="store_true", help="With --prune: actually unload non-OpenClaw agents")
    ap.add_argument("--delete-plists", action="store_true", help="With --prune --apply: also delete plist files (backup to OPENCLAW_HOME/backups/launchagents)")
    args = ap.parse_args()
    if not args.do_prune and not args.do_config:
        args.do_list = True

    agents = list_agents()
    openclaw = [a for a in agents if a["openclaw"]]
    others = [a for a in agents if not a["openclaw"]]

    if args.do_config:
        sys.exit(run_config_check(agents, args.json, args.fix))

    if args.do_prune:
        if not args.apply and not args.dry_run:
            print("Prune: use --dry-run to see what would be unloaded, or --apply to unload non-OpenClaw agents.", file=sys.stderr)
            sys.exit(2)
        if args.json:
            report = {"would_unload": [a["label"] for a in others], "would_keep": [a["label"] for a in openclaw], "applied": False}
        else:
            print("Non-OpenClaw LaunchAgents (would be unloaded):")
            for a in others:
                print("  ", a["label"], a["path"])
            print("OpenClaw (kept):", ", ".join(a["label"] for a in openclaw) or "(none)")
        if args.apply:
            backup_dir = OPENCLAW_HOME / "backups" / "launchagents"
            if args.delete_plists:
                backup_dir.mkdir(parents=True, exist_ok=True)
            for a in others:
                unload_agent(a["label"])
                if args.delete_plists:
                    src = Path(a["path"])
                    if src.exists():
                        dest = backup_dir / src.name
                        shutil.copy2(src, dest)
                        src.unlink()
            if args.json:
                report["applied"] = True
                report["unloaded"] = [a["label"] for a in others]
                print(json.dumps(report))
            elif not args.json:
                print("Unloaded", len(others), "non-OpenClaw agent(s).")
        elif args.json:
            print(json.dumps(report))
        sys.exit(0)

    # Default: list
    if args.json:
        out = {"openclaw": openclaw, "others": others, "all": agents}
        print(json.dumps(out, indent=2))
    else:
        print("OpenClaw LaunchAgents (kept):")
        for a in openclaw:
            status = "loaded" if a["loaded"] else "unloaded"
            print("  ", a["label"], "—", status)
        print("Other LaunchAgents (prune with --prune --apply):")
        for a in others:
            status = "loaded" if a["loaded"] else "unloaded"
            print("  ", a["label"], "—", status, "—", a["path"])

    sys.exit(0)


if __name__ == "__main__":
    main()
