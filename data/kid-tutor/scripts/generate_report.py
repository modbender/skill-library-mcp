#!/usr/bin/env python3
"""
生成学习报告的脚本。
读取学习记录JSON，生成Markdown格式的家长报告。

用法:
  python3 generate_report.py <data_dir> [--child <name>] [--days <n>]

数据目录结构:
  <data_dir>/
    profile.json        — 孩子的个人档案
    sessions/           — 每次学习会话记录
      2026-02-27_1030.json
      ...
"""

import json
import sys
import os
import glob
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from pathlib import Path


def load_profile(data_dir):
    """加载孩子档案"""
    path = os.path.join(data_dir, "profile.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"name": "小朋友", "grade": 3, "age": 9}


def load_sessions(data_dir, days=7):
    """加载最近N天的学习记录"""
    sessions_dir = os.path.join(data_dir, "sessions")
    if not os.path.exists(sessions_dir):
        return []

    cutoff = datetime.now() - timedelta(days=days)
    sessions = []

    for fpath in sorted(glob.glob(os.path.join(sessions_dir, "*.json"))):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                session = json.load(f)
            # 解析日期
            fname = os.path.basename(fpath).replace(".json", "")
            session_date = datetime.strptime(fname[:10], "%Y-%m-%d")
            if session_date >= cutoff:
                session["_date"] = fname[:10]
                sessions.append(session)
        except (json.JSONDecodeError, ValueError):
            continue

    return sessions


def analyze_sessions(sessions):
    """分析学习数据"""
    stats = {
        "total_sessions": len(sessions),
        "total_questions": 0,
        "correct": 0,
        "incorrect": 0,
        "helped": 0,  # 需要引导后答对
        "subjects": Counter(),
        "topics": Counter(),
        "weak_topics": Counter(),
        "strong_topics": Counter(),
        "difficulty_dist": Counter(),
        "daily_minutes": defaultdict(int),
        "streaks": [],  # 连续答对记录
    }

    for s in sessions:
        questions = s.get("questions", [])
        stats["total_questions"] += len(questions)
        stats["daily_minutes"][s.get("_date", "unknown")] += s.get("duration_minutes", 0)

        for q in questions:
            subject = q.get("subject", "数学")
            topic = q.get("topic", "未分类")
            result = q.get("result", "unknown")  # correct/incorrect/helped
            difficulty = q.get("difficulty", 1)

            stats["subjects"][subject] += 1
            stats["topics"][topic] += 1
            stats["difficulty_dist"][difficulty] += 1

            if result == "correct":
                stats["correct"] += 1
                stats["strong_topics"][topic] += 1
            elif result == "incorrect":
                stats["incorrect"] += 1
                stats["weak_topics"][topic] += 1
            elif result == "helped":
                stats["helped"] += 1
                # 需要帮助也算半个弱项
                stats["weak_topics"][topic] += 0.5

    # 计算正确率
    if stats["total_questions"] > 0:
        stats["accuracy"] = stats["correct"] / stats["total_questions"] * 100
        stats["helped_rate"] = stats["helped"] / stats["total_questions"] * 100
    else:
        stats["accuracy"] = 0
        stats["helped_rate"] = 0

    return stats


def generate_markdown(profile, stats, days):
    """生成Markdown报告"""
    name = profile.get("name", "小朋友")
    grade = profile.get("grade", "?")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = []
    lines.append(f"# 📚 {name}的学习报告")
    lines.append(f"")
    lines.append(f"**生成时间**: {now}")
    lines.append(f"**统计周期**: 最近{days}天")
    lines.append(f"**年级**: {grade}年级")
    lines.append(f"")

    # 总览
    lines.append(f"## 📊 学习总览")
    lines.append(f"")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"|------|------|")
    lines.append(f"| 学习次数 | {stats['total_sessions']}次 |")
    lines.append(f"| 总题数 | {stats['total_questions']}题 |")
    lines.append(f"| 独立答对 | {stats['correct']}题 ({stats['accuracy']:.0f}%) |")
    lines.append(f"| 引导后答对 | {stats['helped']}题 ({stats['helped_rate']:.0f}%) |")
    lines.append(f"| 答错 | {stats['incorrect']}题 |")
    lines.append(f"")

    total_minutes = sum(stats["daily_minutes"].values())
    if total_minutes > 0:
        lines.append(f"**总学习时长**: {total_minutes}分钟 (日均{total_minutes // max(days, 1)}分钟)")
        lines.append(f"")

    # 学科分布
    if stats["subjects"]:
        lines.append(f"## 📖 学科分布")
        lines.append(f"")
        for subject, count in stats["subjects"].most_common():
            pct = count / stats["total_questions"] * 100 if stats["total_questions"] > 0 else 0
            bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
            lines.append(f"- **{subject}**: {count}题 ({pct:.0f}%) {bar}")
        lines.append(f"")

    # 强项
    if stats["strong_topics"]:
        lines.append(f"## 💪 掌握较好的知识点")
        lines.append(f"")
        for topic, count in stats["strong_topics"].most_common(5):
            lines.append(f"- ✅ {topic} (答对{int(count)}次)")
        lines.append(f"")

    # 薄弱点
    if stats["weak_topics"]:
        lines.append(f"## 🎯 需要加强的知识点")
        lines.append(f"")
        for topic, count in stats["weak_topics"].most_common(5):
            lines.append(f"- ⚠️ {topic} (出错/需帮助{int(count)}次)")
        lines.append(f"")

    # 每日学习情况
    if stats["daily_minutes"]:
        lines.append(f"## 📅 每日学习记录")
        lines.append(f"")
        lines.append(f"| 日期 | 学习时长 |")
        lines.append(f"|------|---------|")
        for date in sorted(stats["daily_minutes"].keys()):
            minutes = stats["daily_minutes"][date]
            bars = "🟩" * (minutes // 5) if minutes > 0 else "—"
            lines.append(f"| {date} | {minutes}分钟 {bars} |")
        lines.append(f"")

    # 建议
    lines.append(f"## 💡 学习建议")
    lines.append(f"")
    if stats["accuracy"] >= 80:
        lines.append(f"- 🌟 正确率很高！可以适当提升难度，尝试更有挑战性的题目")
    elif stats["accuracy"] >= 60:
        lines.append(f"- 📈 正在稳步进步！建议继续当前难度，巩固薄弱环节")
    else:
        lines.append(f"- 🤗 不要急，慢慢来！建议降低难度，先打好基础再提升")

    if stats["helped_rate"] > 30:
        lines.append(f"- 💬 经常需要引导才答对，说明理解还不够深入。建议复习时多问\"为什么\"")

    if stats["weak_topics"]:
        top_weak = stats["weak_topics"].most_common(1)[0][0]
        lines.append(f"- 🎯 重点关注「{top_weak}」，下次学习会优先复习这个知识点")

    if total_minutes > 0 and total_minutes / max(days, 1) < 10:
        lines.append(f"- ⏰ 日均学习时间偏少，建议每天保持15-20分钟的学习习惯")

    lines.append(f"")
    lines.append(f"---")
    lines.append(f"*报告由AI家教助手自动生成*")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="生成学习报告")
    parser.add_argument("data_dir", help="数据目录路径")
    parser.add_argument("--days", type=int, default=7, help="统计天数 (默认7)")
    parser.add_argument("--output", "-o", help="输出文件路径 (默认打印到stdout)")
    args = parser.parse_args()

    profile = load_profile(args.data_dir)
    sessions = load_sessions(args.data_dir, days=args.days)
    stats = analyze_sessions(sessions)
    report = generate_markdown(profile, stats, args.days)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"报告已保存到: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
