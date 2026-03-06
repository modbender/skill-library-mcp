#!/usr/bin/env python3
"""MASTER.md 渲染模块：将各项检查结果渲染为 token 极简格式"""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("heartbeat.renderer")

WORKSPACE = Path(__file__).parent.parent / "workspace"


def render_master(
    daily_result: dict,
    todo_result: dict,
    ongoing_result: dict,
    mail_result: dict,
    health_info: dict,
    alerts: list = None,
    upcoming_result: dict = None,
) -> str:
    """
    渲染 MASTER.md 内容

    参数:
        daily_result: checker.check_daily() 的结果
        todo_result: checker.check_todo() 的结果
        ongoing_result: checker.check_ongoing() 的结果
        mail_result: mail.check_mail() 的结果
        health_info: health_score.record_score() 的结果
        alerts: 告警信息列表

    返回:
        MASTER.md 的完整内容
    """
    now = datetime.now()
    lines = []

    # 标题
    lines.append(f"# EVA MASTER | {now.strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    # SYS 段
    beat_count = health_info.get("beat_count", 0)
    beat_ok = health_info.get("beat_ok_count", 0)
    streak = health_info.get("streak", 0)
    score = health_info.get("score", 0)
    last = now.strftime("%H:%M")
    lines.append("## SYS")
    lines.append(f"beat:{beat_ok}/{beat_count}ok | streak:{streak} | score:{score} | last:{last}")
    lines.append("")

    # DAILY 段
    d_done = daily_result.get("done", 0)
    d_total = daily_result.get("total", 0)
    lines.append(f"## DAILY [{d_done}/{d_total}]")
    if daily_result.get("error"):
        lines.append(f"（{daily_result['error']}）")
    else:
        for item in daily_result.get("items", []):
            mark = "x" if item["done"] else " "
            lines.append(f"- [{mark}] {item['text']}")
    lines.append("")

    # TODO 段
    t_done = todo_result.get("done", 0)
    t_total = todo_result.get("total", 0)
    lines.append(f"## TODO [{t_done}/{t_total}]")
    if todo_result.get("error"):
        lines.append(f"（{todo_result['error']}）")
    else:
        for item in todo_result.get("items", []):
            mark = "x" if item["done"] else " "
            lines.append(f"- [{mark}] {item['text']}")
        if todo_result.get("overdue"):
            lines.append("")
            lines.append("**超期:**")
            for od in todo_result["overdue"]:
                lines.append(f"- ⏰ {od['text']} (due:{od['due']})")
    lines.append("")

    # ONGOING 段
    lines.append("## ONGOING")
    if ongoing_result.get("error"):
        lines.append(f"（{ongoing_result['error']}）")
    else:
        tasks = ongoing_result.get("tasks", [])
        if tasks:
            lines.append("|id|task|st|prio|prog|eta|")
            lines.append("|--|--|--|--|--|--|")
            for t in tasks:
                tid = t.get("id", "?")
                title = t.get("title", "?")
                st = t.get("status", "?")
                prio = t.get("priority", "—")
                prog = t.get("progress", "—")
                if isinstance(prog, (int, float)) and prog > 0:
                    prog = f"{prog}%"
                else:
                    prog = "—"
                eta = t.get("eta", "—")
                lines.append(f"|{tid}|{title}|{st}|{prio}|{prog}|{eta}|")
        else:
            lines.append("（无活跃任务）")
    lines.append("")

    # UPCOMING 段（最近7天内的事件）
    lines.append("## UPCOMING 7D")
    if upcoming_result is not None:
        from tools.upcoming_checker import format_upcoming_for_master
        upcoming_lines = format_upcoming_for_master(upcoming_result)
        lines.extend(upcoming_lines)
    else:
        lines.append("（未启用）")
    lines.append("")

    # MAIL 段
    lines.append("## MAIL")
    if mail_result.get("error"):
        lines.append(f"error:{mail_result['error']}")
    else:
        unread = mail_result.get("unread_count", 0)
        flagged = mail_result.get("flagged_count", 0)
        flagged_from = mail_result.get("flagged_from", [])
        last_check = mail_result.get("last_check", "—")

        flag_detail = ""
        if flagged > 0 and flagged_from:
            # 提取发件人关键词
            senders = []
            for f in flagged_from[:3]:
                # 取邮件地址中 @ 前面的部分
                if "<" in f:
                    addr = f.split("<")[1].rstrip(">")
                else:
                    addr = f
                name = addr.split("@")[0] if "@" in addr else addr
                senders.append(name)
            flag_detail = f"({','.join(senders)})"

        lines.append(f"unread:{unread} flag:{flagged}{flag_detail} last:{last_check}")
    lines.append("")

    # ALERTS 段
    lines.append("## ALERTS")
    if alerts:
        for alert in alerts:
            lines.append(f"- {alert}")
    else:
        lines.append("（无）")
    lines.append("")

    return "\n".join(lines)


def write_master(content: str):
    """原子写入 MASTER.md"""
    path = WORKSPACE / "MASTER.md"
    tmp_path = path.with_suffix(".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.rename(path)
    logger.info("MASTER.md 已更新")
