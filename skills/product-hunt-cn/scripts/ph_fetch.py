#!/usr/bin/env python3
"""
Product Hunt 获取脚本
Product Hunt Fetcher
"""

import json
import sys
from datetime import datetime

def get_ph_top(limit=10):
    """获取 Product Hunt Top Products（模拟数据）"""
    mock_products = [
        {"rank": 1, "name": "AI Writer Pro", "tagline": "AI 写作助手，让内容创作更简单", "upvotes": 856, "comments": 234, "url": "https://producthunt.com/posts/ai-writer-pro", "category": "AI"},
        {"rank": 2, "name": "Code Assistant", "tagline": "智能编程助手，自动补全代码", "upvotes": 743, "comments": 189, "url": "https://producthunt.com/posts/code-assistant", "category": "Developer Tools"},
        {"rank": 3, "name": "Design Kit 2.0", "tagline": "全新设计工具套件", "upvotes": 621, "comments": 156, "url": "https://producthunt.com/posts/design-kit-2", "category": "Design"},
        {"rank": 4, "name": "NoteFlow", "tagline": "下一代笔记应用", "upvotes": 587, "comments": 203, "url": "https://producthunt.com/posts/noteflow", "category": "Productivity"},
        {"rank": 5, "name": "VideoAI", "tagline": "AI 视频生成工具", "upvotes": 534, "comments": 178, "url": "https://producthunt.com/posts/videoai", "category": "AI"},
        {"rank": 6, "name": "TaskMaster", "tagline": "智能任务管理", "upvotes": 498, "comments": 145, "url": "https://producthunt.com/posts/taskmaster", "category": "Productivity"},
        {"rank": 7, "name": "ChatBot Builder", "tagline": "无代码聊天机器人构建器", "upvotes": 456, "comments": 167, "url": "https://producthunt.com/posts/chatbot-builder", "category": "AI"},
        {"rank": 8, "name": "Analytics Pro", "tagline": "数据可视化平台", "upvotes": 423, "comments": 134, "url": "https://producthunt.com/posts/analytics-pro", "category": "Analytics"},
        {"rank": 9, "name": "Email Wizard", "tagline": "AI 邮件助手", "upvotes": 389, "comments": 112, "url": "https://producthunt.com/posts/email-wizard", "category": "Productivity"},
        {"rank": 10, "name": "CloudSync", "tagline": "跨平台云同步工具", "upvotes": 356, "comments": 98, "url": "https://producthunt.com/posts/cloudsync", "category": "Developer Tools"},
    ]
    return mock_products[:limit]

def format_output(data):
    output = "🚀 Product Hunt 今日热门\n\n"
    for item in data:
        output += f"{item['rank']}. {item['name']}\n"
        output += f"   📝 {item['tagline']}\n"
        output += f"   👍 {item['upvotes']} | 💬 {item['comments']} | [{item['category']}]\n"
        output += f"   {item['url']}\n\n"
    return output

def main():
    limit = 10
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
    
    data = get_ph_top(limit=limit)
    
    if "--json" in sys.argv or "-j" in sys.argv:
        print(json.dumps({"data": data, "date": datetime.now().strftime("%Y-%m-%d")}, ensure_ascii=False, indent=2))
    else:
        print(format_output(data))

if __name__ == "__main__":
    main()
