#!/usr/bin/env python3
"""
即刻热门获取脚本
Jike Hot Topics Fetcher
"""

import json
import sys

def get_jike_hot(limit=10):
    """获取即刻热门（模拟数据）"""
    mock_posts = [
        {"id": 1, "content": "今天换了个新机械键盘，手感太棒了！强烈推荐给大家", "circle": "数码圈", "likes": 1234, "comments": 89, "author": "keyboard_fan"},
        {"id": 2, "content": "分享一下我的投资心得：长期持有才是王道", "circle": "投资圈", "likes": 987, "comments": 156, "author": "investor_zhang"},
        {"id": 3, "content": "远程办公第三年，感觉效率反而提高了", "circle": "职场圈", "likes": 876, "comments": 134, "author": "remote_worker"},
        {"id": 4, "content": "最近在读《置身事内》，推荐给想了解中国经济的朋友", "circle": "读书圈", "likes": 765, "comments": 98, "author": "book_lover"},
        {"id": 5, "content": "新入手的 AirPods Pro 2 体验真不错", "circle": "数码圈", "likes": 654, "comments": 87, "author": "apple_fan"},
        {"id": 6, "content": "今天学到了一个新概念：第一性原理", "circle": "学习圈", "likes": 543, "comments": 76, "author": "learner_wang"},
        {"id": 7, "content": "分享一个提高专注力的方法：番茄工作法", "circle": "效率圈", "likes": 432, "comments": 65, "author": "productivity_guru"},
        {"id": 8, "content": "周末去了趟露营，感觉太治愈了", "circle": "户外圈", "likes": 321, "comments": 54, "author": "outdoor_fan"},
        {"id": 9, "content": "终于把房贷还完了，分享一下这十年的经历", "circle": "生活圈", "likes": 298, "comments": 187, "author": "debt_free"},
        {"id": 10, "content": "推荐一个宝藏播客：无人知晓", "circle": "播客圈", "likes": 234, "comments": 45, "author": "podcast_listener"},
    ]
    return mock_posts[:limit]

def format_output(data):
    output = "💛 即刻热门动态\n\n"
    for item in data:
        likes_k = f"{item['likes'] / 1000:.1f}k" if item['likes'] >= 1000 else str(item['likes'])
        output += f"{item['id']}. {item['content'][:40]}...\n"
        output += f"   📂 {item['circle']} | 💛 {likes_k} | 💬 {item['comments']} | @{item['author']}\n\n"
    return output

def main():
    limit = 10
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
    
    data = get_jike_hot(limit=limit)
    
    if "--json" in sys.argv or "-j" in sys.argv:
        print(json.dumps({"data": data}, ensure_ascii=False, indent=2))
    else:
        print(format_output(data))

if __name__ == "__main__":
    main()
