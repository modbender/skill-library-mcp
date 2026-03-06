#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短视频钩子生成器 - 数据监控脚本
每日 19:00 自动收集使用数据，用于优化和付费转化分析
"""

import json
import os
from datetime import datetime
from pathlib import Path

# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
USAGE_LOG = DATA_DIR / "usage_log.json"
STATS_FILE = DATA_DIR / "daily_stats.json"


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(exist_ok=True)


def load_usage_log():
    """加载使用日志"""
    if USAGE_LOG.exists():
        with open(USAGE_LOG, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"records": []}


def save_usage_log(data):
    """保存使用日志"""
    with open(USAGE_LOG, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def log_usage(topic, hook_type, platform, user_id=None):
    """
    记录一次使用
    
    Args:
        topic: 主题
        hook_type: 钩子类型
        platform: 平台
        user_id: 用户 ID（可选，匿名）
    """
    ensure_data_dir()
    
    log = load_usage_log()
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "hook_type": hook_type or "未指定",
        "platform": platform or "通用",
        "user_id": user_id or "anonymous"
    }
    
    log["records"].append(record)
    
    # 只保留最近 1000 条记录
    if len(log["records"]) > 1000:
        log["records"] = log["records"][-1000:]
    
    save_usage_log(log)
    print(f"✓ 已记录使用：{topic} - {hook_type} - {platform}")


def generate_daily_stats(date=None):
    """
    生成每日统计
    
    Args:
        date: 日期字符串 (YYYY-MM-DD)，默认今天
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    log = load_usage_log()
    
    # 过滤当天的记录
    daily_records = [
        r for r in log["records"]
        if r["timestamp"].startswith(date)
    ]
    
    # 统计分析
    stats = {
        "date": date,
        "total_usage": len(daily_records),
        "topics": {},
        "hook_types": {},
        "platforms": {},
        "peak_hours": []
    }
    
    # 统计主题
    for record in daily_records:
        topic = record["topic"]
        stats["topics"][topic] = stats["topics"].get(topic, 0) + 1
        
        hook_type = record["hook_type"]
        stats["hook_types"][hook_type] = stats["hook_types"].get(hook_type, 0) + 1
        
        platform = record["platform"]
        stats["platforms"][platform] = stats["platforms"].get(platform, 0) + 1
    
    # 按使用次数排序
    stats["top_topics"] = sorted(
        stats["topics"].items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    stats["top_hook_types"] = sorted(
        stats["hook_types"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    stats["top_platforms"] = sorted(
        stats["platforms"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # 保存到文件
    stats_file = STATS_FILE.parent / f"daily_stats_{date}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    return stats


def print_daily_report(date=None):
    """
    打印每日报告
    
    Args:
        date: 日期字符串，默认今天
    """
    stats = generate_daily_stats(date)
    
    print(f"\n{'='*60}")
    print(f"📊 短视频钩子生成器 - 每日报告")
    print(f"📅 日期：{stats['date']}")
    print(f"{'='*60}\n")
    
    print(f"📈 总使用次数：{stats['total_usage']}")
    
    if stats['total_usage'] == 0:
        print("\n暂无数据")
        return
    
    print(f"\n🔥 热门主题 TOP 10:")
    for i, (topic, count) in enumerate(stats['top_topics'], 1):
        print(f"  {i}. {topic}: {count} 次")
    
    print(f"\n🎯 钩子类型分布:")
    for hook_type, count in stats['top_hook_types']:
        percentage = count / stats['total_usage'] * 100
        print(f"  {hook_type}: {count} 次 ({percentage:.1f}%)")
    
    print(f"\n📱 平台分布:")
    for platform, count in stats['top_platforms']:
        percentage = count / stats['total_usage'] * 100
        print(f"  {platform}: {count} 次 ({percentage:.1f}%)")
    
    print(f"\n{'='*60}")
    print(f"💡 优化建议:")
    
    # 根据数据给出建议
    if stats['top_topics']:
        top_topic = stats['top_topics'][0][0]
        print(f"  • 热门主题「{top_topic}」可以增加专属模板")
    
    if stats['top_hook_types']:
        top_type = stats['top_hook_types'][0][0]
        print(f"  • 「{top_type}」最受欢迎，可以优先优化")
    
    print(f"  • 持续收集数据，优化钩子质量")
    print(f"{'='*60}\n")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "log":
            # 记录使用
            topic = sys.argv[2] if len(sys.argv) > 2 else "测试主题"
            hook_type = sys.argv[3] if len(sys.argv) > 3 else None
            platform = sys.argv[4] if len(sys.argv) > 4 else None
            log_usage(topic, hook_type, platform)
        
        elif command == "report":
            # 生成报告
            date = sys.argv[2] if len(sys.argv) > 2 else None
            print_daily_report(date)
        
        elif command == "stats":
            # 生成统计
            date = sys.argv[2] if len(sys.argv) > 2 else None
            stats = generate_daily_stats(date)
            print(json.dumps(stats, ensure_ascii=False, indent=2))
        
        else:
            print("用法:")
            print("  python monitor.py log <主题> [类型] [平台]")
            print("  python monitor.py report [日期]")
            print("  python monitor.py stats [日期]")
    else:
        # 默认显示今日报告
        print_daily_report()


if __name__ == "__main__":
    main()
