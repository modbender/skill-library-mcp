"""
memory_meta.py — 记忆元数据读写工具库（频道隔离版）
"""
import re
from datetime import date
from pathlib import Path
from typing import Optional

META_PATTERN = re.compile(
    r'<!--\s*meta:\s*importance=(\d+)\s+access=(\d+)\s+'
    r'created=([\d-]+)\s+last_accessed=([\d-]+)'
    r'(?:\s+channel=([\w-]+))?\s*-->'
)


def parse_meta(line: str) -> dict | None:
    m = META_PATTERN.search(line)
    if not m:
        return None
    return {
        "importance": int(m.group(1)),
        "access_count": int(m.group(2)),
        "created": m.group(3),
        "last_accessed": m.group(4),
        "channel": m.group(5) or "boss",
    }


def format_meta(
    importance: int,
    access_count: int,
    created: str,
    last_accessed: str,
    channel: str = "boss",
) -> str:
    return (
        f"<!-- meta: importance={importance} access={access_count} "
        f"created={created} last_accessed={last_accessed} channel={channel} -->"
    )


def read_all_meta(filepath: Path, channel: Optional[str] = None, boss_full_access: bool = True) -> list[dict]:
    results = []
    if not filepath.exists():
        return results
    lines = filepath.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        meta = parse_meta(line)
        if not meta:
            continue

        # 读取隔离：boss 全量，其它频道只读本频道
        if channel and not (boss_full_access and channel == "boss"):
            if meta.get("channel") != channel:
                continue

        summary = ""
        for j in range(i - 1, -1, -1):
            stripped = lines[j].strip()
            if stripped and not stripped.startswith("<!--"):
                summary = stripped
                break

        meta["line"] = i + 1
        meta["file"] = str(filepath)
        meta["summary"] = summary
        results.append(meta)
    return results


def write_meta_to_entry(filepath: Path, entry_text: str, importance: int = 5, channel: str = "boss") -> None:
    today = date.today().isoformat()
    meta_line = format_meta(importance, 0, today, today, channel=channel)
    content = filepath.read_text(encoding="utf-8") if filepath.exists() else ""
    with open(filepath, "a", encoding="utf-8") as f:
        if content and not content.endswith("\n"):
            f.write("\n")
        f.write(f"\n{entry_text}\n{meta_line}\n")


def bump_access(filepath: Path, line_number: int) -> bool:
    if not filepath.exists():
        return False
    lines = filepath.read_text(encoding="utf-8").splitlines()
    idx = line_number - 1
    if idx < 0 or idx >= len(lines):
        return False
    meta = parse_meta(lines[idx])
    if not meta:
        return False

    new_meta = format_meta(
        meta["importance"],
        meta["access_count"] + 1,
        meta["created"],
        date.today().isoformat(),
        channel=meta.get("channel", "boss"),
    )
    lines[idx] = META_PATTERN.sub(new_meta, lines[idx])
    filepath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return True
