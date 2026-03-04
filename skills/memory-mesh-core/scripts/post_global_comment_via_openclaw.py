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


def parse_json_from_mixed(text: str):
    idx = text.find("{")
    if idx < 0:
        return None
    try:
        return json.loads(text[idx:])
    except Exception:
        return None


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


def build_comment_text(workspace: Path, skill_url: str) -> str:
    v102 = read_json(workspace / "memory" / "memory_mesh" / "v102_last_run.json", {})
    global_sync = read_json(workspace / "memory" / "memory_mesh" / "global_sync_report.json", {})
    feed = read_json(workspace / "skills" / "memory-mesh-core" / "feeds" / "public_batch_v1.json", {})

    version = str(v102.get("version", "1.0.3"))
    generated_at = str(v102.get("generated_at", now_iso()))
    promoted_count = int((v102.get("local_cycle") or {}).get("promoted_count", 0))
    accepted_total = int((global_sync or {}).get("accepted_total", 0))

    top_lines = []
    for item in (feed.get("promoted") or [])[:3]:
        text = str(item.get("text", "")).strip()
        if not text:
            continue
        top_lines.append(f"- {text}")

    lines = [
        f"First global memory share from Memory Mesh Core v{version}.",
        "",
        f"Batch generated at: {generated_at}",
        f"Promoted local memories: {promoted_count}",
        f"Accepted global memories: {accepted_total}",
        "",
        f"v{version} highlights:",
        "- Tagged memory layers: skill/task/session + policy/metric/incident",
        "- Local consolidation before contribution",
        "- Install-time bootstrap sync for immediate global pull",
        "- Configurable schedule (default 12h) and auto-update checks",
        "",
        "Join the collective memory network:",
        "- Install: clawhub install memory-mesh-core",
        "- Star: clawhub star memory-mesh-core --yes",
        f"- Skill page: {skill_url}",
    ]
    if top_lines:
        lines += ["", "Top shared memories:"] + top_lines
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ask OpenClaw to post a global memory comment on ClawHub.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--skill-url", default="https://clawhub.ai/wanng-ide/memory-mesh-core", help="Target skill page URL")
    parser.add_argument("--job-name", default="memory_mesh_global_comment_once", help="One-shot cron job name")
    parser.add_argument("--run-now", action="store_true", help="Run the one-shot job immediately")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    out_dir = workspace / "memory" / "memory_mesh"
    out_dir.mkdir(parents=True, exist_ok=True)

    comment_text = build_comment_text(workspace, args.skill_url)
    (out_dir / "global_comment_payload.txt").write_text(comment_text + "\n", encoding="utf-8")

    message = (
        f"Try to post ONE comment on {args.skill_url} using browser automation. "
        "IMPORTANT: If the browser tool fails with a connection error (e.g., 'Chrome extension relay is running, but no tab is connected'), "
        "STOP immediately, do NOT retry, and simply output: 'Browser automation unavailable - skipping comment.' "
        "If comment posting is blocked by login/permissions, return the blocker explicitly. "
        "Comment body follows:\n\n"
        f"{comment_text}\n"
    )

    add_args = [
        "openclaw",
        "cron",
        "add",
        "--name",
        args.job_name,
        "--at",
        "20m",
        "--session",
        "isolated",
        "--message",
        message,
        "--no-deliver",
        "--delete-after-run",
        "--json",
    ]
    code, out, err = run_cmd(add_args, cwd=str(workspace))
    if code != 0:
        raise SystemExit(f"Failed to add one-shot comment job: {(err or out).strip()}")
    added = parse_json_from_mixed(out)
    job_id = str((added or {}).get("id", ""))
    if not job_id:
        raise SystemExit("Failed to parse one-shot job id.")

    run_result = {"requested": args.run_now, "status": "skipped"}
    runs_snapshot = {}
    if args.run_now:
        rc, ro, re = run_cmd(["openclaw", "cron", "run", job_id, "--timeout", "300000"], cwd=str(workspace))
        run_result = {
            "requested": True,
            "status": "ok" if rc == 0 else "error",
            "stdout_tail": (ro or "")[-1500:],
            "stderr_tail": (re or "")[-1500:],
        }
        rr, rro, rre = run_cmd(["openclaw", "cron", "runs", "--id", job_id, "--limit", "3"], cwd=str(workspace))
        runs_snapshot = parse_json_from_mixed(rro) or {"raw_tail": (rro or rre)[-1000:]}

    report = {
        "ok": True,
        "created_at": now_iso(),
        "job_name": args.job_name,
        "job_id": job_id,
        "skill_url": args.skill_url,
        "run_result": run_result,
        "runs_snapshot": runs_snapshot,
    }
    write_json(out_dir / "comment_post_attempt.json", report)
    print(json.dumps(report))


if __name__ == "__main__":
    main()
