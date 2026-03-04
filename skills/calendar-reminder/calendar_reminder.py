#!/usr/bin/env python3
"""
每晚 22:00 运行：
1. 拉取明天的日历日程
2. 按上午/下午分类，注册一次性提醒 cron
3. 发飞书消息汇报结果
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
SKILL_DIR = Path.home() / ".agents/skills/owa-outlook"
sys.path.insert(0, str(SKILL_DIR))

# ── 拉取明天日程 ──────────────────────────────────────────────
def fetch_tomorrow_events():
    result = subprocess.run(
        ["python3", str(SKILL_DIR / "owa_calendar.py"), "--tomorrow", "--json"],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"owa_calendar.py 失败: {result.stderr}")
    return json.loads(result.stdout)


# ── 注册一次性 cron 提醒 ──────────────────────────────────────
_cron_counter = 0

def add_once_cron(at_sh: datetime, message: str):
    """at_sh 是上海时间的 datetime（带 tzinfo=TZ），转成 UTC ISO 传给 --at"""
    global _cron_counter
    _cron_counter += 1
    utc = ZoneInfo("UTC")
    at_utc = at_sh.astimezone(utc)
    at_iso = at_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    name = f"cal-remind-{at_sh.strftime('%Y-%m-%d')}-{_cron_counter}"
    subprocess.run([
        "openclaw", "cron", "add",
        "--name", name,
        "--at", at_iso,
        "--delete-after-run",
        "--message", message,
        "--announce",
        "--channel", "feishu",
    ], check=True, timeout=15)


# ── 主逻辑 ───────────────────────────────────────────────────
def main():
    now = datetime.now(TZ)
    tomorrow = (now + timedelta(days=1)).date()

    try:
        events = fetch_tomorrow_events()
    except Exception as e:
        send_feishu(f"❌ 日历扫描失败：{e}")
        return

    # 过滤全天事件 & 解析时间
    morning = []   # 上午 < 12:00
    afternoon = [] # 下午 >= 12:00
    all_day = []

    for ev in events:
        if ev.get("is_all_day"):
            all_day.append(ev)
            continue
        start_str = ev["start"]  # "2026-03-02 14:00" — 已是上海时间(UTC+8)
        start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        ev["_start_dt"] = start_dt
        ev["_start_sh"] = start_dt.strftime("%H:%M")
        if start_dt.hour < 12:
            morning.append(ev)
        else:
            afternoon.append(ev)

    reminders = []

    # 上午日程：提前2小时
    for ev in morning:
        remind_dt = ev["_start_dt"] - timedelta(hours=2)
        if remind_dt <= now:
            remind_dt = now + timedelta(minutes=2)
        msg = f"📅 提醒（2小时后）：{ev['_start_sh']} {ev['subject']}"
        add_once_cron(remind_dt, msg)
        reminders.append(f"  • {ev['_start_sh']} {ev['subject']} → {remind_dt.strftime('%H:%M')} 提醒")

    # 下午日程：统一 12:00 提醒
    if afternoon:
        remind_dt = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 0, tzinfo=TZ)
        if remind_dt <= now:
            remind_dt = now + timedelta(minutes=2)
        lines = "\n".join([f"  • {ev['_start_sh']} {ev['subject']}" for ev in afternoon])
        msg = f"📅 下午日程提醒：\n{lines}"
        add_once_cron(remind_dt, msg)
        for ev in afternoon:
            reminders.append(f"  • {ev['_start_sh']} {ev['subject']} → 12:00 提醒")

    # ── 汇报消息 ─────────────────────────────────────────────
    date_str = tomorrow.strftime("%Y-%m-%d")
    if not events:
        summary = f"✅ 日历扫描完成（{date_str}）\n明天没有日程，好好休息 😴"
    else:
        parts = [f"✅ 日历扫描完成（{date_str}）"]
        if all_day:
            parts.append("📌 全天：")
            for ev in all_day:
                parts.append(f"  • {ev['subject']}")
        if reminders:
            parts.append("⏰ 已设提醒：")
            parts.extend(reminders)
        else:
            parts.append("（无需提醒的日程）")
        summary = "\n".join(parts)

    send_feishu(summary)


def send_feishu(text: str):
    subprocess.run([
        "openclaw", "message", "send",
        "--channel", "feishu",
        "--target", "user:ou_159cbb6a3791ff5a98f3a2a4b38e7d4c",
        "-m", text,
    ], timeout=15)


if __name__ == "__main__":
    main()
