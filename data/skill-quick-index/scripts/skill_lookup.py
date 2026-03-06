#!/usr/bin/env python3
"""
技能快速查询工具 - 根据关键词快速匹配可用技能（v1.0.1）
Usage: python3 skill_lookup.py "<关键词/句子>"
"""

import json
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), 'index', 'skill_index.json')


def load_index():
    try:
        with open(INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading index: {e}")
        return None


def find_matching_categories(query, index):
    """类别匹配 + 评分"""
    q = query.lower()
    results = []

    for cat_id, cat_info in index.get('categories', {}).items():
        score = 0
        matched_keywords = []

        # 名称命中加高权重
        if cat_info.get('name', '').lower() in q:
            score += 6

        for kw in cat_info.get('keywords', []):
            kl = kw.lower()
            if kl in q:
                score += 2
                matched_keywords.append(kw)

        if score > 0:
            results.append((cat_id, cat_info, score, matched_keywords))

    # 按分数降序
    results.sort(key=lambda x: x[2], reverse=True)
    return results


def find_matching_skills(query, index):
    """技能匹配 + 评分（支持多关键词加权）"""
    q = query.lower()
    results = []

    for skill_id, skill_info in index.get('skill_details', {}).items():
        score = 0
        matched_triggers = []

        # 技能ID精确命中
        if skill_id.lower() in q:
            score += 10

        # 中文名命中
        if skill_info.get('name', '').lower() in q:
            score += 8

        for t in skill_info.get('triggers', []):
            tl = t.lower()
            if tl in q:
                score += 3
                matched_triggers.append(t)

        if score > 0:
            results.append((skill_id, skill_info, score, matched_triggers))

    results.sort(key=lambda x: x[2], reverse=True)
    return results


def print_results(categories, skills, index):
    print("\n" + "=" * 64)
    print("🔍 技能快速查询结果（按相关度排序）")
    print("=" * 64)

    if skills:
        print("\n📦 推荐技能（Top 8）：")
        print("-" * 64)
        for skill_id, skill_info, score, triggers in skills[:8]:
            level = skill_info.get('level', 'Unknown')
            name = skill_info.get('name', skill_id)
            quick_ref = skill_info.get('quick_ref', '')
            print(f"  [{level}] {name}  (score={score})")
            print(f"      ID: {skill_id}")
            if triggers:
                print(f"      命中触发词: {', '.join(triggers[:6])}")
            print(f"      简介: {quick_ref}")
            print()

    if categories:
        print("\n📂 匹配类别（Top 5）：")
        print("-" * 64)
        for cat_id, cat_info, score, kws in categories[:5]:
            print(f"\n  📁 {cat_info['name']} ({cat_id})  score={score}")
            print(f"      描述: {cat_info.get('description', '')}")
            if kws:
                print(f"      命中关键词: {', '.join(kws[:8])}")
            print("      可用技能:")
            for skill in cat_info.get('skills', [])[:6]:
                detail = index.get('skill_details', {}).get(skill, {})
                print(f"        • [{detail.get('level', '?')}] {skill} - {detail.get('name', skill)}")

    if not categories and not skills:
        print("\n⚠️ 未找到匹配的技能或类别")
        print("  建议换更具体关键词：如 浏览器 / OCR / 自动化 / 团队协作")

    print("\n" + "=" * 64)


def main():
    if len(sys.argv) < 2:
        print('Usage: python3 skill_lookup.py "<关键词/句子>"')
        sys.exit(1)

    query = sys.argv[1]
    index = load_index()
    if not index:
        print("Failed to load skill index")
        sys.exit(1)

    categories = find_matching_categories(query, index)
    skills = find_matching_skills(query, index)
    print_results(categories, skills, index)


if __name__ == '__main__':
    main()
