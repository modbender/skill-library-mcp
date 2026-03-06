#!/usr/bin/env python3
"""
upcoming_checker.py — 未来事件检查器

解析 workspace/upcoming.md（分区格式），返回最近 N 天内的即将发生事件。

分区格式：
    ## 🔮 FUTURE  — 自动+手动的近期事件
    ## 📌 MANUAL  — 手动长期事件
    ## ✅ DONE    — 已完成事件（不参与告警）
    ## ⏰ OVERDUE — 已过期未完成（参与告警）

也兼容旧的简单格式。
"""

import logging
import re
from datetime import datetime, timedelta, date
from pathlib import Path

logger = logging.getLogger("heartbeat.upcoming")

WORKSPACE = Path(__file__).parent.parent / "workspace"
UPCOMING_FILE = WORKSPACE / "upcoming.md"

# 紧急程度阈值（天）
URGENT_DAYS = 1    # ≤1天 → 🔴 紧急
WARNING_DAYS = 3   # ≤3天 → 🟡 注意
NOTICE_DAYS = 7    # ≤7天 → 🔵 提醒

# 事件行正则
EVENT_RE = re.compile(
    r"^-\s*(?:\[([xX ])\]\s*)?(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)(?:\s*\|\s*(.+))?$"
)


def _parse_upcoming_file(content: str, today: date, lookahead_days: int = 7) -> list:
    """
    解析 upcoming.md，返回指定天数内的事件列表。
    支持分区格式和旧格式。

    FUTURE + MANUAL 区的事件参与检查。
    DONE 区跳过。
    OVERDUE 区的事件标记为过期。
    """
    events = []
    deadline = today + timedelta(days=lookahead_days)

    # 检测是否分区格式
    is_sectioned = "FUTURE" in content or "MANUAL" in content or "OVERDUE" in content

    current_section = None
    skip_section = False

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if is_sectioned:
            # 分区标题检测
            if line.startswith("##"):
                if "FUTURE" in line:
                    current_section = "FUTURE"
                    skip_section = False
                elif "MANUAL" in line:
                    current_section = "MANUAL"
                    skip_section = False
                elif "DONE" in line:
                    current_section = "DONE"
                    skip_section = True  # DONE 不参与告警
                elif "OVERDUE" in line:
                    current_section = "OVERDUE"
                    skip_section = False
                continue

            if skip_section:
                continue

        # 跳过空行、注释、标题
        if not line or line.startswith("#") or line.startswith("<!--"):
            continue

        # 跳过占位文本
        if line.startswith("（") and line.endswith("）"):
            continue

        # 跳过已完成事件（旧格式兼容）
        if not is_sectioned and re.match(r"^-\s*\[x\]", line, re.IGNORECASE):
            continue

        # 解析事件行
        m = EVENT_RE.match(line)
        if not m:
            continue

        checkbox = m.group(1)
        date_str = m.group(2)
        description = m.group(3).strip()
        rest = m.group(4) or ""

        # 跳过已完成
        if checkbox and checkbox.lower() == "x":
            continue

        # 解析日期
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning("日期格式错误: %s", date_str)
            continue

        days_until = (event_date - today).days

        # OVERDUE 区的事件无论日期都显示
        if current_section == "OVERDUE":
            pass  # 不过滤
        elif days_until > lookahead_days:
            continue  # 超过范围的未来事件不显示

        # 解析分类 [tag]
        category = None
        cat_match = re.search(r"\[([^\]]+)\]", rest)
        if cat_match:
            category = cat_match.group(1)

        # 解析时间 @time:HH:MM
        time_str = None
        time_match = re.search(r"@time:(\d{1,2}:\d{2}(?:-\d{1,2}:\d{2})?)", rest)
        if time_match:
            time_str = time_match.group(1)

        # 解析来源
        src = None
        src_match = re.search(r"@src:(\w+)", rest)
        if src_match:
            src = src_match.group(1)

        # 判断紧急程度
        overdue = days_until < 0 or current_section == "OVERDUE"
        if overdue:
            urgency = "overdue"
        elif days_until <= URGENT_DAYS:
            urgency = "urgent"
        elif days_until <= WARNING_DAYS:
            urgency = "warning"
        else:
            urgency = "notice"

        events.append({
            "date": event_date,
            "date_str": date_str,
            "description": description,
            "category": category,
            "time": time_str,
            "src": src,
            "days_until": days_until,
            "urgency": urgency,
            "overdue": overdue,
            "section": current_section,
        })

    # 按日期排序
    events.sort(key=lambda e: e["date"])
    return events


def check_upcoming(lookahead_days: int = 7) -> dict:
    """
    检查 upcoming.md 中最近 N 天内的事件。

    返回：
    {
        "events": [dict],           # 所有事件
        "urgent": [dict],           # ≤1天
        "warning": [dict],          # 1-3天
        "notice": [dict],           # 3-7天
        "overdue": [dict],          # 已过期
        "total": int,
        "has_urgent": bool,
        "error": str | None,
    }
    """
    result = {
        "events": [],
        "urgent": [],
        "warning": [],
        "notice": [],
        "overdue": [],
        "total": 0,
        "has_urgent": False,
        "error": None,
    }

    if not UPCOMING_FILE.exists():
        logger.debug("upcoming.md 不存在，跳过未来事件检查")
        return result

    try:
        content = UPCOMING_FILE.read_text(encoding="utf-8")
    except Exception as e:
        result["error"] = f"读取 upcoming.md 失败: {e}"
        logger.error(result["error"])
        return result

    today = datetime.now().date()
    events = _parse_upcoming_file(content, today, lookahead_days)

    result["events"] = events
    result["total"] = len(events)

    for ev in events:
        urgency = ev["urgency"]
        if urgency == "overdue":
            result["overdue"].append(ev)
        elif urgency == "urgent":
            result["urgent"].append(ev)
        elif urgency == "warning":
            result["warning"].append(ev)
        else:
            result["notice"].append(ev)

    result["has_urgent"] = len(result["urgent"]) > 0 or len(result["overdue"]) > 0

    logger.info(
        "upcoming 检查: 共%d事件 (紧急:%d, 注意:%d, 提醒:%d, 已过期:%d)",
        result["total"],
        len(result["urgent"]),
        len(result["warning"]),
        len(result["notice"]),
        len(result["overdue"]),
    )

    return result


def format_upcoming_for_master(result: dict) -> list:
    """
    将 upcoming 结果格式化为 MASTER.md 的行列表。
    """
    lines = []
    total = result.get("total", 0)

    if result.get("error"):
        lines.append(f"（错误: {result['error']}）")
        return lines

    if total == 0:
        lines.append("（7天内无待办事件）")
        return lines

    urgency_icons = {
        "overdue": "🔴过期",
        "urgent": "🔴",
        "warning": "🟡",
        "notice": "🔵",
    }

    for ev in result["events"]:
        icon = urgency_icons.get(ev["urgency"], "🔵")
        days = ev["days_until"]
        if days == 0:
            day_label = "今天"
        elif days == 1:
            day_label = "明天"
        elif days < 0:
            day_label = f"已过期{abs(days)}天"
        else:
            day_label = f"{days}天后"

        time_part = f" @{ev['time']}" if ev.get("time") else ""
        cat_part = f" [{ev['category']}]" if ev.get("category") else ""
        src_part = f" ({ev['src']})" if ev.get("src") else ""

        lines.append(
            f"- {icon} {ev['date_str']}({day_label}){time_part} {ev['description']}{cat_part}{src_part}"
        )

    return lines
