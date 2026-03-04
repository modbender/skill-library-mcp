#!/usr/bin/env python3
"""各项检查逻辑模块：daily / todo / ongoing 状态检查"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("heartbeat.checker")

WORKSPACE = Path(__file__).parent.parent / "workspace"


def _read_file(name: str) -> Optional[str]:
    """安全读取工作区文件"""
    path = WORKSPACE / name
    if not path.exists():
        logger.warning("文件不存在: %s", path)
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error("读取文件失败 %s: %s", name, e)
        return None


def check_daily() -> dict:
    """
    检查 daily.md 完成情况

    返回:
        {
            "total": int,
            "done": int,
            "pending": [str],
            "items": [{"text": str, "done": bool}],
            "error": str | None
        }
    """
    result = {"total": 0, "done": 0, "pending": [], "items": [], "error": None}
    content = _read_file("daily.md")
    if content is None:
        result["error"] = "daily.md 不存在"
        return result

    for line in content.splitlines():
        line = line.strip()
        # 匹配 - [x] 或 - [ ] 格式
        m = re.match(r"^-\s*\[([ xX])\]\s*(.+)$", line)
        if m:
            done = m.group(1).lower() == "x"
            text = m.group(2).strip()
            result["items"].append({"text": text, "done": done})
            result["total"] += 1
            if done:
                result["done"] += 1
            else:
                result["pending"].append(text)

    logger.info("daily 检查: %d/%d 完成", result["done"], result["total"])
    return result


def check_todo() -> dict:
    """
    检查 todo.md 待办事项

    返回:
        {
            "total": int,
            "done": int,
            "pending": [str],
            "overdue": [{"text": str, "due": str}],
            "items": [{"text": str, "done": bool, "due": str | None}],
            "error": str | None
        }
    """
    result = {
        "total": 0, "done": 0, "pending": [], "overdue": [],
        "items": [], "error": None,
    }
    content = _read_file("todo.md")
    if content is None:
        result["error"] = "todo.md 不存在"
        return result

    now = datetime.now()

    for line in content.splitlines():
        line = line.strip()
        m = re.match(r"^-\s*\[([ xX])\]\s*(.+)$", line)
        if m:
            done = m.group(1).lower() == "x"
            text = m.group(2).strip()

            # 解析 @due:HH:MM
            due_str = None
            due_match = re.search(r"@due:(\d{1,2}:\d{2})", text)
            if due_match:
                due_str = due_match.group(1)

            item = {"text": text, "done": done, "due": due_str}
            result["items"].append(item)
            result["total"] += 1

            if done:
                result["done"] += 1
            else:
                result["pending"].append(text)

                # 检查是否超期
                if due_str and not done:
                    try:
                        due_time = datetime.strptime(due_str, "%H:%M").replace(
                            year=now.year, month=now.month, day=now.day
                        )
                        if now > due_time:
                            result["overdue"].append({"text": text, "due": due_str})
                    except ValueError:
                        pass

    logger.info(
        "todo 检查: %d/%d 完成, %d 超期",
        result["done"], result["total"], len(result["overdue"]),
    )
    return result


def check_ongoing() -> dict:
    """
    检查 ongoing.json 任务状态

    返回:
        {
            "total": int,
            "by_status": {"WIP": int, "WAIT": int, ...},
            "tasks": [dict],
            "stale": [dict],       # 可能卡死的任务
            "overdue": [dict],     # 超过 eta 的任务
            "error": str | None
        }
    """
    result = {
        "total": 0, "by_status": {}, "tasks": [],
        "stale": [], "overdue": [], "error": None,
    }
    content = _read_file("ongoing.json")
    if content is None:
        result["error"] = "ongoing.json 不存在"
        return result

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        result["error"] = f"ongoing.json 解析失败: {e}"
        logger.error(result["error"])
        return result

    tasks = data if isinstance(data, list) else data.get("tasks", [])
    result["total"] = len(tasks)
    result["tasks"] = tasks

    now = datetime.now()

    for task in tasks:
        status = task.get("status", "IDLE")
        result["by_status"][status] = result["by_status"].get(status, 0) + 1

        # 检查 eta 是否过期（仅对活跃任务）
        if status in ("WIP", "WAIT"):
            eta = task.get("eta", "")
            if eta and eta != "持续":
                try:
                    # 支持 MM-DD 或 YYYY-MM-DD 格式
                    if len(eta) <= 5:
                        eta_date = datetime.strptime(eta, "%m-%d").replace(year=now.year)
                    else:
                        eta_date = datetime.strptime(eta, "%Y-%m-%d")
                    if now.date() > eta_date.date():
                        result["overdue"].append(task)
                except ValueError:
                    pass

    logger.info(
        "ongoing 检查: 共%d, 状态=%s, 超期=%d",
        result["total"], result["by_status"], len(result["overdue"]),
    )
    return result


def clean_done_todos() -> int:
    """
    清理已完成的 todo 项（完成即删除）

    返回: 删除的条目数
    """
    path = WORKSPACE / "todo.md"
    if not path.exists():
        return 0

    content = path.read_text(encoding="utf-8")
    lines = content.splitlines()
    new_lines = []
    removed = 0

    for line in lines:
        stripped = line.strip()
        if re.match(r"^-\s*\[[xX]\]", stripped):
            removed += 1
        else:
            new_lines.append(line)

    if removed > 0:
        # 原子写入
        tmp_path = path.with_suffix(".tmp")
        tmp_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        tmp_path.rename(path)
        logger.info("清理了 %d 条已完成 todo", removed)

    return removed
