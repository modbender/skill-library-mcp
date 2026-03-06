#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_cmd(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return p.returncode, p.stdout or "", p.stderr or ""


def read_json(path: Path, fallback):
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_json_line(text: str):
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except Exception:
                continue
    return None


def main():
    parser = argparse.ArgumentParser(description="Run one-time global sync bootstrap when skill is installed.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--force", action="store_true", help="Run bootstrap even if already completed")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    state_path = workspace / "memory" / "memory_mesh" / "install_bootstrap_state.json"
    state = read_json(state_path, {"completed": False, "runs": []})

    if state.get("completed") and not args.force:
        print(json.dumps({"ok": True, "skipped": True, "reason": "already_completed"}))
        return

    script = workspace / "skills" / "memory-mesh-core" / "scripts" / "global_memory_sync.py"
    code, out, err = run_cmd(
        ["python3", str(script), "--workspace", str(workspace), "--config", "skills/memory-mesh-core/config/global_sync.json"],
        cwd=str(workspace),
    )
    result = parse_json_line(out) or {"ok": code == 0, "error": (err or out).strip()[-400:]}
    if code != 0:
        raise SystemExit(f"Bootstrap global sync failed: {(err or out).strip()}")

    run_record = {
        "ran_at": now_iso(),
        "result": result,
    }
    next_state = {
        "completed": True,
        "completed_at": run_record["ran_at"],
        "runs": (state.get("runs", []) + [run_record])[-20:],
    }
    write_json(state_path, next_state)
    print(json.dumps({"ok": True, "bootstrap": result}))


if __name__ == "__main__":
    main()
