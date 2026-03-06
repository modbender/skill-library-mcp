#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序：自动科研文献汇报系统
整合所有步骤：抓取、过滤、生成摘要、推送
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

def run():
    """主流程"""
    
    print("=" * 60)
    print("🚀 开始执行自动科研文献汇报任务")
    print("=" * 60)
    
    # 步骤1：抓取论文
    print("\n【步骤1】抓取论文...")
    from fetch_papers import main as fetch_papers
    papers = fetch_papers()
    
    if not papers:
        print("❌ 没有找到符合条件的论文")
        return False
    
    # 步骤2：生成摘要
    print("\n【步骤2】生成摘要...")
    from generate_summary import process_papers
    papers_with_summary = process_papers()
    
    # 步骤3：格式化消息
    print("\n【步骤3】格式化消息...")
    from send_to_feishu import format_daily_report
    message = format_daily_report(papers_with_summary)
    
    # 保存消息
    output_file = PROJECT_ROOT / 'data' / 'daily_report.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(message)
    
    print(f"✅ 消息已保存: {output_file}")
    
    # 步骤4：推送到飞书（通过OpenClaw）
    print("\n【步骤4】推送到飞书...")
    print("✅ 任务完成！")
    
    return True

if __name__ == '__main__':
    success = run()
    sys.exit(0 if success else 1)