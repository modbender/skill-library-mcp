#!/usr/bin/env python3
"""
小红书评论管理器 - 测试版
功能：查看评论、回复评论、自动回复
"""

import argparse
import os
import sys
import json
import time
import random
from typing import List, Optional, Dict, Any

# 加载 Cookie
def load_cookie() -> str:
    """从 memory 加载 Cookie"""
    try:
        with open(os.path.expanduser('~/.openclaw/workspace/memory/xhs-cookie.md'), 'r') as f:
            content = f.read()
            # 尝试从 markdown 中提取 JSON
            import re
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
            if json_match:
                cookie_data = json.loads(json_match.group(1))
                return '; '.join([f"{k}={v}" for k, v in cookie_data.items()])
    except Exception as e:
        print(f"❌ 加载 Cookie 失败: {e}")
        sys.exit(1)


class CommentManager:
    """评论管理器"""
    
    def __init__(self, cookie: str):
        self.cookie = cookie
        self.client = None
        self.init_client()
    
    def init_client(self):
        """初始化小红书客户端"""
        try:
            from xhs import XhsClient
            from xhs.help import sign as local_sign
        except ImportError:
            print("❌ 错误: 缺少 xhs 库，请运行: pip install xhs")
            sys.exit(1)
        
        def sign_func(uri, data=None, a1="", web_session=""):
            cookies = {}
            for item in self.cookie.split(';'):
                if '=' in item:
                    k, v = item.split('=', 1)
                    cookies[k.strip()] = v.strip()
            a1_from_cookie = cookies.get('a1', '')
            return local_sign(uri, data, a1=a1_from_cookie or a1)
        
        self.client = XhsClient(cookie=self.cookie, sign=sign_func)
        print("✅ 客户端初始化成功")
    
    def get_comments(self, note_id: str) -> List[Dict]:
        """获取笔记评论"""
        try:
            print(f"\n🔍 正在获取笔记 {note_id} 的评论...")
            comments = self.client.get_note_comments(note_id)
            
            if not comments:
                print("💬 暂无评论")
                return []
            
            print(f"✅ 获取到 {len(comments)} 条评论:\n")
            for i, c in enumerate(comments, 1):
                user = c.get('user', {}).get('nickname', '未知用户')
                content = c.get('content', '')
                likes = c.get('like_count', 0)
                print(f"{i}. 👤 {user}: {content[:50]}... (👍 {likes})")
            
            return comments
            
        except Exception as e:
            print(f"❌ 获取评论失败: {e}")
            return []
    
    def reply_comment(self, note_id: str, comment_id: str, content: str) -> bool:
        """回复指定评论"""
        try:
            print(f"\n💬 正在回复评论 {comment_id}...")
            result = self.client.comment_note(note_id, content, parent_comment_id=comment_id)
            print(f"✅ 回复成功: {content}")
            return True
        except Exception as e:
            print(f"❌ 回复失败: {e}")
            return False
    
    def post_comment(self, note_id: str, content: str) -> bool:
        """发表评论"""
        try:
            print(f"\n📝 正在发表评论...")
            # 添加随机延迟，防封号
            delay = random.uniform(3, 8)
            print(f"⏳ 等待 {delay:.1f} 秒...")
            time.sleep(delay)
            
            result = self.client.comment_note(note_id, content)
            print(f"✅ 评论发表成功: {content}")
            return True
        except Exception as e:
            print(f"❌ 评论失败: {e}")
            return False
    
    def auto_reply(self, note_id: str, keywords: Dict[str, str] = None):
        """自动回复（基于关键词）"""
        if keywords is None:
            keywords = {
                "666": "私信你啦！",
                "好用": "感谢认可！",
                "怎么": "看置顶笔记或私信我～",
                "求": "关注后进群领取！"
            }
        
        print(f"\n🤖 启动自动回复监控（按 Ctrl+C 停止）...")
        print(f"📝 监控笔记: {note_id}")
        print(f"🔑 关键词: {list(keywords.keys())}\n")
        
        seen_comments = set()
        
        try:
            while True:
                comments = self.client.get_note_comments(note_id)
                
                for c in comments:
                    comment_id = c.get('id')
                    content = c.get('content', '').lower()
                    
                    if comment_id in seen_comments:
                        continue
                    
                    seen_comments.add(comment_id)
                    
                    # 检查关键词
                    for keyword, reply in keywords.items():
                        if keyword in content:
                            print(f"🎯 触发关键词 '{keyword}': {content[:30]}...")
                            self.reply_comment(note_id, comment_id, reply)
                            break
                
                # 随机间隔 30-60 秒
                wait = random.uniform(30, 60)
                print(f"⏳ {wait:.0f}秒后再次检查...")
                time.sleep(wait)
                
        except KeyboardInterrupt:
            print("\n👋 自动回复已停止")


def main():
    parser = argparse.ArgumentParser(description='小红书评论管理器')
    parser.add_argument('--note-id', required=True, help='笔记ID')
    parser.add_argument('--action', choices=['list', 'reply', 'post', 'auto'], 
                       default='list', help='操作类型')
    parser.add_argument('--comment-id', help='评论ID（回复时使用）')
    parser.add_argument('--content', help='回复内容')
    
    args = parser.parse_args()
    
    # 加载 Cookie
    cookie = load_cookie()
    
    # 初始化管理器
    manager = CommentManager(cookie)
    
    # 执行操作
    if args.action == 'list':
        manager.get_comments(args.note_id)
    
    elif args.action == 'reply':
        if not args.comment_id or not args.content:
            print("❌ 错误: --reply 需要 --comment-id 和 --content")
            sys.exit(1)
        manager.reply_comment(args.note_id, args.comment_id, args.content)
    
    elif args.action == 'post':
        if not args.content:
            print("❌ 错误: --post 需要 --content")
            sys.exit(1)
        manager.post_comment(args.note_id, args.content)
    
    elif args.action == 'auto':
        manager.auto_reply(args.note_id)


if __name__ == '__main__':
    main()
