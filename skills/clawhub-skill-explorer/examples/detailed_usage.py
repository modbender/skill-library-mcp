#!/usr/bin/env python3
"""
ClawHub技能探索工具的详细使用示例
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))

from clawhub_skill_explorer import ClawHubSkillExplorer

def print_skill_details(skill):
    """打印技能详细信息"""
    print(f"技能名称: {skill.name}")
    print(f"技能slug: {skill.slug}")
    print(f"版本: v{skill.version}")
    print(f"描述: {skill.description}")
    print(f"作者: {skill.author}")
    print(f"分类: {skill.category}")
    if skill.tags:
        print(f"标签: {', '.join(skill.tags)}")
    print(f"得分: {skill.score:.2f}")
    print()

def main():
    # 创建技能探索器实例
    explorer = ClawHubSkillExplorer()
    
    print("=== ClawHub技能探索工具 - 详细使用示例 ===")
    print()
    
    try:
        # 获取平台统计信息
        print("1. 获取平台统计信息")
        print("-" * 50)
        stats = explorer.get_statistics()
        
        print(f"总技能数量: {stats['total_skills']}")
        if stats['categories']:
            print(f"技能分类: {', '.join(stats['categories'])}")
        
        if stats.get('versions'):
            print("版本分布:")
            for version_range, count in stats['versions'].items():
                print(f"  {version_range}: {count} 个技能")
        
        print()
        
        # 列出所有技能分类
        print("2. 列出所有技能分类")
        print("-" * 50)
        
        categories = explorer.list_categories()
        for category in categories:
            print(f"📂 {category}")
        
        print()
        
        # 搜索技能
        print("3. 搜索技能示例")
        print("-" * 50)
        
        search_queries = ["search", "productivity", "development", "automation"]
        
        for query in search_queries:
            print(f"  🔍 搜索: '{query}'")
            results = explorer.search_skills(query, 3)
            
            if results:
                for skill in results:
                    print(f"    🎯 {skill.name} ({skill.slug}@v{skill.version})")
            else:
                print(f"    ❌ 没有找到相关技能")
            print()
        
        # 浏览分类
        print("4. 浏览分类示例")
        print("-" * 50)
        
        categories_to_browse = ["general", "productivity"]
        
        for category in categories_to_browse:
            print(f"  📂 分类: '{category}'")
            results = explorer.browse_category(category, 4)
            
            if results:
                for skill in results:
                    print(f"    🎯 {skill.name} ({skill.slug}@v{skill.version})")
            else:
                print(f"    ❌ 分类 '{category}' 为空")
            print()
        
        # 获取推荐技能
        print("5. 获取推荐技能")
        print("-" * 50)
        
        recommendations = explorer.get_recommendations(3)
        for skill in recommendations:
            print(f"  🎯 {skill.name} ({skill.slug}@v{skill.version})")
            print(f"     {skill.description}")
            print()
        
        print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        print(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"程序错误: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)
