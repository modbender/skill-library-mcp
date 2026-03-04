#!/usr/bin/env python3
import argparse
from pathlib import Path
from datetime import datetime, timezone


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_line(path: Path, line: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def ensure_section(path: Path, header: str):
    if not path.exists():
        path.write_text(f"{header}\n\n", encoding="utf-8")
    else:
        txt = path.read_text(encoding="utf-8")
        if header not in txt:
            path.write_text(txt + f"\n{header}\n\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Record change request impact")
    parser.add_argument("--root", default=".", help="Project root")
    parser.add_argument("--request", required=True, help="Change request text")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ts = now_iso()

    change_log = root / "docs" / "change-log.md"
    append_line(change_log, f"| {ts} | {args.request} | User-requested change | requirements/architecture/tests/tasks | orchestrator |\n")

    tasks = root / "docs" / "tasks.md"
    append_line(tasks, f"| CR-{ts} | Assess and implement change: {args.request} | TODO | G1/G2+ | orchestrator | {ts} |\n")

    trace = root / "docs" / "traceability.md"
    append_line(trace, f"| CR-{ts} | docs/requirements.md | implementation TBD | tests TBD | TODO |\n")

    impact = root / "docs" / "change-impact.md"
    ensure_section(impact, "# Change Impact")
    append_line(
        impact,
        (
            f"\n## {ts}\n"
            f"Request: {args.request}\n"
            f"Impacted docs (review/update):\n"
            f"- docs/requirements.md\n"
            f"- docs/architecture.md\n"
            f"- docs/test-plan.md\n"
            f"- docs/test-results.md\n"
            f"- docs/tasks.md\n"
            f"- docs/progress.md\n"
            f"Validation actions:\n"
            f"- Re-run impacted unit/integration/e2e tests\n"
            f"- Re-run manual scenarios tied to changed behavior\n"
        ),
    )

    print("Change impact recorded. Review docs/change-impact.md for TODOs.")


if __name__ == "__main__":
    main()
