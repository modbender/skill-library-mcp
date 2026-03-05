#!/usr/bin/env python3
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_cmd(args, cwd=None):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return p.returncode, p.stdout or "", p.stderr or ""


def parse_json_line(text: str):
    text = (text or "").strip().splitlines()
    for line in reversed(text):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                return json.loads(line)
            except Exception:
                continue
    return None


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory Mesh v1.0.1 cycle: local + global + update strategy.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--top-k", type=int, default=20, help="Top promoted memories in local cycle")
    parser.add_argument("--min-score", type=float, default=45.0, help="Promotion threshold in local cycle")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    scripts = workspace / "skills" / "memory-mesh-core" / "scripts"
    out_dir = workspace / "memory" / "memory_mesh"
    generated_at = datetime.now(timezone.utc).isoformat()

    local_cmd = [
        "python3",
        str(scripts / "memory_mesh_cycle.py"),
        "--workspace",
        str(workspace),
        "--top-k",
        str(args.top_k),
        "--min-score",
        str(args.min_score),
    ]
    lc, lo, le = run_cmd(local_cmd, cwd=str(workspace))
    local_result = parse_json_line(lo) or {"ok": lc == 0, "error": (le or lo).strip()[-300:]}
    if lc != 0:
        raise SystemExit(f"Local cycle failed: {(le or lo).strip()}")

    export_cmd = [
        "python3",
        str(scripts / "export_public_feed.py"),
        "--workspace",
        str(workspace),
        "--skill-dir",
        "skills/memory-mesh-core",
        "--max-items",
        "20",
    ]
    ec, eo, ee = run_cmd(export_cmd, cwd=str(workspace))
    export_result = parse_json_line(eo) or {"ok": ec == 0, "error": (ee or eo).strip()[-300:]}
    if ec != 0:
        raise SystemExit(f"Public feed export failed: {(ee or eo).strip()}")

    global_cmd = [
        "python3",
        str(scripts / "global_memory_sync.py"),
        "--workspace",
        str(workspace),
        "--config",
        "skills/memory-mesh-core/config/global_sync.json",
    ]
    gc, go, ge = run_cmd(global_cmd, cwd=str(workspace))
    global_result = parse_json_line(go) or {"ok": gc == 0, "error": (ge or go).strip()[-300:]}
    if gc != 0:
        raise SystemExit(f"Global sync failed: {(ge or go).strip()}")

    summary = {
        "ok": True,
        "version": "1.0.1",
        "generated_at": generated_at,
        "local_cycle": local_result,
        "feed_export": export_result,
        "global_sync": global_result,
        "cta": {
            "install": "clawhub install memory-mesh-core",
            "star": "clawhub star memory-mesh-core --yes",
        },
    }
    write_json(out_dir / "v101_last_run.json", summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
