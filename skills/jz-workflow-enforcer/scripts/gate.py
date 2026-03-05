#!/usr/bin/env python3
"""
Gate - 任务执行前的强制检查点
"""

import argparse
import sys
import yaml
from pathlib import Path

# ANSI colors
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
RESET = "\033[0m"

GATE_CONFIGS = {
    "content": {
        "name": "内容创作",
        "checklist": [
            "已读相关 SKILL.md（contentgen / writing-style）",
            "已确认目标账号/平台",
            "已检查 style-context.yaml（如分段任务）",
        ],
        "skills_to_read": [
            "contentgen",
            "writing-style",
        ],
        "key_points": [
            "即时感：像聊天不像报告",
            "口语化短句：不要书面语",
            "有具体数字或例子",
            "去 AI 味：检查禁用词",
        ],
    },
    "code": {
        "name": "代码修改",
        "checklist": [
            "已确认修改范围",
            "已检查是否涉及核心文件",
            "已准备回滚方案",
        ],
        "key_points": [
            "改前先测试现有行为",
            "改后立即验证",
            "核心文件需要额外确认",
        ],
    },
    "deploy": {
        "name": "部署操作",
        "checklist": [
            "已确认目标环境",
            "已备份当前状态",
            "已准备回滚命令",
        ],
        "key_points": [
            "先在测试环境验证",
            "记录部署时间和版本",
            "保持回滚能力",
        ],
    },
}


def print_gate(task_type: str, platform: str = None, account: str = None):
    """打印 gate 检查输出"""
    
    config = GATE_CONFIGS.get(task_type)
    if not config:
        print(f"{RED}❌ 未知任务类型: {task_type}{RESET}")
        print(f"支持的类型: {', '.join(GATE_CONFIGS.keys())}")
        sys.exit(1)
    
    print("═" * 55)
    print(f"{RED}🚧 硬门禁：{config['name']}前检查{RESET}")
    print("═" * 55)
    print()
    
    # 平台和账号信息
    if platform or account:
        if platform:
            print(f"{GREEN}📝 平台:{RESET} {platform}")
        if account:
            print(f"{GREEN}👤 账号:{RESET} {account}")
        print()
    
    # 必读 Skills
    if "skills_to_read" in config:
        print("═" * 55)
        print(f"{YELLOW}📚 必读 Skills:{RESET}")
        print("═" * 55)
        print()
        for skill in config["skills_to_read"]:
            print(f"  • {skill}")
        print()
    
    # 要点
    if "key_points" in config:
        print(f"{YELLOW}【关键要点】{RESET}")
        for point in config["key_points"]:
            print(f"  • {point}")
        print()
    
    # Checklist
    print("═" * 55)
    print(f"{CYAN}📋 Checklist (必须全部确认):{RESET}")
    print("═" * 55)
    print()
    for i, item in enumerate(config["checklist"], 1):
        print(f"[ ] {i}. {item}")
    print()
    
    # 强制输出格式提醒
    print("═" * 55)
    print(f"{YELLOW}⚠️ 强制输出格式要求:{RESET}")
    print("═" * 55)
    print()
    print("第一条回复必须包含：")
    print()
    print("📋 Task Checklist")
    print("□ 已跑 gate")
    print("□ 已读相关 skill")
    if account:
        print(f"□ Account: {account}")
    print()
    print(f"{RED}没有这个块 = 不能开始任务{RESET}")
    print()
    print("═" * 55)


def main():
    parser = argparse.ArgumentParser(description="Gate - 任务执行前的强制检查点")
    parser.add_argument("task_type", choices=list(GATE_CONFIGS.keys()) + ["custom"],
                        help="任务类型")
    parser.add_argument("--platform", "-p", help="目标平台")
    parser.add_argument("--account", "-a", help="目标账号")
    parser.add_argument("--config", "-c", help="自定义配置文件 (用于 custom 类型)")
    
    args = parser.parse_args()
    
    if args.task_type == "custom":
        if not args.config:
            print(f"{RED}❌ custom 类型需要 --config 参数{RESET}")
            sys.exit(1)
        # TODO: 加载自定义配置
        print(f"{YELLOW}自定义配置暂未实现{RESET}")
        sys.exit(1)
    
    print_gate(args.task_type, args.platform, args.account)


if __name__ == "__main__":
    main()
