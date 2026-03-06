#!/usr/bin/env python3
import argparse
from pathlib import Path
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(text)


def main():
    parser = argparse.ArgumentParser(description="Append standard per-step doc updates")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--gate", required=True, help="Gate id, e.g. G3")
    parser.add_argument("--task", required=True, help="Task summary")
    parser.add_argument("--status", default="DONE", help="Task status")
    parser.add_argument("--evidence", default="", help="Evidence summary")
    parser.add_argument("--owner", default="orchestrator", help="Owner")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ts = now_iso()

    append(root / "docs" / "tasks.md", f"| {args.gate}-{ts} | {args.task} | {args.status} | {args.gate} | {args.owner} | {ts} |\n")
    append(root / "docs" / "change-log.md", f"| {ts} | {args.task} | Gate {args.gate} execution | code/docs/tests | {args.owner} |\n")
    append(root / "docs" / "traceability.md", f"| {args.gate}-{ts} | docs/architecture.md/docs/requirements.md | implementation update | test run | {args.status} |\n")
    append(root / "docs" / "test-results.md", f"| {args.gate} | {args.task} | see commands/logs | expected met | {args.evidence or 'see logs'} | {'PASS' if args.status.upper() in ('DONE','PASS') else args.status.upper()} | {args.evidence or 'n/a'} | {ts} |\n")
    append(root / "docs" / "progress.md", f"\n- [{ts}] {args.gate}: {args.task} ({args.status})\n")

    print("Documentation step updates appended.")


if __name__ == "__main__":
    main()
