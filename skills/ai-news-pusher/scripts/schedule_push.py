#!/usr/bin/env python3
"""
定时推送任务管理脚本 - 支持OpenClaw Cron系统
"""

import os
import sys
import json
import argparse
from datetime import datetime

# OpenClaw Gateway配置
GATEWAY_URL = os.environ.get('OPENCLAW_GATEWAY_URL', 'http://localhost:8080')
GATEWAY_TOKEN = os.environ.get('OPENCLAW_GATEWAY_TOKEN', '')


def create_cron_job(schedule_time, limit=8, target_channel=None):
    """
    创建定时推送任务
    
    Args:
        schedule_time: Cron表达式或时间字符串
        limit: 推送新闻数量
        target_channel: 目标频道（如feishu）
    """
    job_name = f"ai-news-push-{datetime.now().strftime('%Y%m%d')}"
    
    # 构建cron schedule
    # 支持 "0 9 * * *" (cron格式) 或 "09:00" (时间格式)
    if ':' in schedule_time and ' ' not in schedule_time:
        # 时间格式如 "09:00"
        hour, minute = schedule_time.split(':')
        cron_expr = f"{int(minute)} {int(hour)} * * *"
    else:
        # 已经是cron格式
        cron_expr = schedule_time
    
    # 构建job配置
    job_config = {
        "name": job_name,
        "schedule": {
            "kind": "cron",
            "expr": cron_expr,
            "tz": "Asia/Shanghai"
        },
        "payload": {
            "kind": "agentTurn",
            "message": f"获取并推送AI新闻 (limit={limit})"
        },
        "sessionTarget": "isolated",
        "enabled": True
    }
    
    # 输出配置供用户手动创建
    print(f"\n=== 定时任务配置 ===")
    print(f"任务名称: {job_name}")
    print(f"Cron表达式: {cron_expr}")
    print(f"推送数量: {limit} 条")
    print(f"目标频道: {target_channel or 'feishu'}")
    print(f"\nJSON配置:\n{json.dumps(job_config, ensure_ascii=False, indent=2)}")
    
    return job_config


def list_cron_jobs():
    """列出所有定时任务"""
    print("\n=== 现有定时任务 ===")
    print("请使用 OpenClaw CLI 查看:\n")
    print("  openclaw cron list")
    print("\n或通过 Gateway API 查询")


def delete_cron_job(job_id):
    """删除定时任务"""
    print(f"\n=== 删除定时任务 ===")
    print(f"任务ID: {job_id}")
    print("\n请使用以下命令删除:\n")
    print(f"  openclaw cron remove {job_id}")


def test_push(limit=5):
    """测试推送"""
    print(f"\n=== 测试推送 ===")
    print(f"将获取并推送 {limit} 条AI新闻到Feishu")
    print("\n请运行:\n")
    print(f"  python3 scripts/fetch_ai_news.py --limit {limit}")


def main():
    parser = argparse.ArgumentParser(
        description='AI新闻定时推送任务管理',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 创建每天9点推送任务
  python3 schedule_push.py create --time "0 9 * * *"
  
  # 使用简写时间格式
  python3 schedule_push.py create --time "09:00" --limit 10
  
  # 测试推送
  python3 schedule_push.py test --limit 5
  
  # 查看任务列表
  python3 schedule_push.py list
  
  # 删除任务
  python3 schedule_push.py delete --job-id <任务ID>
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # create命令
    create_parser = subparsers.add_parser('create', help='创建定时推送任务')
    create_parser.add_argument('--time', required=True, 
                              help='定时时间 (cron表达式如 "0 9 * * *" 或时间格式如 "09:00")')
    create_parser.add_argument('--limit', type=int, default=8, 
                              help='每次推送的新闻数量 (默认8)')
    create_parser.add_argument('--channel', default='feishu', 
                              help='目标频道 (默认feishu)')
    
    # list命令
    subparsers.add_parser('list', help='列出所有定时任务')
    
    # delete命令
    delete_parser = subparsers.add_parser('delete', help='删除定时任务')
    delete_parser.add_argument('--job-id', required=True, help='任务ID')
    
    # test命令
    test_parser = subparsers.add_parser('test', help='测试推送')
    test_parser.add_argument('--limit', type=int, default=5, help='测试推送的新闻数量')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    if args.command == 'create':
        create_cron_job(args.time, args.limit, args.channel)
    elif args.command == 'list':
        list_cron_jobs()
    elif args.command == 'delete':
        delete_cron_job(args.job_id)
    elif args.command == 'test':
        test_push(args.limit)


if __name__ == '__main__':
    main()