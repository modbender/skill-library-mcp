#!/usr/bin/env python3
"""
Unified Knowledge Query

统一知识库查询接口：
- 按关键字触发查询
- 按分类查询
- 按标签查询
- 全文搜索
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# Category to directory mapping
CATEGORY_DIRS = {
    'experience': 'experiences',
    'tech-stack': 'tech-stacks',
    'scenario': 'scenarios',
    'problem': 'problems',
    'testing': 'testing',
    'pattern': 'patterns',
    'skill': 'skills'
}


# 路径解析器导入
_path_resolver_module = None

def _try_import_path_resolver():
    """尝试导入 path_resolver 模块"""
    global _path_resolver_module
    if _path_resolver_module is not None:
        return _path_resolver_module if _path_resolver_module else None
    
    # 添加 path_resolver 所在目录到 Python path
    script_dir = Path(__file__).parent
    core_scripts = script_dir.parent / 'core'
    if core_scripts.exists() and str(core_scripts) not in sys.path:
        sys.path.insert(0, str(core_scripts))
    
    try:
        import path_resolver
        _path_resolver_module = path_resolver
        return path_resolver
    except ImportError:
        _path_resolver_module = False  # type: ignore
        return None


def get_kb_root() -> Path:
    """
    Get knowledge base root directory.
    
    使用统一的 path_resolver 模块进行跨平台路径解析。
    支持 OpenCode (~/.config/opencode/skills/) 和 Claude Code (~/.claude/skills/)。
    """
    # 1. 优先使用 path_resolver
    resolver = _try_import_path_resolver()
    if resolver:
        return resolver.get_knowledge_base_dir()
    
    # 2. Fallback: 内置路径解析逻辑
    env_path = os.environ.get('KNOWLEDGE_BASE_PATH')
    if env_path:
        kb_path = Path(env_path)
        if kb_path.exists():
            return kb_path
    
    opencode_kb = Path.home() / '.config' / 'opencode' / 'knowledge'
    if opencode_kb.exists():
        return opencode_kb
    
    claude_kb = Path.home() / '.claude' / 'knowledge'
    if claude_kb.exists():
        return claude_kb
    
    opencode_kb.mkdir(parents=True, exist_ok=True)
    return opencode_kb


def load_json(path: Path) -> Dict[str, Any]:
    """Safely load JSON file."""
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def get_global_index() -> Dict[str, Any]:
    """Load global index."""
    return load_json(get_kb_root() / 'index.json')


def query_by_triggers(triggers: List[str], limit: int = 10) -> List[Dict[str, Any]]:
    """
    根据触发关键字查询知识。
    
    Args:
        triggers: 触发关键字列表
        limit: 返回结果数量限制
    
    Returns:
        匹配的知识条目列表，按匹配度排序
    """
    kb_root = get_kb_root()
    index = get_global_index()
    trigger_index = index.get('trigger_index', {})
    
    # Count matches per entry
    entry_matches: Dict[str, int] = {}
    matched_entry_ids: Set[str] = set()
    
    for trigger in triggers:
        trigger_lower = trigger.lower()
        # Exact match
        if trigger_lower in trigger_index:
            for entry_id in trigger_index[trigger_lower]:
                entry_matches[entry_id] = entry_matches.get(entry_id, 0) + 2  # Higher weight for exact
                matched_entry_ids.add(entry_id)
        
        # Partial match
        for indexed_trigger, entry_ids in trigger_index.items():
            if trigger_lower in indexed_trigger or indexed_trigger in trigger_lower:
                for entry_id in entry_ids:
                    entry_matches[entry_id] = entry_matches.get(entry_id, 0) + 1
                    matched_entry_ids.add(entry_id)
    
    if not matched_entry_ids:
        return []
    
    # Sort by match count
    sorted_entries = sorted(entry_matches.items(), key=lambda x: x[1], reverse=True)
    
    # Load entry details
    results: List[Dict[str, Any]] = []
    for entry_id, match_count in sorted_entries[:limit]:
        # Determine category from entry_id
        category = entry_id.split('-')[0] if '-' in entry_id else 'experience'
        cat_dir = CATEGORY_DIRS.get(category, 'experiences')
        
        entry_path = kb_root / cat_dir / f"{entry_id}.json"
        if entry_path.exists():
            entry = load_json(entry_path)
            entry['_match_score'] = match_count
            results.append(entry)
    
    return results


def query_by_category(category: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    按分类查询所有知识条目。
    
    Args:
        category: 知识分类
        limit: 返回数量限制
    
    Returns:
        该分类下的知识条目列表
    """
    kb_root = get_kb_root()
    cat_dir = CATEGORY_DIRS.get(category)
    if not cat_dir:
        return []
    
    cat_path = kb_root / cat_dir
    if not cat_path.exists():
        return []
    
    results: List[Dict[str, Any]] = []
    for entry_file in cat_path.glob('*.json'):
        if entry_file.name == 'index.json':
            continue
        entry = load_json(entry_file)
        if entry:
            results.append(entry)
        if len(results) >= limit:
            break
    
    # Sort by effectiveness and usage
    results.sort(key=lambda x: (x.get('effectiveness', 0), x.get('usage_count', 0)), reverse=True)
    return results


def query_by_tags(tags: List[str], limit: int = 10) -> List[Dict[str, Any]]:
    """
    按标签查询知识。
    
    Args:
        tags: 标签列表
        limit: 返回数量限制
    
    Returns:
        匹配标签的知识条目列表
    """
    kb_root = get_kb_root()
    tags_lower = [t.lower() for t in tags]
    results: List[Dict[str, Any]] = []
    
    # Search all categories
    for cat_dir in CATEGORY_DIRS.values():
        cat_path = kb_root / cat_dir
        if not cat_path.exists():
            continue
        
        for entry_file in cat_path.glob('*.json'):
            if entry_file.name == 'index.json':
                continue
            entry = load_json(entry_file)
            if not entry:
                continue
            
            entry_tags = [t.lower() for t in entry.get('tags', [])]
            if any(tag in entry_tags for tag in tags_lower):
                results.append(entry)
                if len(results) >= limit:
                    break
        
        if len(results) >= limit:
            break
    
    return results


def search_content(keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    全文搜索知识内容。
    
    Args:
        keyword: 搜索关键字
        limit: 返回数量限制
    
    Returns:
        包含关键字的知识条目列表
    """
    kb_root = get_kb_root()
    keyword_lower = keyword.lower()
    results: List[Dict[str, Any]] = []
    
    # Search all categories
    for cat_dir in CATEGORY_DIRS.values():
        cat_path = kb_root / cat_dir
        if not cat_path.exists():
            continue
        
        for entry_file in cat_path.glob('*.json'):
            if entry_file.name == 'index.json':
                continue
            
            # Read raw content for search
            try:
                content_str = entry_file.read_text(encoding='utf-8').lower()
                if keyword_lower in content_str:
                    entry = load_json(entry_file)
                    if entry:
                        results.append(entry)
                        if len(results) >= limit:
                            break
            except IOError:
                continue
        
        if len(results) >= limit:
            break
    
    return results


def get_entry(entry_id: str) -> Optional[Dict[str, Any]]:
    """
    获取单个知识条目。
    
    Args:
        entry_id: 知识条目ID
    
    Returns:
        知识条目，如不存在则返回 None
    """
    kb_root = get_kb_root()
    
    # Try to determine category from ID
    parts = entry_id.split('-')
    if parts:
        category = parts[0]
        cat_dir = CATEGORY_DIRS.get(category)
        if cat_dir:
            entry_path = kb_root / cat_dir / f"{entry_id}.json"
            if entry_path.exists():
                return load_json(entry_path)
    
    # Fallback: search all categories
    for cat_dir in CATEGORY_DIRS.values():
        entry_path = kb_root / cat_dir / f"{entry_id}.json"
        if entry_path.exists():
            return load_json(entry_path)
    
    return None


def get_stats() -> Dict[str, Any]:
    """获取知识库统计信息。"""
    index = get_global_index()
    return {
        'version': index.get('version', 'unknown'),
        'last_updated': index.get('last_updated'),
        'stats': index.get('stats', {}),
        'trigger_count': len(index.get('trigger_index', {})),
        'recent_entries': index.get('recent_entries', [])[:5]
    }


def format_output(data: Any, fmt: str = 'json') -> str:
    """Format output based on type."""
    if fmt == 'json':
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif fmt == 'markdown':
        if isinstance(data, list):
            lines = []
            for entry in data:
                lines.append(f"### {entry.get('name', 'Unknown')}")
                lines.append(f"- **Category**: {entry.get('category', 'N/A')}")
                lines.append(f"- **Triggers**: {', '.join(entry.get('triggers', [])[:5])}")
                content = entry.get('content', {})
                if 'description' in content:
                    lines.append(f"- **Description**: {content['description'][:100]}...")
                lines.append("")
            return '\n'.join(lines)
        elif isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    lines.append(f"**{key}**: {json.dumps(value, ensure_ascii=False)}")
                else:
                    lines.append(f"**{key}**: {value}")
            return '\n'.join(lines)
    return str(data)


def main():
    parser = argparse.ArgumentParser(
        description='Query unified knowledge base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query by triggers (most common)
  python knowledge_query.py --trigger react,hooks,state
  
  # Query by category
  python knowledge_query.py --category problem
  
  # Search content
  python knowledge_query.py --search "跨域"
  
  # Get single entry
  python knowledge_query.py --id problem-cors-abc123
  
  # Get stats
  python knowledge_query.py --stats
        """
    )
    
    parser.add_argument('--trigger', '-t', help='Comma-separated trigger keywords')
    parser.add_argument('--category', '-c', choices=list(CATEGORY_DIRS.keys()),
                        help='Query by category')
    parser.add_argument('--tags', help='Comma-separated tags')
    parser.add_argument('--search', '-s', help='Full-text search keyword')
    parser.add_argument('--id', help='Get entry by ID')
    parser.add_argument('--stats', action='store_true', help='Show knowledge base stats')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Result limit')
    parser.add_argument('--format', '-f', choices=['json', 'markdown'], default='json',
                        help='Output format')
    
    args = parser.parse_args()
    
    if args.stats:
        result = get_stats()
    elif args.id:
        result = get_entry(args.id)
        if not result:
            print(f"Entry not found: {args.id}", file=sys.stderr)
            sys.exit(1)
    elif args.trigger:
        triggers = [t.strip() for t in args.trigger.split(',')]
        result = query_by_triggers(triggers, args.limit)
    elif args.category:
        result = query_by_category(args.category, args.limit)
    elif args.tags:
        tags = [t.strip() for t in args.tags.split(',')]
        result = query_by_tags(tags, args.limit)
    elif args.search:
        result = search_content(args.search, args.limit)
    else:
        # Default: show stats
        result = get_stats()
    
    print(format_output(result, args.format))


if __name__ == '__main__':
    main()
