#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime
from pathlib import Path


def validate_path_within(prefix: Path, path: Path, name: str):
    """Ensure path is within prefix to prevent arbitrary file write."""
    try:
        path.resolve().relative_to(prefix.resolve())
    except ValueError:
        raise SystemExit(f"Error: {name} must be within {prefix}")


def norm_agent_id(name: str) -> str:
    s = name.strip().lower().replace("_", " ")
    out = []
    for ch in s:
        if ch.isalnum() or ch == "-":
            out.append(ch)
        elif ch.isspace():
            out.append("-")
    agent = "".join(out)
    while "--" in agent:
        agent = agent.replace("--", "-")
    return agent.strip("-")


def ensure_agent(cfg: dict, agent_id: str, model: str, workspace: str):
    agents = cfg.setdefault("agents", {}).setdefault("list", [])
    home = Path.home()
    agent_dir = str(home / ".openclaw" / "agents" / agent_id / "agent")
    found = None
    for a in agents:
        if a.get("id") == agent_id:
            found = a
            break
    if not found:
        found = {"id": agent_id}
        agents.append(found)
    found["name"] = found.get("name") or agent_id
    found["workspace"] = workspace
    found["agentDir"] = agent_dir
    found["model"] = model


def ensure_binding(cfg: dict, agent_id: str, chat_id: str):
    bindings = cfg.setdefault("bindings", [])
    for b in bindings:
        p = b.get("match", {}).get("peer", {})
        if b.get("agentId") == agent_id and b.get("match", {}).get("channel") == "telegram" and p.get("id") == chat_id:
            return
    bindings.append({
        "agentId": agent_id,
        "match": {"channel": "telegram", "peer": {"kind": "group", "id": chat_id}},
    })


def ensure_telegram_group(cfg: dict, chat_id: str):
    tg = cfg.setdefault("channels", {}).setdefault("telegram", {})
    groups = tg.setdefault("groups", {})
    g = groups.setdefault(chat_id, {})
    g["requireMention"] = False


def main():
    ap = argparse.ArgumentParser(description="Provision OpenClaw agent + telegram binding deterministically")
    ap.add_argument("--agent-name", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--chat-id", required=True)
    ap.add_argument("--config", default=os.path.expanduser("~/.openclaw/openclaw.json"))
    ap.add_argument("--workspace-root", default=os.path.expanduser("~"))
    ap.add_argument("--no-backup", action="store_true", help="Disable automatic config backup")
    args = ap.parse_args()

    agent_id = norm_agent_id(args.agent_name)
    if not agent_id:
        raise SystemExit("Error: agent-name cannot be empty or contain only invalid characters")

    home = Path.home()
    workspace_root = Path(args.workspace_root).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve()

    # Validate paths to prevent arbitrary file write
    validate_path_within(home, workspace_root, "workspace-root")
    validate_path_within(home, config_path, "config")

    workspace = str(workspace_root / f"claw-{agent_id}")
    Path(workspace).mkdir(parents=True, exist_ok=True)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    ensure_agent(cfg, agent_id, args.model, workspace)
    ensure_binding(cfg, agent_id, args.chat_id)
    ensure_telegram_group(cfg, args.chat_id)
    cfg.setdefault("gateway", {}).setdefault("reload", {})["mode"] = cfg.setdefault("gateway", {}).setdefault("reload", {}).get("mode", "hybrid")

    backup_path = None
    if not args.no_backup:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = f"{config_path}.bak.{ts}"
        Path(backup_path).write_text(Path(config_path).read_text(encoding="utf-8"), encoding="utf-8")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "agent_id": agent_id,
        "workspace": workspace,
        "chat_id": args.chat_id,
        "requireMention": False,
        "config": str(config_path),
        "backup": backup_path,
        "changed": [
            "agents.list(+update)",
            "bindings(+)",
            f"channels.telegram.groups.{args.chat_id}.requireMention=false",
            "gateway.reload.mode(default=hybrid if absent)"
        ]
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
