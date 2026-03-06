#!/usr/bin/env python3
"""
少数派热门获取脚本
SSPAI Hot Articles Fetcher
"""

import json
import sys

def get_sspai_hot(limit=10):
    """获取少数派热门（模拟数据）"""
    mock_articles = [
        {"id": 1, "title": "2026 年最值得安装的 10 个 Mac 效率工具", "category": "效率工具", "views": 52000, "comments": 123},
        {"id": 2, "title": "iPhone 16 Pro 深度体验：信号终于好了", "category": "数码评测", "views": 48000, "comments": 98},
        {"id": 3, "title": "我的 Obsidian 工作流：从笔记到知识管理", "category": "效率工具", "views": 43000, "comments": 87},
        {"id": 4, "title": "2026 值得关注的 5 个 AI 写作工具", "category": "AI应用", "views": 39000, "comments": 76},
        {"id": 5, "title": "Apple Watch Ultra 3 上手体验", "category": "数码评测", "views": 35000, "comments": 65},
        {"id": 6, "title": "这些 Windows 11 隐藏功能你可能不知道", "category": "桌面软件", "views": 31000, "comments": 54},
        {"id": 7, "title": "用 Notion 打造个人任务管理系统", "category": "效率工具", "views": 27000, "comments": 48},
        {"id": 8, "title": "2026 年度最佳播客 App 推荐", "category": "手机应用", "views": 23000, "comments": 43},
        {"id": 9, "title": "智能家居入门：从零开始搭建", "category": "智能硬件", "views": 19000, "comments": 38},
        {"id": 10, "title": "摄影爱好者必备的 5 款后期 App", "category": "手机应用", "views": 15000, "comments": 32},
    ]
    return mock_articles[:limit]

def format_output(data):
    output = "⚡ 少数派今日热门\n\n"
    for item in data:
        views_w = f"{item['views'] / 10000:.1f}万"
        output += f"{item['id']}. {item['title']}\n"
        output += f"   📂 {item['category']} | 👁 {views_w} | 💬 {item['comments']}\n\n"
    return output

def main():
    limit = 10
    for arg in sys.argv[1:]:
        if arg.isdigit():
            limit = int(arg)
    
    data = get_sspai_hot(limit=limit)
    
    if "--json" in sys.argv or "-j" in sys.argv:
        print(json.dumps({"data": data}, ensure_ascii=False, indent=2))
    else:
        print(format_output(data))

if __name__ == "__main__":
    main()
