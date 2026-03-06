#!/usr/bin/env python3
"""Batch download source/pdf artifacts for multiple arXiv paper directories."""

from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Batch download paper artifacts for a run directory. "
            "Supports source/pdf/source_then_pdf with concurrency control."
        )
    )
    parser.add_argument(
        "--run-dir",
        default="",
        help=(
            "Run directory that contains per-paper subdirectories. "
            "If provided and no explicit paper list is given, paper directories are auto-discovered."
        ),
    )
    parser.add_argument(
        "--paper-dir",
        action="append",
        default=[],
        help="Explicit paper directory. Repeat this flag for multiple papers.",
    )
    parser.add_argument(
        "--paper-dirs-file",
        default="",
        help="Optional text file with one paper directory path per line.",
    )
    parser.add_argument(
        "--artifact",
        default="source_then_pdf",
        choices=["source", "pdf", "source_then_pdf"],
        help="Artifact policy per paper. Default source_then_pdf.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=3,
        help="Max concurrent papers. Default 3.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional limit for paper count after discovery. 0 means no limit.",
    )
    parser.add_argument("--language", default="English", help="Workflow language for trace logs.")
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=45,
        help="HTTP timeout seconds forwarded to per-paper scripts.",
    )
    parser.add_argument(
        "--user-agent",
        default="arxiv-paper-batch-downloader/1.0 (contact: local-agent)",
        help="HTTP user agent forwarded to per-paper scripts.",
    )
    parser.add_argument(
        "--rate-state-path",
        default="",
        help=(
            "Optional throttle-state JSON path forwarded to per-paper scripts. "
            "If empty, scripts use <run_dir>/.runtime/arxiv_download_state.json."
        ),
    )
    parser.add_argument(
        "--min-interval-sec",
        type=float,
        default=5.0,
        help="Minimum interval between requests across workers. Default 5.0.",
    )
    parser.add_argument(
        "--retry-max",
        type=int,
        default=4,
        help="Retry max forwarded to per-paper scripts. Default 4.",
    )
    parser.add_argument(
        "--retry-base-sec",
        type=float,
        default=5.0,
        help="Retry base seconds forwarded to per-paper scripts. Default 5.0.",
    )
    parser.add_argument(
        "--retry-max-sec",
        type=float,
        default=120.0,
        help="Retry max seconds forwarded to per-paper scripts. Default 120.0.",
    )
    parser.add_argument(
        "--retry-jitter-sec",
        type=float,
        default=1.0,
        help="Retry jitter seconds forwarded to per-paper scripts. Default 1.0.",
    )
    parser.add_argument("--force", action="store_true", help="Force redownload and overwrite existing artifacts.")
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue processing other papers if one fails.",
    )
    parser.add_argument("--python-bin", default="python3", help="Python executable for sub-calls.")
    parser.add_argument(
        "--source-script",
        default="",
        help="Optional explicit path to download_arxiv_source.py.",
    )
    parser.add_argument(
        "--pdf-script",
        default="",
        help="Optional explicit path to download_arxiv_pdf.py.",
    )
    parser.add_argument(
        "--output-log",
        default="",
        help=(
            "Optional batch log output path. "
            "Default: <run_dir>/download_batch_log.json when --run-dir is set."
        ),
    )
    parser.add_argument("--print-commands", action="store_true", help="Print subcommands before execution.")
    return parser.parse_args()


def parse_last_json_block(raw: str) -> dict[str, Any]:
    lines = raw.strip().splitlines()
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].lstrip().startswith("{"):
            chunk = "\n".join(lines[idx:])
            try:
                data = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                return data
    return {}


def read_paper_dirs_file(path: Path) -> list[Path]:
    out: list[Path] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        out.append(Path(line).expanduser().resolve())
    return out


def discover_paper_dirs(run_dir: Path) -> list[Path]:
    out: list[Path] = []
    for child in sorted(run_dir.iterdir()):
        if not child.is_dir():
            continue
        if child.name in {"query_results", "query_selection"}:
            continue
        if (child / "metadata.md").exists() or (child / "metadata.json").exists():
            out.append(child.resolve())
    return out


def unique_paths(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve())
        if key in seen:
            continue
        seen.add(key)
        out.append(path.resolve())
    return out


def has_usable_source(paper_dir: Path) -> bool:
    extract_dir = paper_dir / "source" / "source_extract"
    if not extract_dir.exists():
        return False
    return any(p.is_file() for p in extract_dir.rglob("*.tex"))


def has_pdf(paper_dir: Path) -> bool:
    pdf_path = paper_dir / "source" / "paper.pdf"
    if not pdf_path.exists() or not pdf_path.is_file():
        return False
    return pdf_path.stat().st_size > 0


def is_paper_dir(path: Path) -> bool:
    return path.is_dir() and ((path / "metadata.md").exists() or (path / "metadata.json").exists())


def build_common_flags(args: argparse.Namespace) -> list[str]:
    flags = [
        "--language",
        args.language,
        "--request-timeout",
        str(args.request_timeout),
        "--user-agent",
        args.user_agent,
        "--min-interval-sec",
        str(args.min_interval_sec),
        "--retry-max",
        str(args.retry_max),
        "--retry-base-sec",
        str(args.retry_base_sec),
        "--retry-max-sec",
        str(args.retry_max_sec),
        "--retry-jitter-sec",
        str(args.retry_jitter_sec),
    ]
    if args.rate_state_path.strip():
        flags += ["--rate-state-path", args.rate_state_path.strip()]
    if args.force:
        flags.append("--force")
    return flags


def build_source_cmd(args: argparse.Namespace, source_script: Path, paper_dir: Path) -> list[str]:
    return [
        args.python_bin,
        str(source_script),
        "--paper-dir",
        str(paper_dir),
        *build_common_flags(args),
    ]


def build_pdf_cmd(args: argparse.Namespace, pdf_script: Path, paper_dir: Path) -> list[str]:
    return [
        args.python_bin,
        str(pdf_script),
        "--paper-dir",
        str(paper_dir),
        *build_common_flags(args),
    ]


def run_cmd(cmd: list[str], *, print_command: bool) -> dict[str, Any]:
    if print_command:
        print("[CMD] " + " ".join(shlex.quote(part) for part in cmd))
    proc = subprocess.run(cmd, text=True, capture_output=True)
    parsed = parse_last_json_block(proc.stdout)
    return {
        "command": cmd,
        "return_code": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
        "result": parsed,
    }


def source_ok_from_result(run_result: dict[str, Any]) -> bool:
    result = run_result.get("result", {})
    if not isinstance(result, dict):
        return False
    extract_ok = bool(result.get("extract_ok", False))
    tex_count = int(result.get("tex_file_count", 0) or 0)
    return extract_ok and tex_count > 0


def process_one_paper(
    *,
    args: argparse.Namespace,
    source_script: Path,
    pdf_script: Path,
    paper_dir: Path,
) -> dict[str, Any]:
    start_ts = dt.datetime.now(dt.timezone.utc)
    entry: dict[str, Any] = {
        "paper_dir": str(paper_dir),
        "artifact_mode": args.artifact,
        "started_at_utc": start_ts.isoformat(),
        "precheck": {
            "has_usable_source": has_usable_source(paper_dir),
            "has_pdf": has_pdf(paper_dir),
        },
        "actions": [],
    }

    if args.artifact == "source":
        if entry["precheck"]["has_usable_source"] and not args.force:
            entry["status"] = "skipped_existing_source"
        else:
            call_result = run_cmd(
                build_source_cmd(args, source_script, paper_dir),
                print_command=args.print_commands,
            )
            entry["actions"].append({"type": "source", **call_result})
            entry["status"] = "ok" if call_result["return_code"] == 0 else "error"

    elif args.artifact == "pdf":
        if entry["precheck"]["has_pdf"] and not args.force:
            entry["status"] = "skipped_existing_pdf"
        else:
            call_result = run_cmd(
                build_pdf_cmd(args, pdf_script, paper_dir),
                print_command=args.print_commands,
            )
            entry["actions"].append({"type": "pdf", **call_result})
            entry["status"] = "ok" if call_result["return_code"] == 0 else "error"

    else:  # source_then_pdf
        if entry["precheck"]["has_usable_source"] and not args.force:
            entry["status"] = "skipped_existing_source"
        elif entry["precheck"]["has_pdf"] and not args.force:
            entry["status"] = "skipped_existing_pdf"
        else:
            source_result = run_cmd(
                build_source_cmd(args, source_script, paper_dir),
                print_command=args.print_commands,
            )
            entry["actions"].append({"type": "source", **source_result})
            if source_result["return_code"] != 0:
                entry["status"] = "error"
            elif source_ok_from_result(source_result):
                entry["status"] = "ok"
            else:
                pdf_result = run_cmd(
                    build_pdf_cmd(args, pdf_script, paper_dir),
                    print_command=args.print_commands,
                )
                entry["actions"].append({"type": "pdf", **pdf_result})
                entry["status"] = "ok" if pdf_result["return_code"] == 0 else "error"

    end_ts = dt.datetime.now(dt.timezone.utc)
    entry["finished_at_utc"] = end_ts.isoformat()
    entry["duration_sec"] = round((end_ts - start_ts).total_seconds(), 3)
    entry["postcheck"] = {
        "has_usable_source": has_usable_source(paper_dir),
        "has_pdf": has_pdf(paper_dir),
    }
    return entry


def resolve_script(path_arg: str, default_name: str) -> Path:
    if path_arg.strip():
        return Path(path_arg).expanduser().resolve()
    return (Path(__file__).resolve().parent / default_name).resolve()


def run() -> int:
    args = parse_args()

    source_script = resolve_script(args.source_script, "download_arxiv_source.py")
    pdf_script = resolve_script(args.pdf_script, "download_arxiv_pdf.py")
    if not source_script.exists():
        print(f"[ERROR] source script not found: {source_script}")
        return 1
    if not pdf_script.exists():
        print(f"[ERROR] pdf script not found: {pdf_script}")
        return 1

    run_dir: Path | None = None
    paper_dirs: list[Path] = []
    if args.run_dir.strip():
        run_dir = Path(args.run_dir).expanduser().resolve()
        if not run_dir.exists() or not run_dir.is_dir():
            print(f"[ERROR] run directory not found: {run_dir}")
            return 1
        paper_dirs.extend(discover_paper_dirs(run_dir))

    for paper_dir in args.paper_dir:
        paper_dirs.append(Path(paper_dir).expanduser().resolve())

    if args.paper_dirs_file.strip():
        file_path = Path(args.paper_dirs_file).expanduser().resolve()
        if not file_path.exists():
            print(f"[ERROR] paper-dirs-file not found: {file_path}")
            return 1
        paper_dirs.extend(read_paper_dirs_file(file_path))

    paper_dirs = unique_paths(paper_dirs)
    paper_dirs = [path for path in paper_dirs if is_paper_dir(path)]

    if args.limit > 0:
        paper_dirs = paper_dirs[: args.limit]

    if not paper_dirs:
        print("[ERROR] no valid paper directories found.")
        return 1

    max_workers = max(1, args.max_workers)
    results: list[dict[str, Any]] = []
    failed = 0
    stop_requested = False

    with cf.ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map = {
            pool.submit(
                process_one_paper,
                args=args,
                source_script=source_script,
                pdf_script=pdf_script,
                paper_dir=paper_dir,
            ): paper_dir
            for paper_dir in paper_dirs
        }
        for fut in cf.as_completed(future_map):
            paper_dir = future_map[fut]
            try:
                item = fut.result()
            except Exception as exc:  # pragma: no cover - defensive
                item = {
                    "paper_dir": str(paper_dir),
                    "artifact_mode": args.artifact,
                    "status": "error",
                    "actions": [],
                    "exception": repr(exc),
                }
            results.append(item)
            if item.get("status") == "error":
                failed += 1
                if not args.continue_on_error:
                    stop_requested = True
            if stop_requested:
                for pending in future_map:
                    pending.cancel()
                break

    results.sort(key=lambda x: x.get("paper_dir", ""))
    status_counter: dict[str, int] = {}
    for item in results:
        status = str(item.get("status", "unknown"))
        status_counter[status] = status_counter.get(status, 0) + 1

    payload = {
        "artifact_mode": args.artifact,
        "run_dir": str(run_dir) if run_dir else "",
        "paper_count": len(results),
        "max_workers": max_workers,
        "language": args.language,
        "status_counter": status_counter,
        "failed_count": failed,
        "stopped_early": stop_requested,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "results": results,
    }

    output_log = args.output_log.strip()
    if not output_log and run_dir is not None:
        output_log = str((run_dir / "download_batch_log.json").resolve())
    if output_log:
        log_path = Path(output_log).expanduser().resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        payload["output_log"] = str(log_path)

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 1 if failed > 0 and not args.continue_on_error else 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
