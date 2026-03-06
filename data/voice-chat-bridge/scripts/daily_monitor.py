#!/usr/bin/env python3
"""
Voice Chat Bridge 每日监控脚本
收集安装数据、bug报告、用户反馈
"""

import os
import json
import datetime
import subprocess

METRICS_DIR = os.path.expanduser("~/.openclaw/workspace/memory/voice-chat-bridge/metrics")
BUGS_DIR = os.path.expanduser("~/.openclaw/workspace/memory/voice-chat-bridge/bugs")
SKILL_DIR = os.path.expanduser("~/.openclaw/skills/voice-chat-bridge")

def get_today():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def ensure_dirs():
    os.makedirs(METRICS_DIR, exist_ok=True)
    os.makedirs(BUGS_DIR, exist_ok=True)

def run_local_tests():
    """运行本地功能测试"""
    results = []
    
    # 测试1: 本地模式
    try:
        result = subprocess.run(
            ["python3", f"{SKILL_DIR}/scripts/generate_voice.py", "测试"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            results.append(("本地模式", "✅ 通过"))
        else:
            results.append(("本地模式", f"❌ 失败: {result.stderr[:100]}"))
    except Exception as e:
        results.append(("本地模式", f"❌ 错误: {e}"))
    
    return results

def check_github_issues():
    """检查 GitHub issues（需要手动查看）"""
    return "请手动检查: https://github.com/openclaw/skills/issues?q=voice-chat-bridge"

def generate_report():
    today = get_today()
    ensure_dirs()
    
    report_file = f"{METRICS_DIR}/{today}.md"
    
    # 运行测试
    test_results = run_local_tests()
    
    report = f"""# Voice Chat Bridge 监控报告 - {today}

## 数据收集时间
{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 安装数据
> ⚠️ 需要手动从 ClawHub 获取
- ClawHub 安装数: [待填写]
- 今日新增: [待填写]
- 评分: [待填写]/5.0

## GitHub 状态
{check_github_issues()}

## 本地功能测试
"""
    
    for test_name, result in test_results:
        report += f"- {test_name}: {result}\n"
    
    report += f"""
## 今日行动项
- [ ] 查看 ClawHub 反馈
- [ ] 回复 GitHub issues
- [ ] 更新文档（如有需要）

## 备注
<!-- 在此添加任何观察或问题 -->

---
*自动生成的监控报告*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 监控报告已生成: {report_file}")
    return report_file

if __name__ == "__main__":
    report_path = generate_report()
    print(f"\n请查看报告并手动补充 ClawHub 数据")
    print(f"报告位置: {report_path}")
