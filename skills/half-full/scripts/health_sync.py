#!/usr/bin/env python3
"""
半饱 - Apple Health 数据接收器

解析从 iPhone Shortcuts 发来的健康数据，存入本地记录。

用法（agent 调用）:
  python3 health_sync.py parse "[半饱数据] 步数：8432 步，活动消耗：312 千卡，体重：83.5 kg"
  python3 health_sync.py today        # 查看今天的运动数据
  python3 health_sync.py history 7    # 最近7天
"""

import json
import re
import argparse
from datetime import datetime, date
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ACTIVITY_LOG = DATA_DIR / "activity.json"


def load_activity() :
    if ACTIVITY_LOG.exists():
        return json.loads(ACTIVITY_LOG.read_text())
    return {"records": []}


def save_activity(data: dict):
    DATA_DIR.mkdir(exist_ok=True)
    ACTIVITY_LOG.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def parse_health_message(text: str):
    """
    解析 iPhone Shortcuts 发来的消息。
    格式：[半饱数据] 步数：8432 步，活动消耗：312 千卡，体重：83.5 kg
    字段都是可选的，有啥解析啥。
    """
    if "[半饱数据]" not in text:
        return None

    result = {"date": date.today().isoformat(), "source": "apple_health"}

    # 步数
    m = re.search(r"步数[：:]\s*([\d,]+)\s*步", text)
    if m:
        result["steps"] = int(m.group(1).replace(",", ""))

    # 活动消耗（千卡）
    m = re.search(r"活动消耗[：:]\s*([\d.]+)\s*千卡", text)
    if m:
        result["active_calories"] = float(m.group(1))

    # 体重
    m = re.search(r"体重[：:]\s*([\d.]+)\s*kg", text, re.IGNORECASE)
    if m:
        result["weight_kg"] = float(m.group(1))

    # 静息消耗（可选，Shortcuts 可以加）
    m = re.search(r"静息[：:]\s*([\d.]+)\s*千卡", text)
    if m:
        result["resting_calories"] = float(m.group(1))

    # 站立小时（可选）
    m = re.search(r"站立[：:]\s*([\d]+)\s*小时", text)
    if m:
        result["stand_hours"] = int(m.group(1))

    return result if len(result) > 2 else None  # 至少有一个有效字段


def save_record(record: dict) :
    """存入 activity.json，同一天的数据覆盖更新"""
    data = load_activity()
    today = record["date"]

    # 找今天的记录
    existing = next((r for r in data["records"] if r["date"] == today), None)
    if existing:
        existing.update(record)
    else:
        data["records"].append(record)

    # 只保留最近 90 天
    data["records"] = sorted(data["records"], key=lambda r: r["date"])[-90:]
    save_activity(data)

    # 如果有体重，同步到 weight.json
    if "weight_kg" in record:
        _sync_weight(today, record["weight_kg"])

    return record


def _sync_weight(date_str: str, kg: float):
    """同步体重到 weight.json"""
    weight_path = DATA_DIR / "weight.json"
    if weight_path.exists():
        w = json.loads(weight_path.read_text())
    else:
        w = {"records": []}

    existing = next((r for r in w["records"] if r["date"] == date_str), None)
    if existing:
        existing["kg"] = kg
    else:
        w["records"].append({"date": date_str, "kg": kg})

    w["records"] = sorted(w["records"], key=lambda r: r["date"])
    weight_path.write_text(json.dumps(w, ensure_ascii=False, indent=2))


def get_today() :
    data = load_activity()
    today = date.today().isoformat()
    return next((r for r in data["records"] if r["date"] == today), None)


def get_history(days: int = 7) -> list:
    data = load_activity()
    return data["records"][-days:]


def activity_summary(record: dict) -> str:
    """生成给 agent 用的活动摘要（不含数字，用感受描述）"""
    if not record:
        return "今天还没有运动数据"

    steps = record.get("steps", 0)
    calories = record.get("active_calories", 0)

    # 步数感受
    if steps >= 10000:
        step_feel = "走了很多路"
    elif steps >= 6000:
        step_feel = "走动还不少"
    elif steps >= 3000:
        step_feel = "走了一些"
    else:
        step_feel = "今天基本没怎么动"

    # 消耗感受（用食物翻译）
    if calories >= 400:
        cal_feel = "消耗挺多的，大概一顿正餐的量"
    elif calories >= 200:
        cal_feel = "消耗了一些，差不多一碗米饭"
    elif calories >= 100:
        cal_feel = "消耗不多，一个苹果左右"
    else:
        cal_feel = "消耗很少"

    parts = [step_feel]
    if calories:
        parts.append(cal_feel)

    return "，".join(parts)


def cmd_parse(text: str):
    record = parse_health_message(text)
    if not record:
        print(json.dumps({"status": "skip", "reason": "not a health message"}, ensure_ascii=False))
        return

    saved = save_record(record)
    summary = activity_summary(saved)

    print(json.dumps({
        "status": "ok",
        "record": saved,
        "summary": summary,
    }, ensure_ascii=False, indent=2))


def cmd_today():
    record = get_today()
    summary = activity_summary(record)
    print(json.dumps({
        "record": record,
        "summary": summary,
    }, ensure_ascii=False, indent=2))


def cmd_history(days: int):
    records = get_history(days)
    print(json.dumps(records, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="半饱 Apple Health 数据接收")
    sub = parser.add_subparsers(dest="command")

    parse_p = sub.add_parser("parse", help="解析健康消息")
    parse_p.add_argument("text", help="消息内容")

    sub.add_parser("today", help="今天的运动数据")

    hist_p = sub.add_parser("history", help="历史数据")
    hist_p.add_argument("days", type=int, default=7, nargs="?")

    args = parser.parse_args()

    if args.command == "parse":
        cmd_parse(args.text)
    elif args.command == "today":
        cmd_today()
    elif args.command == "history":
        cmd_history(args.days)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
