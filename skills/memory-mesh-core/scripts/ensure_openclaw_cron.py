#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path


def run_cmd(args, cwd=None):
    proc = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def parse_json_maybe(text: str):
    text = text or ""
    idx = text.find("{")
    if idx == -1:
        return None
    try:
        return json.loads(text[idx:])
    except Exception:
        return None


def find_job_id(list_json, name: str):
    jobs = (list_json or {}).get("jobs", [])
    for job in jobs:
        if str(job.get("name", "")) == name:
            return str(job.get("id"))
    return ""


def main():
    parser = argparse.ArgumentParser(description="Ensure OpenClaw cron for memory mesh and optionally run now.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--job-name", default="memory_mesh_sync", help="Cron job name")
    parser.add_argument("--every", default="12h", help="Cron interval")
    parser.add_argument(
        "--issue-url",
        default="https://github.com/wanng-ide/memory-mesh-core/issues/1",
        help="GitHub issue URL for contribution intake",
    )
    parser.add_argument(
        "--post-issue-comments",
        action="store_true",
        help="Enable posting contribution comments to GitHub issue in scheduled cycle",
    )
    parser.add_argument("--post-max-items", type=int, default=2, help="Max comments to post per scheduled cycle")
    parser.add_argument("--run-now", action="store_true", help="Run the cron job once after ensuring")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    post_flags = ""
    if args.post_issue_comments:
        post_flags = f" --post-issue-comments --post-max-items {max(1, int(args.post_max_items))}"
    message = (
        "exec: python3 skills/memory-mesh-core/scripts/memory_mesh_v102_cycle.py "
        f"--workspace . --top-k 20 --min-score 45 --max-consolidated 400 --issue-url {args.issue_url}{post_flags}"
    )

    code, out, err = run_cmd(["openclaw", "cron", "list", "--json"], cwd=str(workspace))
    if code != 0:
        raise SystemExit(f"Failed to list cron jobs: {(err or out).strip()}")
    list_json = parse_json_maybe(out)
    if not list_json:
        raise SystemExit("Failed to parse cron list JSON output.")

    job_id = find_job_id(list_json, args.job_name)
    action = "edited"
    if job_id:
        edit_args = [
            "openclaw",
            "cron",
            "edit",
            job_id,
            "--every",
            args.every,
            "--session",
            "isolated",
            "--message",
            message,
            "--enable",
            "--no-deliver",
            "--json",
        ]
        code, out, err = run_cmd(edit_args, cwd=str(workspace))
        if code != 0:
            raise SystemExit(f"Failed to edit cron job: {(err or out).strip()}")
    else:
        action = "created"
        add_args = [
            "openclaw",
            "cron",
            "add",
            "--name",
            args.job_name,
            "--every",
            args.every,
            "--session",
            "isolated",
            "--message",
            message,
            "--no-deliver",
            "--json",
        ]
        code, out, err = run_cmd(add_args, cwd=str(workspace))
        if code != 0:
            raise SystemExit(f"Failed to add cron job: {(err or out).strip()}")
        created = parse_json_maybe(out)
        if created and created.get("id"):
            job_id = str(created["id"])
        else:
            code, out, err = run_cmd(["openclaw", "cron", "list", "--json"], cwd=str(workspace))
            if code != 0:
                raise SystemExit(f"Cron created but failed to re-list jobs: {(err or out).strip()}")
            list_json = parse_json_maybe(out)
            job_id = find_job_id(list_json, args.job_name)

    if not job_id:
        raise SystemExit("Could not resolve cron job id after ensure.")

    run_result = {"requested": args.run_now, "status": "skipped"}
    if args.run_now:
        code, out, err = run_cmd(["openclaw", "cron", "run", job_id, "--timeout", "300000"], cwd=str(workspace))
        run_result = {
            "requested": True,
            "status": "ok" if code == 0 else "error",
            "stdout_tail": (out or "")[-800:],
            "stderr_tail": (err or "")[-800:],
        }
        if code != 0:
            raise SystemExit(f"Cron run failed: {(err or out).strip()}")

    print(
        json.dumps(
            {
                "ok": True,
                "action": action,
                "job_name": args.job_name,
                "job_id": job_id,
                "every": args.every,
                "issue_url": args.issue_url,
                "post_issue_comments": args.post_issue_comments,
                "post_max_items": max(1, int(args.post_max_items)),
                "run_result": run_result,
            }
        )
    )


if __name__ == "__main__":
    main()
