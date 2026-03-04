#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import subprocess
from pathlib import Path


def now_iso():
    return dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def load_env(path: Path):
    env = {}
    if not path.exists():
        return env
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_\-]+", "_", name.strip().lower())
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        raise ValueError("invalid slug")
    return s


def task_paths(cfg, slug):
    workspace = Path(cfg["WORKSPACE_DIR"]).expanduser()
    tasks_root = workspace / cfg.get("TASKS_DIR", "tasks")
    task_dir = tasks_root / slug
    return {
        "workspace": workspace,
        "tasks_root": tasks_root,
        "task_dir": task_dir,
        "registry": workspace / cfg.get("REGISTRY_FILE", "TASK_REGISTRY.md"),
    }


def ensure_registry(registry: Path):
    if registry.exists():
        return
    registry.write_text("# TASK_REGISTRY\n\n| slug | title | status | created_at | updated_at |\n|---|---|---|---|---|\n")


def upsert_registry_row(registry: Path, slug: str, title: str, status: str):
    ensure_registry(registry)
    lines = registry.read_text().splitlines()
    row = f"| {slug} | {title} | {status} | {now_iso()} | {now_iso()} |"
    out, replaced = [], False
    for line in lines:
        if line.startswith(f"| {slug} |"):
            out.append(row)
            replaced = True
        else:
            out.append(line)
    if not replaced:
        out.append(row)
    registry.write_text("\n".join(out) + "\n")


def init_task(cfg, slug, title, purpose, skills, plugins, tools):
    p = task_paths(cfg, slug)
    p["tasks_root"].mkdir(parents=True, exist_ok=True)
    td = p["task_dir"]
    (td / "artifacts").mkdir(parents=True, exist_ok=True)
    (td / "scripts").mkdir(parents=True, exist_ok=True)
    (td / "crons").mkdir(parents=True, exist_ok=True)

    front = {
        "name": slug,
        "title": title,
        "status": "registered",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    task_md = td / "TASK.md"
    if not task_md.exists():
        task_md.write_text(
            "---\n"
            + "\n".join(f"{k}: {v}" for k, v in front.items())
            + "\n---\n\n"
            + "# Purpose\n"
            + f"{purpose}\n\n"
            + "# Important Decisions\n- TBD\n\n"
            + "# Blockers\n- None\n\n"
            + "# Capabilities\n"
            + f"- Skills: {', '.join(skills) if skills else 'None'}\n"
            + f"- Plugins: {', '.join(plugins) if plugins else 'None'}\n"
            + f"- Tools: {', '.join(tools) if tools else 'None'}\n\n"
            + "# Change Log\n"
            + f"- {now_iso()} — Task registered and initialized.\n"
        )

    todos = td / "TODOS.md"
    if not todos.exists():
        todos.write_text("# TODOS\n\n- [ ] Define first milestone\n")

    state = td / "state.json"
    if not state.exists():
        state.write_text(json.dumps({"status": "registered", "updated_at": now_iso()}, indent=2) + "\n")

    ensure_registry(p["registry"])
    upsert_registry_row(p["registry"], slug, title, "registered")


def append_changelog(task_dir: Path, msg: str):
    task_md = task_dir / "TASK.md"
    if not task_md.exists():
        raise FileNotFoundError("TASK.md missing")
    with task_md.open("a") as f:
        f.write(f"- {now_iso()} — {msg}\n")


def set_state(task_dir: Path, status: str):
    st = task_dir / "state.json"
    data = {}
    if st.exists():
        data = json.loads(st.read_text())
    data["status"] = status
    data["updated_at"] = now_iso()
    st.write_text(json.dumps(data, indent=2) + "\n")


def ensure_queue_files(task_dir: Path):
    for fn in ["queue.jsonl", "done.jsonl", "failed.jsonl"]:
        fp = task_dir / fn
        if not fp.exists():
            fp.write_text("")
    lk = task_dir / "lock.json"
    if not lk.exists():
        lk.write_text(json.dumps({"locked": False, "updated_at": now_iso()}, indent=2) + "\n")


def add_cron(task_dir: Path, cfg, cron_expr: str, message: str, name: str = None):
    name = name or f"task-{task_dir.name}"
    spec = {
        "name": name,
        "cron": cron_expr,
        "tz": cfg.get("DEFAULT_CRON_TZ", "America/Indianapolis"),
        "agent": cfg.get("DEFAULT_AGENT_ID", "main"),
        "message": message,
        "updated_at": now_iso(),
    }
    (task_dir / "crons" / f"{name}.json").write_text(json.dumps(spec, indent=2) + "\n")

    cmd = [
        "openclaw", "cron", "add",
        "--name", name,
        "--cron", cron_expr,
        "--tz", spec["tz"],
        "--agent", spec["agent"],
        "--message", message,
        "--no-deliver",
    ]
    subprocess.run(cmd, check=False)


def rm_cron(task_dir: Path, name: str):
    spec = task_dir / "crons" / f"{name}.json"
    if spec.exists():
        spec.unlink()
    subprocess.run(["openclaw", "cron", "rm", "--name", name], check=False)


def main():
    ap = argparse.ArgumentParser(description="task-father helper")
    ap.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "config.env"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init")
    s.add_argument("slug")
    s.add_argument("--title", required=True)
    s.add_argument("--purpose", default="TBD")
    s.add_argument("--skills", default="")
    s.add_argument("--plugins", default="")
    s.add_argument("--tools", default="")

    s = sub.add_parser("set-state")
    s.add_argument("slug")
    s.add_argument("status")

    s = sub.add_parser("log")
    s.add_argument("slug")
    s.add_argument("message")

    s = sub.add_parser("enable-queue")
    s.add_argument("slug")

    s = sub.add_parser("cron-add")
    s.add_argument("slug")
    s.add_argument("--cron", required=True)
    s.add_argument("--message", required=True)
    s.add_argument("--name", default=None)

    s = sub.add_parser("cron-rm")
    s.add_argument("slug")
    s.add_argument("--name", required=True)

    args = ap.parse_args()
    cfg = {
        "WORKSPACE_DIR": "/home/miles/.openclaw/workspace",
        "TASKS_DIR": "tasks",
        "REGISTRY_FILE": "TASK_REGISTRY.md",
        "DEFAULT_AGENT_ID": "main",
        "DEFAULT_CRON_TZ": "America/Indianapolis",
    }
    cfg.update(load_env(Path(args.config)))

    if args.cmd == "init":
        slug = slugify(args.slug)
        init_task(
            cfg,
            slug,
            args.title,
            args.purpose,
            [x.strip() for x in args.skills.split(",") if x.strip()],
            [x.strip() for x in args.plugins.split(",") if x.strip()],
            [x.strip() for x in args.tools.split(",") if x.strip()],
        )
        print(f"initialized: {slug}")
        return

    slug = slugify(args.slug)
    tp = task_paths(cfg, slug)
    td = tp["task_dir"]
    if not td.exists():
        raise SystemExit(f"task not found: {slug}")

    if args.cmd == "set-state":
        set_state(td, args.status)
        append_changelog(td, f"State changed to '{args.status}'.")
        upsert_registry_row(tp["registry"], slug, slug, args.status)
        print("ok")
    elif args.cmd == "log":
        append_changelog(td, args.message)
        print("ok")
    elif args.cmd == "enable-queue":
        ensure_queue_files(td)
        append_changelog(td, "Enabled queue/done/failed/lock state files.")
        print("ok")
    elif args.cmd == "cron-add":
        add_cron(td, cfg, args.cron, args.message, args.name)
        append_changelog(td, f"Cron added: {args.name or f'task-{slug}'} ({args.cron}).")
        print("ok")
    elif args.cmd == "cron-rm":
        rm_cron(td, args.name)
        append_changelog(td, f"Cron removed: {args.name}.")
        print("ok")


if __name__ == "__main__":
    main()
