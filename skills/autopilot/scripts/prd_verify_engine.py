#!/usr/bin/env python3
"""PRD verification engine.

Features:
- Parse prd-items.yaml with version inheritance (`extends`)
- Verify feature items and bugfix items
- Support checker plugins: file_exists, file_contains, command, json_field_equals
- Output machine-readable report (prd-progress.json)
"""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

ITEM_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*(?:-[A-Za-z0-9]+)+")
TODO_ITEM_RE = re.compile(rf"^-\s*(✅\s*)?({ITEM_ID_RE.pattern})\b")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"items file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("invalid items file: root must be mapping")
    return data


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = deep_merge(merged[k], v)
        else:
            merged[k] = copy.deepcopy(v)
    return merged


def resolve_version(doc: dict[str, Any], target_version: str) -> dict[str, Any]:
    versions = doc.get("versions")
    if not isinstance(versions, list):
        raise ValueError("invalid items file: versions must be list")

    version_map: dict[str, dict[str, Any]] = {}
    for v in versions:
        if not isinstance(v, dict) or "id" not in v:
            continue
        version_map[str(v["id"])] = v

    if target_version not in version_map:
        raise ValueError(f"version not found: {target_version}")

    def _resolve(v_id: str, stack: set[str]) -> dict[str, Any]:
        if v_id in stack:
            raise ValueError(f"cyclic extends detected: {v_id}")
        raw = version_map[v_id]
        base: dict[str, Any] = {
            "id": raw["id"],
            "iterations": [],
            "items": [],
            "bugfixes": [],
        }
        parent = raw.get("extends")
        if parent:
            stack.add(v_id)
            base = _resolve(str(parent), stack)
            stack.remove(v_id)

        merged = deep_merge(base, {k: v for k, v in raw.items() if k != "extends"})
        merged["items"] = merge_entries(
            as_list(base.get("items")),
            as_list(raw.get("items")),
            as_list(raw.get("item_updates")),
        )
        merged["bugfixes"] = merge_entries(
            as_list(base.get("bugfixes")),
            as_list(raw.get("bugfixes")),
            as_list(raw.get("bugfix_updates")),
        )
        merged["iterations"] = merge_entries(
            as_list(base.get("iterations")),
            as_list(raw.get("iterations")),
            [],
        )
        return merged

    return _resolve(target_version, set())


def merge_entries(
    inherited: list[dict[str, Any]],
    additions: list[dict[str, Any]],
    updates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []

    for src in (inherited, additions):
        for item in src:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            if not item_id:
                continue
            if item_id not in by_id:
                ordered_ids.append(item_id)
                by_id[item_id] = {}
            by_id[item_id] = deep_merge(by_id[item_id], item)

    for patch in updates:
        if not isinstance(patch, dict):
            continue
        item_id = str(patch.get("id", "")).strip()
        if not item_id:
            continue
        if item_id not in by_id:
            ordered_ids.append(item_id)
            by_id[item_id] = {}
        by_id[item_id] = deep_merge(by_id[item_id], patch)

    return [by_id[item_id] for item_id in ordered_ids]


def read_json_field(path: Path, field: str) -> Any:
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)

    if not field:
        return obj

    cur: Any = obj
    for part in field.split("."):
        part = part.strip()
        if not part:
            continue
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
            continue
        raise KeyError(f"field not found: {field}")
    return cur


def run_check(project_dir: Path, check: dict[str, Any]) -> dict[str, Any]:
    check_id = str(check.get("id", "unnamed-check"))
    check_type = str(check.get("type", "")).strip()
    result = {
        "id": check_id,
        "type": check_type,
        "passed": False,
        "detail": "",
    }

    try:
        if check_type == "file_exists":
            rel = str(check.get("path", "")).strip()
            if not rel:
                raise ValueError("missing path")
            path = project_dir / rel
            result["passed"] = path.exists()
            result["detail"] = f"exists={result['passed']} path={rel}"

        elif check_type == "file_contains":
            rel = str(check.get("path", "")).strip()
            pattern = str(check.get("pattern", ""))
            literal = bool(check.get("literal", False))
            if not rel or not pattern:
                raise ValueError("missing path/pattern")
            path = project_dir / rel
            if not path.exists():
                result["detail"] = f"file not found: {rel}"
                return result
            content = path.read_text(encoding="utf-8", errors="ignore")
            if literal:
                matched = pattern in content
            else:
                matched = re.search(pattern, content, flags=re.MULTILINE) is not None
            result["passed"] = matched
            result["detail"] = f"matched={matched} path={rel}"

        elif check_type == "command":
            raw_command = check.get("command", "")
            if isinstance(raw_command, list):
                command_list = [str(part) for part in raw_command if str(part).strip()]
            else:
                command_list = []
            command = str(raw_command).strip() if not isinstance(raw_command, list) else " ".join(command_list)
            if not command and not command_list:
                raise ValueError("missing command")
            timeout_sec = int(check.get("timeout_sec", 30))
            expect_exit = as_list(check.get("expect_exit", [0]))
            expect_exit_codes = {int(x) for x in expect_exit}
            cwd_rel = str(check.get("cwd", "")).strip()
            cwd = project_dir / cwd_rel if cwd_rel else project_dir
            use_shell = bool(check.get("shell", True))
            # SECURITY: command checks come from repository-maintained prd-items.yaml (trusted input).
            # If needed, set `shell: false` in a check to run with argument mode.
            if use_shell:
                run_args: Any = command
            else:
                run_args = command_list if command_list else shlex.split(command)
            proc = subprocess.run(
                run_args,
                cwd=str(cwd),
                shell=use_shell,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                check=False,
            )
            passed = proc.returncode in expect_exit_codes
            result["passed"] = passed
            out = (proc.stdout or "").strip().replace("\n", " ")
            err = (proc.stderr or "").strip().replace("\n", " ")
            result["detail"] = (
                f"exit={proc.returncode} expected={sorted(expect_exit_codes)} "
                f"stdout={out[:120]} stderr={err[:120]}"
            )

        elif check_type == "json_field_equals":
            rel = str(check.get("path", "")).strip()
            field = str(check.get("field", "")).strip()
            expected = check.get("expected")
            if not rel or not field:
                raise ValueError("missing path/field")
            path = project_dir / rel
            actual = read_json_field(path, field)
            result["passed"] = actual == expected
            result["detail"] = f"actual={actual!r} expected={expected!r}"

        else:
            raise ValueError(f"unsupported check type: {check_type}")

    except Exception as exc:  # pylint: disable=broad-except
        result["passed"] = False
        result["detail"] = f"error: {exc}"

    return result


def should_select_item(
    item: dict[str, Any],
    only_ids: set[str],
    only_type: str,
    changed_files: list[str],
) -> bool:
    item_id = str(item.get("id", "")).strip()
    item_type = str(item.get("type", "feature"))

    if only_ids and item_id not in only_ids:
        return False
    if only_type != "all" and item_type != only_type:
        return False

    if not changed_files:
        return True

    paths = [str(p) for p in as_list(item.get("paths")) if str(p).strip()]
    if not paths:
        return True

    for changed in changed_files:
        for configured in paths:
            if changed == configured or changed.startswith(configured.rstrip("/") + "/"):
                return True
    return False


def evaluate_entry(project_dir: Path, entry: dict[str, Any], strict_mode: bool) -> dict[str, Any]:
    checks = as_list(entry.get("checks"))
    if not checks:
        checks = as_list(entry.get("regression_checks"))

    check_results = [run_check(project_dir, c) for c in checks if isinstance(c, dict)]
    passed = all(r["passed"] for r in check_results) if check_results else (not strict_mode)
    status = "passed" if passed else "failed"
    if not check_results:
        status = "no_checks" if not strict_mode else "failed"

    return {
        "id": entry.get("id"),
        "type": entry.get("type", "feature"),
        "priority": entry.get("priority"),
        "severity": entry.get("severity"),
        "title": entry.get("title"),
        "status": status,
        "configured_status": entry.get("status"),
        "iteration": entry.get("iteration"),
        "owner": entry.get("owner"),
        "paths": as_list(entry.get("paths")),
        "checks": check_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify PRD items and output JSON progress.")
    parser.add_argument("--project-dir", default=".", help="project root containing PRD files")
    parser.add_argument("--items-file", default="prd-items.yaml", help="items yaml path")
    parser.add_argument("--output", default="prd-progress.json", help="output JSON path")
    parser.add_argument("--version", default="", help="target PRD version")
    parser.add_argument("--only-ids", default="", help="comma-separated item ids")
    parser.add_argument(
        "--only-type",
        default="all",
        choices=["all", "feature", "bugfix"],
        help="verify only a specific type",
    )
    parser.add_argument(
        "--changed-files",
        default="",
        help="changed files filter, accepts JSON array or comma-separated list",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat items without checks as failure",
    )
    parser.add_argument(
        "--print-failures-only",
        action="store_true",
        help="print compact failure summary to stdout",
    )
    parser.add_argument(
        "--sync-todo",
        action="store_true",
        help="sync prd-todo.md checkmarks from verification result",
    )
    parser.add_argument(
        "--todo-file",
        default="prd-todo.md",
        help="todo markdown path used with --sync-todo",
    )
    return parser.parse_args()


def parse_changed_files_arg(raw: str) -> list[str]:
    payload = raw.strip()
    if not payload:
        return []

    if payload.startswith("["):
        try:
            decoded = json.loads(payload)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list):
            return [str(item).strip() for item in decoded if str(item).strip()]

    if "\n" in payload:
        return [line.strip() for line in payload.splitlines() if line.strip()]

    return [item.strip() for item in payload.split(",") if item.strip()]


def sync_todo_file(project_dir: Path, todo_file: str, report: dict[str, Any]) -> None:
    todo_path = (project_dir / todo_file).resolve()
    if not todo_path.exists():
        return

    status_by_id: dict[str, str] = {}
    for result in report.get("results", []):
        if not isinstance(result, dict):
            continue
        item_id = str(result.get("id", "")).strip()
        if not item_id:
            continue
        status_by_id[item_id] = str(result.get("status", ""))

    if not status_by_id:
        return

    lines = todo_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    updated_lines: list[str] = []
    changed = False

    for line in lines:
        m = TODO_ITEM_RE.match(line)
        if not m:
            updated_lines.append(line)
            continue

        item_id = m.group(2)
        status = status_by_id.get(item_id)
        if not status:
            updated_lines.append(line)
            continue

        want_checked = status == "passed"
        has_checked = line.startswith("- ✅ ")
        base_line = re.sub(r"^-\s*✅\s*", "- ", line)

        if want_checked and not has_checked:
            updated_lines.append(base_line.replace("- ", "- ✅ ", 1))
            changed = True
        elif not want_checked and has_checked:
            updated_lines.append(base_line)
            changed = True
        else:
            updated_lines.append(line)

    if changed:
        todo_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    items_path = (project_dir / args.items_file).resolve()
    output_path = (project_dir / args.output).resolve()

    doc = load_yaml(items_path)
    meta = doc.get("meta", {}) if isinstance(doc.get("meta"), dict) else {}
    version = args.version or str(meta.get("default_version", ""))
    if not version:
        raise ValueError("version missing and meta.default_version not set")

    resolved = resolve_version(doc, version)
    strict_mode = bool(args.strict or meta.get("strict_mode_default", False))

    only_ids = {i.strip() for i in args.only_ids.split(",") if i.strip()}
    changed_files = parse_changed_files_arg(args.changed_files)

    all_entries = as_list(resolved.get("items")) + as_list(resolved.get("bugfixes"))
    selected = [
        entry
        for entry in all_entries
        if isinstance(entry, dict)
        and should_select_item(entry, only_ids, args.only_type, changed_files)
    ]

    results = [evaluate_entry(project_dir, entry, strict_mode) for entry in selected]
    passed_count = sum(1 for r in results if r["status"] == "passed")
    failed_count = sum(1 for r in results if r["status"] == "failed")
    no_checks_count = sum(1 for r in results if r["status"] == "no_checks")

    report = {
        "meta": {
            "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "project_dir": str(project_dir),
            "items_file": str(items_path),
            "version": version,
            "strict_mode": strict_mode,
            "selected_count": len(results),
            "passed_count": passed_count,
            "failed_count": failed_count,
            "no_checks_count": no_checks_count,
            "changed_files_filter": changed_files,
            "only_type": args.only_type,
            "only_ids": sorted(only_ids),
        },
        "results": results,
        "summary": {
            "ok": failed_count == 0 and (no_checks_count == 0 or not strict_mode),
            "failed_ids": [r["id"] for r in results if r["status"] == "failed"],
            "no_checks_ids": [r["id"] for r in results if r["status"] == "no_checks"],
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if args.sync_todo:
        sync_todo_file(project_dir, args.todo_file, report)

    if args.print_failures_only:
        for result in results:
            if result["status"] != "failed":
                continue
            details = "; ".join(
                f"{c['id']}: {c['detail']}" for c in result.get("checks", []) if not c.get("passed")
            )
            print(f"{result.get('id')}: {details}")
    else:
        print(
            json.dumps(
                {
                    "version": version,
                    "selected_count": len(results),
                    "passed_count": passed_count,
                    "failed_count": failed_count,
                    "no_checks_count": no_checks_count,
                    "output": str(output_path),
                },
                ensure_ascii=False,
            )
        )

    return 0 if report["summary"]["ok"] else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pylint: disable=broad-except
        print(f"prd_verify_engine_error: {exc}", file=sys.stderr)
        raise SystemExit(3)
