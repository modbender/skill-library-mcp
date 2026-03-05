#!/usr/bin/env python3
"""
cleanup-state.py

根据 config.yaml 的 project_dirs / projects 清理 state.json 中的僵尸项目数据。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import yaml


def normalize_project_dir(project_dir: str) -> str:
    """规范化项目目录路径，便于跨写法比对。"""
    return os.path.realpath(os.path.expanduser(project_dir.strip()))


def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("配置文件格式错误: 顶层必须是对象")
    return data


def load_state(state_path: Path) -> Dict[str, Any]:
    if not state_path.exists():
        return {}
    with state_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("状态文件格式错误: 顶层必须是对象")
    return data


def _basename_from_dir(project_dir: str) -> str:
    normalized = project_dir.rstrip(os.sep)
    return os.path.basename(normalized)


def _collect_dirs_from_project_dirs(config: Dict[str, Any]) -> Set[str]:
    configured_dirs = config.get("project_dirs", [])
    if isinstance(configured_dirs, str):
        configured_dirs = [configured_dirs]
    if not isinstance(configured_dirs, list):
        return set()

    return {
        normalize_project_dir(project_dir)
        for project_dir in configured_dirs
        if isinstance(project_dir, str) and project_dir.strip()
    }


def _collect_from_projects_section(config: Dict[str, Any]) -> Tuple[Set[str], Set[str]]:
    projects = config.get("projects")
    valid_dirs: Set[str] = set()
    valid_names: Set[str] = set()

    def add_dir(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            normalized = normalize_project_dir(value)
            valid_dirs.add(normalized)
            base = _basename_from_dir(normalized)
            if base:
                valid_names.add(base)

    def add_name(value: Any) -> None:
        if isinstance(value, str) and value.strip():
            valid_names.add(value.strip())

    if isinstance(projects, dict):
        for project_key, project_value in projects.items():
            add_name(project_key)
            if isinstance(project_value, dict):
                add_name(project_value.get("window"))
                add_name(project_value.get("name"))
                add_dir(project_value.get("dir"))
                add_dir(project_value.get("project_dir"))
                add_dir(project_value.get("path"))
            else:
                add_dir(project_value)
    elif isinstance(projects, list):
        for project_item in projects:
            if isinstance(project_item, dict):
                add_name(project_item.get("window"))
                add_name(project_item.get("name"))
                add_dir(project_item.get("dir"))
                add_dir(project_item.get("project_dir"))
                add_dir(project_item.get("path"))
            else:
                add_dir(project_item)

    return valid_dirs, valid_names


def collect_valid_projects(config: Dict[str, Any]) -> Tuple[Set[str], Set[str]]:
    valid_dirs = _collect_dirs_from_project_dirs(config)
    project_dirs, project_names = _collect_from_projects_section(config)
    valid_dirs.update(project_dirs)

    valid_names = {_basename_from_dir(project_dir) for project_dir in valid_dirs if _basename_from_dir(project_dir)}
    valid_names.update(project_names)
    return valid_dirs, valid_names


def is_project_valid(project_value: Any, valid_dirs: Set[str], valid_names: Set[str]) -> bool:
    if not isinstance(project_value, str) or not project_value.strip():
        return False

    candidate = project_value.strip()
    normalized = normalize_project_dir(candidate)

    if normalized in valid_dirs:
        return True

    basename_raw = os.path.basename(candidate.rstrip("/"))
    if basename_raw in valid_names:
        return True

    basename_normalized = os.path.basename(normalized)
    return basename_normalized in valid_names


def cleanup_state(
    state: Dict[str, Any], valid_dirs: Set[str], valid_names: Set[str]
) -> Dict[str, List[Any]]:
    removed: Dict[str, List[Any]] = {
        "projects": [],
        "active_projects": [],
        "paused_projects": [],
        "project_send_order": [],
    }

    projects = state.get("projects")
    if isinstance(projects, dict):
        stale_project_keys = [
            project_key
            for project_key in list(projects.keys())
            if not is_project_valid(project_key, valid_dirs, valid_names)
        ]
        for project_key in stale_project_keys:
            projects.pop(project_key, None)
        removed["projects"] = stale_project_keys

    for field in ("active_projects", "paused_projects", "project_send_order"):
        values = state.get(field)
        if not isinstance(values, list):
            continue

        kept_values: List[Any] = []
        stale_values: List[Any] = []
        for value in values:
            if is_project_valid(value, valid_dirs, valid_names):
                kept_values.append(value)
            else:
                stale_values.append(value)
        state[field] = kept_values
        removed[field] = stale_values

    return removed


def save_state(state_path: Path, state: Dict[str, Any]) -> None:
    tmp_state_path = state_path.with_name(f"{state_path.name}.tmp")
    try:
        with tmp_state_path.open("w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_state_path, state_path)
    except Exception:
        if tmp_state_path.exists():
            tmp_state_path.unlink(missing_ok=True)
        raise


def parse_args() -> argparse.Namespace:
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    parser = argparse.ArgumentParser(
        description="清理 state.json 中不在 config.yaml project_dirs/projects 的项目数据"
    )
    parser.add_argument(
        "--config",
        default=str(root_dir / "config.yaml"),
        help="config.yaml 路径（默认：仓库根目录/config.yaml）",
    )
    parser.add_argument(
        "--state",
        default=str(root_dir / "state.json"),
        help="state.json 路径（默认：仓库根目录/state.json）",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).expanduser()
    state_path = Path(args.state).expanduser()

    try:
        config = load_config(config_path)
        state = load_state(state_path)
    except Exception as exc:
        print(f"cleanup-state: 读取失败 - {exc}", file=sys.stderr)
        return 1

    valid_dirs, valid_names = collect_valid_projects(config)
    if not valid_dirs:
        print("cleanup-state: 未发现有效 project_dirs/projects，跳过清理")
        return 0

    removed = cleanup_state(state, valid_dirs, valid_names)
    changed_count = sum(len(items) for items in removed.values())
    if changed_count == 0:
        print("cleanup-state: 无需清理，state.json 已同步")
        return 0

    try:
        save_state(state_path, state)
    except Exception as exc:
        print(f"cleanup-state: 保存失败 - {exc}", file=sys.stderr)
        return 1

    print(
        "cleanup-state: 清理完成 "
        f"(projects={len(removed['projects'])}, "
        f"active={len(removed['active_projects'])}, "
        f"paused={len(removed['paused_projects'])}, "
        f"send_order={len(removed['project_send_order'])})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
