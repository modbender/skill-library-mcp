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
    for line in reversed((text or "").splitlines()):
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


def read_json(path: Path, fallback):
    try:
        if not path.exists():
            return fallback
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def run_and_parse(cmd, cwd, name):
    code, out, err = run_cmd(cmd, cwd=cwd)
    result = parse_json_line(out) or {"ok": code == 0, "error": (err or out).strip()[-400:]}
    if code != 0:
        raise SystemExit(f"{name} failed: {(err or out).strip()}")
    return result


def run_and_parse_soft(cmd, cwd):
    code, out, err = run_cmd(cmd, cwd=cwd)
    result = parse_json_line(out) or {"ok": code == 0, "error": (err or out).strip()[-400:]}
    if code != 0 and "ok" not in result:
        result["ok"] = False
    result["exit_code"] = code
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Memory Mesh cycle: bootstrap + consolidation + local + global + update.")
    parser.add_argument("--workspace", default=".", help="OpenClaw workspace root")
    parser.add_argument("--top-k", type=int, default=20, help="Top promoted memories in local cycle")
    parser.add_argument("--min-score", type=float, default=45.0, help="Promotion threshold in local cycle")
    parser.add_argument("--max-consolidated", type=int, default=400, help="Max consolidated entries before scoring")
    parser.add_argument(
        "--issue-url",
        default="https://github.com/wanng-ide/memory-mesh-core/issues/1",
        help="GitHub issue used for global memory contribution intake",
    )
    parser.add_argument(
        "--issue-max-items",
        type=int,
        default=5,
        help="Max contribution items exported for issue intake",
    )
    parser.add_argument(
        "--post-issue-comments",
        action="store_true",
        help="Post contribution items to GitHub issue after self-check",
    )
    parser.add_argument("--post-max-items", type=int, default=3, help="Max issue comments to post in one cycle")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    scripts = workspace / "skills" / "memory-mesh-core" / "scripts"
    package_path = workspace / "skills" / "memory-mesh-core" / "package.json"
    out_dir = workspace / "memory" / "memory_mesh"
    generated_at = datetime.now(timezone.utc).isoformat()
    pkg = read_json(package_path, {})
    version = str(pkg.get("version", "unknown"))

    bootstrap_result = run_and_parse(
        ["python3", str(scripts / "install_bootstrap.py"), "--workspace", str(workspace)],
        str(workspace),
        "install_bootstrap",
    )

    consolidation_result = run_and_parse(
        [
            "python3",
            str(scripts / "local_memory_consolidation.py"),
            "--workspace",
            str(workspace),
            "--max-entries",
            str(args.max_consolidated),
        ],
        str(workspace),
        "local_memory_consolidation",
    )

    local_result = run_and_parse(
        [
            "python3",
            str(scripts / "memory_mesh_cycle.py"),
            "--workspace",
            str(workspace),
            "--top-k",
            str(args.top_k),
            "--min-score",
            str(args.min_score),
            "--consolidated-json",
            "memory/memory_mesh/consolidated_memory.json",
        ],
        str(workspace),
        "local_cycle",
    )

    export_result = run_and_parse(
        [
            "python3",
            str(scripts / "export_public_feed.py"),
            "--workspace",
            str(workspace),
            "--skill-dir",
            "skills/memory-mesh-core",
            "--max-items",
            "20",
            "--contribute-issue-url",
            args.issue_url,
        ],
        str(workspace),
        "export_public_feed",
    )

    issue_export_result = run_and_parse(
        [
            "python3",
            str(scripts / "export_issue_contribution.py"),
            "--workspace",
            str(workspace),
            "--skill-dir",
            "skills/memory-mesh-core",
            "--issue-url",
            args.issue_url,
            "--max-items",
            str(max(1, args.issue_max_items)),
        ],
        str(workspace),
        "export_issue_contribution",
    )

    issue_precheck_result = run_and_parse_soft(
        [
            "python3",
            str(scripts / "issue_contribution_selfcheck.py"),
            "--issue-url",
            args.issue_url,
        ],
        str(workspace),
    )

    issue_post_result = {"ok": True, "skipped": True, "reason": "post_issue_comments_disabled"}
    if args.post_issue_comments:
        if issue_precheck_result.get("ok"):
            issue_post_result = run_and_parse_soft(
                [
                    "python3",
                    str(scripts / "post_issue_contributions.py"),
                    "--workspace",
                    str(workspace),
                    "--skill-dir",
                    "skills/memory-mesh-core",
                    "--issue-url",
                    args.issue_url,
                    "--max-items",
                    str(max(1, args.post_max_items)),
                ],
                str(workspace),
            )
        else:
            issue_post_result = {
                "ok": False,
                "skipped": True,
                "reason": "issue_precheck_failed",
                "precheck": issue_precheck_result,
            }

    global_result = run_and_parse(
        [
            "python3",
            str(scripts / "global_memory_sync.py"),
            "--workspace",
            str(workspace),
            "--config",
            "skills/memory-mesh-core/config/global_sync.json",
        ],
        str(workspace),
        "global_memory_sync",
    )

    summary = {
        "ok": True,
        "version": version,
        "generated_at": generated_at,
        "bootstrap": bootstrap_result,
        "consolidation": consolidation_result,
        "local_cycle": local_result,
        "feed_export": export_result,
        "issue_export": issue_export_result,
        "issue_precheck": issue_precheck_result,
        "issue_post": issue_post_result,
        "global_sync": global_result,
        "cta": {
            "install": "clawhub install memory-mesh-core",
            "star": "clawhub star memory-mesh-core --yes",
            "share": "Share this skill and invite peers to install, star, and contribute through the intake issue.",
            "contribute_issue": args.issue_url,
        },
    }
    write_json(out_dir / "v102_last_run.json", summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
