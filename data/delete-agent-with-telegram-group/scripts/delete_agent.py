#!/usr/bin/env python3
import argparse
import json
import re
import shutil
from pathlib import Path
from datetime import datetime

OPENCLAW_JSON = Path.home() / ".openclaw" / "openclaw.json"
CRON_JSON = Path.home() / ".openclaw" / "cron" / "jobs.json"
AGENTS_DIR = Path.home() / ".openclaw" / "agents"


def validate_agent_id(agent_id: str):
    if not re.fullmatch(r"[a-z0-9-]+", agent_id):
        raise SystemExit("Error: --agent-id must match [a-z0-9-]+")


def validate_within(base: Path, p: Path, name: str):
    try:
        p.resolve().relative_to(base.resolve())
    except Exception:
        raise SystemExit(f"Error: refusing unsafe {name} path outside {base}: {p}")


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def backup(path: Path):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    b = path.with_name(path.name + f".bak.{ts}")
    b.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    return str(b)


def main():
    ap = argparse.ArgumentParser(description="Delete OpenClaw agent cleanly")
    ap.add_argument("--agent-id", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--yes", action="store_true")
    ap.add_argument("--delete-workspace", action="store_true")
    ap.add_argument("--delete-telegram-group-config", action="store_true")
    ap.add_argument("--delete-cron-jobs", action="store_true")
    args = ap.parse_args()

    if not args.dry_run and not args.yes:
        raise SystemExit("Refusing destructive run without --yes (or use --dry-run)")

    cfg = load_json(OPENCLAW_JSON)
    if cfg is None:
        raise SystemExit(f"Config not found: {OPENCLAW_JSON}")

    agent_id = args.agent_id.strip()
    validate_agent_id(agent_id)
    removed = {
        "agent": False,
        "bindings": [],
        "telegram_groups": [],
        "agent_dir": None,
        "workspace": None,
        "cron_jobs": [],
        "backups": [],
    }

    agents = cfg.get("agents", {}).get("list", [])
    target = None
    new_agents = []
    for a in agents:
        if a.get("id") == agent_id:
            target = a
        else:
            new_agents.append(a)

    if target:
        removed["agent"] = True
        cfg["agents"]["list"] = new_agents
        removed["workspace"] = target.get("workspace")

    bindings = cfg.get("bindings", [])
    keep_bindings = []
    group_ids = set()
    for b in bindings:
        if b.get("agentId") == agent_id:
            removed["bindings"].append(b)
            p = b.get("match", {}).get("peer", {})
            if p.get("kind") == "group" and p.get("id"):
                group_ids.add(p.get("id"))
        else:
            keep_bindings.append(b)
    cfg["bindings"] = keep_bindings

    if args.delete_telegram_group_config:
        tg_groups = cfg.get("channels", {}).get("telegram", {}).get("groups", {})
        for gid in sorted(group_ids):
            if gid in tg_groups:
                removed["telegram_groups"].append(gid)
                tg_groups.pop(gid, None)

    agent_dir = AGENTS_DIR / agent_id
    validate_within(AGENTS_DIR, agent_dir, "agent_dir")
    if agent_dir.exists():
        removed["agent_dir"] = str(agent_dir)

    cron = load_json(CRON_JSON)
    if cron and args.delete_cron_jobs:
        jobs = cron.get("jobs", [])
        kept = []
        for j in jobs:
            if j.get("agentId") == agent_id:
                removed["cron_jobs"].append(j.get("id"))
            else:
                kept.append(j)
        cron["jobs"] = kept

    if args.dry_run:
        print(json.dumps({"mode": "dry-run", "agent_id": agent_id, "plan": removed}, ensure_ascii=False, indent=2))
        return

    # write files with backups
    removed["backups"].append(backup(OPENCLAW_JSON))
    OPENCLAW_JSON.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

    if cron and args.delete_cron_jobs:
        removed["backups"].append(backup(CRON_JSON))
        CRON_JSON.write_text(json.dumps(cron, ensure_ascii=False, indent=2), encoding="utf-8")

    if agent_dir.exists():
        shutil.rmtree(agent_dir)

    if args.delete_workspace and removed["workspace"]:
        wp = Path(removed["workspace"]).expanduser()
        # guardrail: only allow deleting workspaces under user's home and matching claw-* naming
        validate_within(Path.home(), wp, "workspace")
        if not wp.name.startswith("claw-"):
            raise SystemExit(f"Error: refusing unsafe workspace delete (expected claw-*): {wp}")
        if wp.exists():
            shutil.rmtree(wp)

    print(json.dumps({"mode": "execute", "agent_id": agent_id, "removed": removed}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
