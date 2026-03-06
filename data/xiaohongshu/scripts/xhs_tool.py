#!/usr/bin/env python3
"""
小红书工具 - 使用内置签名
"""

import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

def get_client():
    """获取 XHS 客户端（使用内置签名）"""
    from xhs import XhsClient
    from xhs.help import sign as local_sign
    
    cookie = os.getenv('XHS_COOKIE')
    if not cookie:
        print("❌ 错误: 未配置 XHS_COOKIE")
        sys.exit(1)
    
    def sign_func(uri, data=None, a1="", web_session=""):
        return local_sign(uri, data, a1=a1)
    
    client = XhsClient(cookie=cookie, sign=sign_func)
    return client

def cmd_search(args):
    """搜索笔记"""
    client = get_client()
    print(f"🔍 搜索: {args.keyword}...")
    result = client.get_note_by_keyword(args.keyword)
    notes = result.get('items', [])
    
    print(f"找到 {len(notes)} 条笔记\n")
    for i, item in enumerate(notes[:args.limit], 1):
        note = item.get('note_card', {})
        print(f"{i}. {note.get('display_title', note.get('title', '无标题'))}")
        print(f"   👤 {note.get('user', {}).get('nickname', '未知')}")
        print(f"   ❤️  {note.get('liked_count', 0)}")
        print(f"   🔗 ID: {note.get('note_id', 'N/A')}")
        print()

def cmd_note(args):
    """查看笔记详情"""
    client = get_client()
    print(f"📖 获取笔记...")
    note = client.get_note_by_id(args.note_id, xsec_token=args.token or "")
    
    info = note.get('note_card', note)
    print(f"\n📝 {info.get('title', info.get('display_title', '无标题'))}")
    print(f"{'='*50}")
    print(f"👤 作者: {info.get('user', {}).get('nickname', '未知')}")
    print(f"❤️  点赞: {info.get('interact_info', {}).get('liked_count', 0)}")
    print(f"⭐ 收藏: {info.get('interact_info', {}).get('collected_count', 0)}")
    print(f"💬 评论: {info.get('interact_info', {}).get('comment_count', 0)}")
    print(f"\n📄 内容:\n{info.get('desc', '无内容')}")

def cmd_user(args):
    """查看用户信息"""
    client = get_client()
    print(f"👤 获取用户信息...")
    user = client.get_user_info(args.user_id)
    
    info = user.get('basic_info', user)
    print(f"\n👤 {info.get('nickname', '未知')}")
    print(f"🔴 小红书号: {info.get('red_id', 'N/A')}")
    print(f"📝 简介: {info.get('desc', '无')}")
    print(f"👥 粉丝: {info.get('fans', 0)}")

def cmd_me(args):
    """查看自己的账号"""
    client = get_client()
    print(f"👤 获取账号信息...")
    info = client.get_self_info()
    
    basic = info.get('basic_info', info)
    print(f"\n👤 我的账号")
    print(f"{'='*50}")
    print(f"昵称: {basic.get('nickname', 'N/A')}")
    print(f"小红书号: {basic.get('red_id', 'N/A')}")
    print(f"粉丝: {basic.get('fans', 0)}")

def cmd_publish(args):
    """发布图文笔记"""
    client = get_client()
    
    # 读取内容
    if args.content:
        desc = args.content
    elif args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            desc = f.read()
    else:
        print("❌ 需要 --content 或 --file")
        sys.exit(1)
    
    # 验证图片
    images = []
    for img in args.images:
        if os.path.exists(img):
            images.append(os.path.abspath(img))
        else:
            print(f"⚠️ 图片不存在: {img}")
    
    if not images:
        print("❌ 没有有效图片")
        sys.exit(1)
    
    print(f"📤 准备发布...")
    print(f"   标题: {args.title}")
    print(f"   图片: {len(images)} 张")
    
    if args.dry_run:
        print("\n⚠️ [试运行] 不会实际发布")
        return
    
    result = client.create_image_note(
        title=args.title[:20],
        desc=desc,
        files=images,
        is_private=args.private
    )
    
    print(f"\n✅ 发布成功!")
    if isinstance(result, dict):
        note_id = result.get('note_id') or result.get('id')
        if note_id:
            print(f"🔗 https://www.xiaohongshu.com/explore/{note_id}")

def main():
    parser = argparse.ArgumentParser(description='小红书工具')
    subparsers = parser.add_subparsers(dest='command')
    
    # search
    p = subparsers.add_parser('search', help='搜索笔记')
    p.add_argument('keyword')
    p.add_argument('-n', '--limit', type=int, default=10)
    p.set_defaults(func=cmd_search)
    
    # note
    p = subparsers.add_parser('note', help='查看笔记')
    p.add_argument('note_id')
    p.add_argument('--token', default='')
    p.set_defaults(func=cmd_note)
    
    # user
    p = subparsers.add_parser('user', help='查看用户')
    p.add_argument('user_id')
    p.set_defaults(func=cmd_user)
    
    # me
    p = subparsers.add_parser('me', help='查看自己')
    p.set_defaults(func=cmd_me)
    
    # publish
    p = subparsers.add_parser('publish', help='发布笔记')
    p.add_argument('-t', '--title', required=True)
    p.add_argument('-c', '--content')
    p.add_argument('-f', '--file')
    p.add_argument('-i', '--images', nargs='+', required=True)
    p.add_argument('--private', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p.set_defaults(func=cmd_publish)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
