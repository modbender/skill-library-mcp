#!/usr/bin/env python3
"""
AI新闻推送到Feishu脚本 - 支持真正的Webhook推送
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from pathlib import Path


def get_script_dir():
    """获取脚本所在目录（支持相对路径）"""
    return Path(__file__).parent.absolute()


def load_news_from_file(file_path):
    """从文件加载新闻"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件失败: {e}", file=sys.stderr)
        return []


def fetch_news_from_script(limit=8):
    """通过调用fetch_ai_news脚本获取新闻"""
    import subprocess
    try:
        script_dir = get_script_dir()
        result = subprocess.run(
            ['python3', str(script_dir / 'fetch_ai_news.py'), '--limit', str(limit), '--format', 'json'],
            capture_output=True,
            text=True,
            cwd=str(script_dir)
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"获取新闻失败: {result.stderr}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"获取新闻失败: {e}", file=sys.stderr)
        return []


def fetch_news_multi_source(limit=8):
    """使用多源聚合获取新闻"""
    try:
        from news_sources import get_default_aggregator
        aggregator = get_default_aggregator()
        news = aggregator.fetch_all(query="AI artificial intelligence", limit=limit, days=3)
        return news
    except Exception as e:
        print(f"多源聚合失败，回退到单源: {e}", file=sys.stderr)
        return fetch_news_from_script(limit)


def format_feishu_message(news_list):
    """
    格式化Feishu消息
    
    Args:
        news_list: 新闻列表
    
    Returns:
        str: 格式化后的消息
    """
    if not news_list:
        return "暂无AI新闻"
    
    lines = []
    lines.append("📰 **AI新闻资讯**")
    lines.append(f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"共 {len(news_list)} 条新闻\n")
    lines.append("---\n")
    
    for i, news in enumerate(news_list, 1):
        title = news.get('title', '无标题')
        url = news.get('url', '')
        content = news.get('content', '')[:200]
        source = news.get('source', '未知来源')
        date = news.get('published_date', '')
        source_type = news.get('source_type', '')
        
        # 来源标签
        source_tag = f"[{source}]"
        if source_type:
            source_tag = f"[{source_type.upper()}] {source_tag}"
        
        lines.append(f"**{i}. {title}**")
        lines.append(f"🔗 {url}")
        lines.append(f"📌 {source_tag}")
        if date:
            lines.append(f"📅 {date}")
        if content:
            lines.append(f"> {content}...")
        lines.append("")  # 空行
    
    lines.append("---")
    lines.append("🤖 由 OpenClaw AI 助手推送")
    
    return "\n".join(lines)


def send_to_feishu_webhook(message, webhook_url=None):
    """
    发送消息到Feishu Webhook
    
    Args:
        message: 消息内容（支持Markdown）
        webhook_url: Feishu Webhook URL，如果不提供则从环境变量获取
    
    Returns:
        bool: 是否发送成功
    """
    webhook_url = webhook_url or os.environ.get('FEISHU_WEBHOOK_URL')
    
    if not webhook_url:
        print("❌ 错误: 未设置 FEISHU_WEBHOOK_URL 环境变量", file=sys.stderr)
        print("提示: 在Feishu群聊中添加'自定义机器人'，获取Webhook URL", file=sys.stderr)
        return False
    
    # 构造Feishu消息
    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }
    
    try:
        print(f"正在发送消息到Feishu...")
        response = requests.post(
            webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        if result.get("code") == 0:
            print(f"✅ 消息发送成功！")
            return True
        else:
            print(f"❌ 发送失败: {result.get('msg')}", file=sys.stderr)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ 发送失败: {e}", file=sys.stderr)
        return False


def send_to_feishu(message, channel='feishu', use_webhook=True):
    """
    发送消息到Feishu
    
    Args:
        message: 消息内容
        channel: 渠道名称（默认feishu）
        use_webhook: 是否使用webhook发送（默认True）
    
    Returns:
        bool: 是否发送成功
    """
    print(f"消息已格式化，准备发送到 {channel}")
    print(f"消息长度: {len(message)} 字符")
    
    # 输出消息内容（调试用）
    print("\n=== 消息预览 ===")
    print(message[:500] + "..." if len(message) > 500 else message)
    print("=== 消息结束 ===\n")
    
    if use_webhook:
        # 使用webhook发送
        return send_to_feishu_webhook(message)
    else:
        # 仅打印消息（调试模式）
        print("提示: 使用 --use-webhook 参数或设置 FEISHU_WEBHOOK_URL 环境变量以实际发送消息")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='AI新闻推送到Feishu - 支持真正的Webhook推送',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用示例:
  # 获取并推送新闻到Feishu（需要设置FEISHU_WEBHOOK_URL）
  python3 push_to_feishu.py --limit 8
  
  # 使用多源聚合
  python3 push_to_feishu.py --limit 10 --multi-source
  
  # 从文件加载新闻并推送
  python3 push_to_feishu.py --input news.json
  
  # 仅格式化消息，不发送（干运行模式）
  python3 push_to_feishu.py --limit 5 --dry-run
  
环境变量:
  FEISHU_WEBHOOK_URL    Feishu Webhook URL（必须设置才能实际发送）
        '''
    )
    
    parser.add_argument('--limit', type=int, default=8,
                        help='推送新闻数量 (默认8)')
    parser.add_argument('--input', type=str,
                        help='从文件加载新闻(JSON格式)')
    parser.add_argument('--multi-source', action='store_true',
                        help='使用多源聚合(Tavily+Brave+RSS)')
    parser.add_argument('--channel', type=str, default='feishu',
                        help='推送渠道 (默认feishu)')
    parser.add_argument('--dry-run', action='store_true',
                        help='仅格式化消息，不实际发送')
    parser.add_argument('--use-webhook', action='store_true',
                        help='使用Webhook发送（默认如果设置了FEISHU_WEBHOOK_URL则自动使用）')
    
    args = parser.parse_args()
    
    # 检查环境变量
    webhook_url = os.environ.get('FEISHU_WEBHOOK_URL')
    if not webhook_url and not args.dry_run:
        print("⚠️ 警告: 未设置 FEISHU_WEBHOOK_URL 环境变量", file=sys.stderr)
        print("提示: 使用 --dry-run 参数进行测试，或设置 FEISHU_WEBHOOK_URL 环境变量", file=sys.stderr)
        print("     在Feishu群聊中添加'自定义机器人'获取Webhook URL", file=sys.stderr)
    
    # 加载新闻
    if args.input:
        print(f"从文件加载新闻: {args.input}")
        news_list = load_news_from_file(args.input)
    else:
        print(f"获取新闻 (limit={args.limit}, multi-source={args.multi_source})...")
        if args.multi_source:
            news_list = fetch_news_multi_source(limit=args.limit)
        else:
            news_list = fetch_news_from_script(limit=args.limit)
    
    if not news_list:
        print("❌ 没有获取到新闻", file=sys.stderr)
        sys.exit(1)
    
    print(f"✓ 共获取 {len(news_list)} 条新闻")
    
    # 格式化消息
    message = format_feishu_message(news_list)
    
    if args.dry_run:
        print("\n=== 消息内容 (干运行模式) ===")
        print(message)
        print("\n=== 消息未发送 ===")
        print("提示: 使用 --use-webhook 参数或设置 FEISHU_WEBHOOK_URL 环境变量以实际发送消息")
    else:
        # 发送消息
        use_webhook = args.use_webhook or bool(webhook_url)
        success = send_to_feishu(message, channel=args.channel, use_webhook=use_webhook)
        if success:
            print(f"\n✅ 成功推送 {len(news_list)} 条新闻到 {args.channel}")
        else:
            print(f"\n❌ 推送失败", file=sys.stderr)
            sys.exit(1)


if __name__ == '__main__':
    main()
