#!/usr/bin/env python3
"""
codex-token-daily.py

按项目汇总 Codex 当日 token 使用量，输出机器可读 JSON。

数据来源：~/.codex/sessions/YYYY/MM/DD/*.jsonl 的 token_count 事件。
统计口径：优先使用 total_token_usage 做差分，避免重复事件导致双计数。
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional


@dataclass
class Project:
    window: str
    directory: str


@dataclass
class Counter:
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_output_tokens: int = 0
    total_tokens: int = 0

    def add(self, other: "Counter") -> None:
        self.input_tokens += other.input_tokens
        self.cached_input_tokens += other.cached_input_tokens
        self.output_tokens += other.output_tokens
        self.reasoning_output_tokens += other.reasoning_output_tokens
        self.total_tokens += other.total_tokens

    @staticmethod
    def from_obj(obj: object) -> "Counter":
        if not isinstance(obj, dict):
            return Counter()

        def _i(key: str) -> int:
            v = obj.get(key, 0)
            return int(v) if isinstance(v, int) else 0

        return Counter(
            input_tokens=_i("input_tokens"),
            cached_input_tokens=_i("cached_input_tokens"),
            output_tokens=_i("output_tokens"),
            reasoning_output_tokens=_i("reasoning_output_tokens"),
            total_tokens=_i("total_tokens"),
        )

    def delta_from(self, prev: "Counter") -> "Counter":
        # total usage 理论上单调递增；防御性处理异常回退/重置
        return Counter(
            input_tokens=max(self.input_tokens - prev.input_tokens, 0),
            cached_input_tokens=max(self.cached_input_tokens - prev.cached_input_tokens, 0),
            output_tokens=max(self.output_tokens - prev.output_tokens, 0),
            reasoning_output_tokens=max(
                self.reasoning_output_tokens - prev.reasoning_output_tokens, 0
            ),
            total_tokens=max(self.total_tokens - prev.total_tokens, 0),
        )

    def to_dict(self) -> Dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "output_tokens": self.output_tokens,
            "reasoning_output_tokens": self.reasoning_output_tokens,
            "total_tokens": self.total_tokens,
        }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="按项目汇总 Codex 当日 token 使用量（JSON 输出）"
    )
    parser.add_argument(
        "--project",
        action="append",
        default=[],
        help="项目映射，格式: <window>:<project_dir>，可重复传入",
    )
    parser.add_argument(
        "--date",
        default="",
        help="目标日期，格式 YYYY-MM-DD（默认: 本地今天）",
    )
    parser.add_argument(
        "--lookback-days",
        type=int,
        default=7,
        help="扫描最近 N 天目录（默认 7）",
    )
    parser.add_argument(
        "--sessions-root",
        default=os.path.expanduser("~/.codex/sessions"),
        help="Codex sessions 根目录",
    )
    return parser.parse_args()


def parse_project_specs(specs: Iterable[str]) -> list[Project]:
    projects: list[Project] = []
    for spec in specs:
        if ":" not in spec:
            continue
        window, directory = spec.split(":", 1)
        window = window.strip()
        directory = directory.strip()
        if not window or not directory:
            continue
        projects.append(Project(window=window, directory=os.path.normpath(directory)))
    return projects


def iter_candidate_files(
    sessions_root: Path, target_date: dt.date, lookback_days: int
) -> Iterable[Path]:
    seen: set[Path] = set()
    for offset in range(max(lookback_days, 1)):
        d = target_date - dt.timedelta(days=offset)
        day_dir = sessions_root / f"{d:%Y/%m/%d}"
        if not day_dir.is_dir():
            continue
        for p in day_dir.glob("*.jsonl"):
            if p not in seen:
                seen.add(p)
                yield p

    # 补漏：跨日期目录但最近仍在写入的 session
    # 这里取最近 36 小时修改过的 JSONL，避免漏掉超长会话。
    try:
        result = subprocess.run(
            [
                "find",
                str(sessions_root),
                "-name",
                "*.jsonl",
                "-mmin",
                "-2160",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and result.stdout:
            for line in result.stdout.splitlines():
                p = Path(line.strip())
                if p and p not in seen:
                    seen.add(p)
                    yield p
    except Exception:
        pass


def read_session_cwd(path: Path) -> Optional[str]:
    try:
        with path.open("r", encoding="utf-8") as f:
            first = f.readline()
    except OSError:
        return None

    if not first:
        return None

    try:
        data = json.loads(first)
    except json.JSONDecodeError:
        return None

    if data.get("type") != "session_meta":
        return None

    payload = data.get("payload")
    if not isinstance(payload, dict):
        return None
    cwd = payload.get("cwd")
    return str(cwd) if isinstance(cwd, str) and cwd else None


def pick_project(cwd: str, projects: list[Project]) -> Optional[Project]:
    norm_cwd = os.path.normpath(cwd)
    for p in projects:
        if norm_cwd == p.directory:
            return p
        prefix = p.directory + os.sep
        if norm_cwd.startswith(prefix):
            return p
    return None


def parse_event_date(ts: str, local_tz: dt.tzinfo) -> Optional[dt.date]:
    try:
        parsed = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(local_tz).date()


def main() -> int:
    args = parse_args()
    projects = parse_project_specs(args.project)

    local_tz = dt.datetime.now().astimezone().tzinfo
    if local_tz is None:
        local_tz = dt.timezone.utc

    if args.date:
        try:
            target_date = dt.date.fromisoformat(args.date)
        except ValueError:
            print(
                json.dumps({"error": f"invalid --date: {args.date}"}, ensure_ascii=False),
                file=sys.stderr,
            )
            return 2
    else:
        target_date = dt.datetime.now(local_tz).date()

    sessions_root = Path(args.sessions_root).expanduser()
    if not sessions_root.exists():
        print(
            json.dumps(
                {
                    "date": target_date.isoformat(),
                    "timezone": str(local_tz),
                    "totals": Counter().to_dict(),
                    "projects": [],
                    "top_project": None,
                },
                ensure_ascii=False,
            )
        )
        return 0

    project_stats: Dict[str, Dict[str, object]] = {}
    for p in projects:
        project_stats[p.window] = {
            "window": p.window,
            "dir": p.directory,
            "counters": Counter(),
            "sessions": 0,
            "last_event": "",
        }

    for session_path in iter_candidate_files(
        sessions_root, target_date=target_date, lookback_days=args.lookback_days
    ):
        cwd = read_session_cwd(session_path)
        if not cwd:
            continue

        project = pick_project(cwd, projects)
        if not project:
            continue

        counters = Counter()
        last_event_ts = ""
        had_today_event = False
        prev_total: Optional[Counter] = None
        last_fallback: Optional[Counter] = None

        try:
            with session_path.open("r", encoding="utf-8") as f:
                for raw in f:
                    if not raw.strip():
                        continue
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue

                    if data.get("type") != "event_msg":
                        continue
                    payload = data.get("payload")
                    if not isinstance(payload, dict):
                        continue
                    if payload.get("type") != "token_count":
                        continue

                    ts = data.get("timestamp")
                    if not isinstance(ts, str):
                        continue
                    event_date = parse_event_date(ts, local_tz=local_tz)
                    if event_date != target_date:
                        info = payload.get("info")
                        if isinstance(info, dict):
                            total_obj = info.get("total_token_usage")
                            if isinstance(total_obj, dict):
                                prev_total = Counter.from_obj(total_obj)
                        continue

                    had_today_event = True
                    last_event_ts = ts

                    info = payload.get("info")
                    if not isinstance(info, dict):
                        continue

                    total_obj = info.get("total_token_usage")
                    if isinstance(total_obj, dict):
                        cur_total = Counter.from_obj(total_obj)
                        if prev_total is not None:
                            counters.add(cur_total.delta_from(prev_total))
                        prev_total = cur_total
                        continue

                    # fallback：某些事件只有 last_token_usage（或 info 不完整）
                    last_obj = info.get("last_token_usage")
                    if isinstance(last_obj, dict):
                        fallback = Counter.from_obj(last_obj)
                        if (
                            last_fallback is None
                            or fallback.total_tokens != last_fallback.total_tokens
                            or fallback.input_tokens != last_fallback.input_tokens
                            or fallback.output_tokens != last_fallback.output_tokens
                        ):
                            counters.add(fallback)
                        last_fallback = fallback
        except OSError:
            continue

        if had_today_event:
            stats = project_stats[project.window]
            stats_counter = stats["counters"]
            if isinstance(stats_counter, Counter):
                stats_counter.add(counters)
            stats["sessions"] = int(stats["sessions"]) + 1

            prev_last = str(stats["last_event"])
            if not prev_last or last_event_ts > prev_last:
                stats["last_event"] = last_event_ts

    totals = Counter()
    project_rows = []
    for window, stats in project_stats.items():
        counters = stats["counters"]
        if not isinstance(counters, Counter):
            counters = Counter()
        totals.add(counters)
        row = {
            "window": window,
            "dir": stats["dir"],
            **counters.to_dict(),
            "sessions": int(stats["sessions"]),
            "last_event": stats["last_event"] or None,
        }
        project_rows.append(row)

    project_rows.sort(key=lambda x: int(x.get("total_tokens", 0)), reverse=True)
    top_project = project_rows[0] if project_rows and project_rows[0]["total_tokens"] > 0 else None
    if top_project is not None:
        top_project = {
            "window": top_project["window"],
            "total_tokens": int(top_project["total_tokens"]),
        }

    output = {
        "date": target_date.isoformat(),
        "timezone": str(local_tz),
        "totals": totals.to_dict(),
        "projects": project_rows,
        "top_project": top_project,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
