#!/usr/bin/env python3
"""
A 股每日投资报告 Pro - 定时推送脚本
每天 9:25 自动生成报告并推送到飞书
"""

import os
import sys
import subprocess
from datetime import datetime

# 技能目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = "/tmp"
DATE_STR = datetime.now().strftime("%Y%m%d")

def main():
    print(f"📈 A 股每日投资报告 - {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
    print("=" * 50)
    
    # 1. 生成报告
    print("1️⃣ 生成报告...")
    report_script = os.path.join(SCRIPT_DIR, "generate_report.py")
    output_file = os.path.join(OUTPUT_DIR, f"stock-report-{DATE_STR}")
    
    result = subprocess.run(
        ["python3", report_script, "--format", "both", "--output", output_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 报告生成失败：{result.stderr}")
        return
    
    print(f"✅ 报告生成成功")
    
    # 2. 推送到飞书
    print("2️⃣ 推送到飞书...")
    image_file = f"{output_file}.png"
    
    if os.path.exists(image_file):
        # 使用 openclaw message 命令推送
        # 注意：--target 指定接收人，这里使用当前会话的 user
        message_result = subprocess.run(
            ["openclaw", "message", "send", 
             "--channel", "feishu",
             "--target", "ou_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # 替换为实际用户 ID
             "--media", image_file,
             "--message", f"📈 A 股每日投资报告 - {datetime.now().strftime('%Y年%m月%d日')}"],
            capture_output=True,
            text=True
        )
        
        if message_result.returncode == 0:
            print(f"✅ 飞书推送成功：{image_file}")
        else:
            print(f"❌ 飞书推送失败：{message_result.stderr}")
    else:
        print(f"⚠️ 图片文件不存在：{image_file}")
    
    print("=" * 50)
    print("完成！")

if __name__ == "__main__":
    main()
