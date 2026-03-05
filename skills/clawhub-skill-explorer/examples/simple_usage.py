#!/usr/bin/env python3
"""
ClawHub技能探索工具的简单使用示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

from clawhub_skill_explorer import ClawHubSkillExplorer

def main():
    explorer = ClawHubSkillExplorer()
    
    print("=== ClawHub技能探索工具使用示例 ===")
    print()
    
    # 获取平台统计
    print("1. 获取平台统计：")
    stats = explorer.get_statistics()
    print(f"   总技能数量: {stats['total_skills']}")
    if stats['categories']:
        print(f"   分类: {', '.join(stats['categories'])}")
    
    print()
    
    # 列出所有分类
    print("2. 列出所有分类：")
    categories = explorer.list_categories()
    for category in categories:
        print(f"   📂 {category}")
    
    print()
    
    # 搜索技能示例
    print("3. 搜索技能示例：")
    query = "search"
    results = explorer.search_skills(query, 5)
    if results:
        print(f"   🔍 搜索 '{query}' 找到 {len(results)} 个结果：")
        for skill in results:
            print(f"      🎯 {skill.name} ({skill.slug}@v{skill.version})")
    else:
        print(f"   🔍 没有找到与 '{query}' 相关的技能")
    
    print()
    
    # 浏览分类示例
    print("4. 浏览分类示例：")
    category = "all"
    results = explorer.browse_category(category, 5)
    if results:
        print(f"   📂 分类 '{category}' 的技能：")
        for skill in results:
            print(f"      🎯 {skill.name} ({skill.slug}@v{skill.version})")
    else:
        print(f"   📂 分类 '{category}' 为空")
    
    print()
    print("=== 使用完成 ===")

if __name__ == "__main__":
    main()
