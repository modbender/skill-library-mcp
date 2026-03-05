#!/usr/bin/env python3
"""
Geekbench 监控脚本 - 定期运行
支持飞书通知和本地归档
"""

import sys
import os
import time
import json
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from geekbench_crawler import GeekbenchCrawler
from datetime import datetime

# 配置
ARCHIVE_DIR = '/Users/ding/.openclaw/workspace/geekbench/archives'
DATA_DIR = '/Users/ding/.openclaw/workspace/geekbench/data'

def send_to_feishu(message):
    """发送监控报告到飞书"""
    import subprocess
    try:
        cmd = [
            'openclaw', 'message', 'send',
            '--channel', 'feishu',
            '--target', 'ou_b5694469884a90935f9c9b5a687155a1',
            '--message', message
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("Feishu message sent")
            return True
        else:
            print(f"Feishu error: {result.stderr}")
            return False
    except Exception as e:
        print(f"Feishu not available: {e}")
        return False

def save_to_archive(report, timestamp):
    """保存报告到归档目录"""
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # 保存markdown版本
    md_file = os.path.join(ARCHIVE_DIR, f"monitor_{timestamp}.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# Geekbench 监控报告\n\n{report}")
    print(f"Archived: {md_file}")

    # 保存JSON版本
    json_file = os.path.join(ARCHIVE_DIR, f"monitor_{timestamp}.json")
    json_data = {
        'timestamp': datetime.now().isoformat(),
        'report': report
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"JSON archived: {json_file}")

    return md_file, json_file

def cleanup_old_archives(keep_count=30):
    """清理旧归档"""
    try:
        archives = sorted(glob.glob(os.path.join(ARCHIVE_DIR, 'monitor_*.json')),
                         key=os.path.getmtime)
        if len(archives) > keep_count:
            removed = len(archives) - keep_count
            for old_file in archives[:-keep_count]:
                os.remove(old_file)
            print(f"Cleaned {removed} old archives")
    except Exception as e:
        print(f"Archive cleanup failed: {e}")

def main():
    print(f"\n{'='*60}")
    print(f"Geekbench Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    crawler = GeekbenchCrawler()

    print("Fetching latest benchmarks...")
    latest = crawler.get_latest_benchmarks(30)

    if not latest:
        print("Failed to fetch benchmarks")
        return

    # 加载上次记录
    last_file = os.path.join(DATA_DIR, 'last_check.json')
    last_data = {}
    last_ids = set()

    if os.path.exists(last_file):
        with open(last_file, 'r') as f:
            last_data = json.load(f)
        last_ids = set(last_data.get('benchmarks', []))

    current_ids = set(b['id'] for b in latest)
    new_ids = current_ids - last_ids
    new_benchmarks = [b for b in latest if b['id'] in new_ids]

    high_scores = []
    special_devices = []

    print(f"Checking {len(new_benchmarks)} new benchmarks...")

    for b in new_benchmarks[:10]:
        detail = crawler.get_benchmark_detail(b['id'])
        if detail:
            if detail['single_core_score'] > 3000:
                high_scores.append({
                    'id': b['id'],
                    'title': detail['model'] or b['title'],
                    'single': detail['single_core_score'],
                    'multi': detail['multi_core_score'],
                    'url': f"https://browser.geekbench.com/v6/cpu/{b['id']}"
                })

            device_name = detail.get('model', '')
            if device_name and device_name not in last_data.get('known_devices', []):
                special_devices.append({
                    'id': b['id'],
                    'model': device_name,
                    'cpu': detail.get('cpu', {}).get('name', 'N/A'),
                    'os': detail.get('operating_system', 'N/A'),
                    'url': f"https://browser.geekbench.com/v6/cpu/{b['id']}"
                })

            if device_name and device_name not in last_data.get('known_devices', []):
                last_data.setdefault('known_devices', []).append(device_name)

        time.sleep(0.3)

    # 保存当前状态
    current_state = {
        'checked_at': datetime.now().isoformat(),
        'benchmarks': list(current_ids),
        'known_devices': last_data.get('known_devices', [])
    }

    with open(last_file, 'w') as f:
        json.dump(current_state, f, ensure_ascii=False, indent=2)

    # 生成报告
    timestamp_short = datetime.now().strftime("%Y%m%d_%H%M")
    lines = [
        f"Geekbench Monitor Report",
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "-" * 60
    ]

    if new_benchmarks:
        lines.append(f"\nNew Benchmarks ({len(new_benchmarks)}):")
        for b in new_benchmarks[:10]:
            lines.append(f"  - #{b['id']}: {b['title'][:50]}")
    else:
        lines.append("\nNo new benchmarks")

    if high_scores:
        lines.append(f"\nHigh Scores (Single-Core > 3000):")
        for h in high_scores[:5]:
            lines.append(f"  - #{h['id']}: {h['title']}")
            lines.append(f"    Single: {h['single']} | Multi: {h['multi']}")
            lines.append(f"    {h['url']}")

    if special_devices:
        lines.append(f"\nNew Devices:")
        for d in special_devices[:5]:
            lines.append(f"  - {d['model']}")
            lines.append(f"    CPU: {d['cpu']} | OS: {d['os']}")
            lines.append(f"    {d['url']}")

    report = '\n'.join(lines)
    print("\n" + report)

    # 保存到归档
    save_to_archive(report, timestamp_short)
    cleanup_old_archives(keep_count=30)

    # 发送到飞书
    print("\nSending Feishu notification...")
    send_to_feishu(report)

    print(f"\n{'='*60}")
    print("Monitor completed")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
