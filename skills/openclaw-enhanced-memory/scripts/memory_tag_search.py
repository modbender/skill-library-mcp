#!/usr/bin/env python3
"""
记忆标签检索工具 (Memory Tag Search)
用法：
  python3 memory_tag_search.py "人物:刘辉"                    # 按单标签搜索
  python3 memory_tag_search.py "人物:王隆哲" "类型:开票信息"    # 多标签 AND 搜索
  python3 memory_tag_search.py --list-tags                     # 列出所有标签
  python3 memory_tag_search.py --list-tags --category 人物     # 列出某分类下的标签
"""

import os
import re
import sys
from collections import defaultdict

MEMORY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory")
TAG_PATTERN = re.compile(r'\[([^:\[\]]+):([^:\[\]]+)\]')


def scan_files():
    """递归扫描 memory/ 下所有 .md 文件，返回 (filepath, lineno, line, tags) 列表"""
    results = []
    for root, _, files in os.walk(MEMORY_DIR):
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    for lineno, line in enumerate(f, 1):
                        tags = TAG_PATTERN.findall(line)
                        if tags:
                            results.append((fpath, lineno, line.rstrip('\n'), tags))
            except (OSError, UnicodeDecodeError):
                continue
    return results


def search_tags(query_tags):
    """按标签搜索，query_tags 是 [(分类, 值), ...] 列表，AND 逻辑"""
    results = scan_files()
    matched = []
    for fpath, lineno, line, tags in results:
        tag_set = set(tags)
        if all(qt in tag_set for qt in query_tags):
            matched.append((fpath, lineno, line))
    return matched


def list_all_tags(category_filter=None):
    """列出所有标签及出现次数"""
    results = scan_files()
    tag_count = defaultdict(int)
    for _, _, _, tags in results:
        for tag in tags:
            if category_filter and tag[0] != category_filter:
                continue
            tag_count[tag] += 1
    return sorted(tag_count.items(), key=lambda x: (-x[1], x[0][0], x[0][1]))


def rel_path(fpath):
    """返回相对于工作目录的路径"""
    try:
        return os.path.relpath(fpath)
    except ValueError:
        return fpath


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__.strip())
        sys.exit(0)

    # --list-tags 模式
    if '--list-tags' in args:
        cat_filter = None
        if '--category' in args:
            idx = args.index('--category')
            if idx + 1 < len(args):
                cat_filter = args[idx + 1]
        tags = list_all_tags(cat_filter)
        if not tags:
            print("未找到任何标签。")
            sys.exit(0)
        print(f"共找到 {len(tags)} 个标签：\n")
        current_cat = None
        for (cat, val), count in tags:
            if cat != current_cat:
                if current_cat is not None:
                    print()
                print(f"【{cat}】")
                current_cat = cat
            print(f"  [{cat}:{val}]  ×{count}")
        sys.exit(0)

    # 搜索模式：解析查询标签
    query_tags = []
    for arg in args:
        # 支持 "人物:刘辉" 或 "[人物:刘辉]" 两种写法
        clean = arg.strip('[]')
        if ':' in clean:
            cat, val = clean.split(':', 1)
            query_tags.append((cat, val))
        else:
            print(f"无效标签格式: {arg}（应为 分类:值）")
            sys.exit(1)

    matched = search_tags(query_tags)

    if not matched:
        tag_str = ' AND '.join(f'[{c}:{v}]' for c, v in query_tags)
        print(f"未找到匹配 {tag_str} 的记录。")
        sys.exit(0)

    tag_str = ' AND '.join(f'[{c}:{v}]' for c, v in query_tags)
    print(f"搜索 {tag_str}，找到 {len(matched)} 条结果：\n")
    for fpath, lineno, line in matched:
        print(f"  {rel_path(fpath)}:{lineno}")
        print(f"    {line}\n")


if __name__ == '__main__':
    main()
