#!/usr/bin/env python3
"""
Unified Knowledge Store

统一知识库存储接口，支持所有分类：
- experience: 经验积累
- tech-stack: 技术栈积累
- scenario: 场景积累
- problem: 问题积累
- testing: 测试积累
- pattern: 编程范式
- skill: 编程技能
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# 路径解析器导入标志
_path_resolver_module = None

def _try_import_path_resolver():
    """尝试导入 path_resolver 模块"""
    global _path_resolver_module
    if _path_resolver_module is not None:
        return _path_resolver_module
    
    # 添加 path_resolver 所在目录到 Python path
    script_dir = Path(__file__).parent
    core_scripts = script_dir.parent / 'core'
    if core_scripts.exists() and str(core_scripts) not in sys.path:
        sys.path.insert(0, str(core_scripts))
    
    # 尝试导入
    try:
        import path_resolver
        _path_resolver_module = path_resolver
        return path_resolver
    except ImportError:
        _path_resolver_module = False  # type: ignore
        return None


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

VALID_CATEGORIES = list(CATEGORY_DIRS.keys())


def get_kb_root() -> Path:
    """
    Get knowledge base root directory.
    
    使用统一的 path_resolver 模块进行跨平台路径解析。
    支持 OpenCode (~/.config/opencode/skills/) 和 Claude Code (~/.claude/skills/)。
    
    优先级：
    1. 使用 path_resolver 模块（推荐）
    2. 环境变量 KNOWLEDGE_BASE_PATH（如果设置）
    3. 自动检测已存在的知识库目录
    4. 创建默认目录
    """
    # 1. 优先使用 path_resolver
    resolver = _try_import_path_resolver()
    if resolver:
        return resolver.get_knowledge_base_dir()
    
    # 2. Fallback: 内置路径解析逻辑
    # 检查环境变量
    env_path = os.environ.get('KNOWLEDGE_BASE_PATH')
    if env_path:
        kb_path = Path(env_path)
        if kb_path.exists():
            return kb_path
    
    # 检查 OpenCode 知识库位置
    opencode_kb = Path.home() / '.config' / 'opencode' / 'knowledge'
    if opencode_kb.exists():
        return opencode_kb
    
    # 检查 Claude Code 知识库位置
    claude_kb = Path.home() / '.claude' / 'knowledge'
    if claude_kb.exists():
        return claude_kb
    
    # 如果都不存在，创建 OpenCode 默认位置
    opencode_kb.mkdir(parents=True, exist_ok=True)
    return opencode_kb


def generate_id(category: str, name: str) -> str:
    """Generate unique ID for knowledge entry."""
    hash_input = f"{category}:{name}:{datetime.now().isoformat()}"
    hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    name_slug = name.lower().replace(' ', '-').replace('/', '-')[:30]
    return f"{category}-{name_slug}-{hash_suffix}"


def load_json(path: Path) -> Dict[str, Any]:
    """Safely load JSON file."""
    if not path.exists():
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_json(path: Path, data: Dict[str, Any]) -> None:
    """Save JSON file with pretty formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def extract_triggers(name: str, content: Dict[str, Any], tags: Optional[List[str]] = None) -> List[str]:
    """
    自动从知识内容中提取触发关键字。
    
    提取规则：
    1. 名称分词
    2. 相关技术栈
    3. 显式标签
    4. 内容中的关键术语
    """
    triggers: set = set()
    
    # 从名称提取
    name_parts = name.lower().replace('-', ' ').replace('_', ' ').split()
    triggers.update(name_parts)
    
    # 从标签提取
    if tags:
        triggers.update(t.lower() for t in tags)
    
    # 从内容中提取相关技术
    related_tech = content.get('related_tech', [])
    triggers.update(t.lower() for t in related_tech)
    
    # 技术栈名称
    if 'tech_name' in content:
        triggers.add(content['tech_name'].lower())
    
    # 框架名称
    if 'framework' in content:
        triggers.add(content['framework'].lower())
    
    # 问题症状关键字
    if 'symptoms' in content:
        for symptom in content['symptoms']:
            # 提取简短关键字
            words = symptom.lower().split()[:3]
            triggers.update(words)
    
    # 过滤太短或太通用的词
    stop_words = {'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'and', 'or', 'but', 'not', 'as', 'if', 'when', 'than'}
    triggers = {t for t in triggers if len(t) > 2 and t not in stop_words}
    
    return sorted(list(triggers))


def update_global_index(kb_root: Path, entry_id: str, category: str, triggers: List[str]) -> None:
    """Update the global index with new entry and trigger mappings."""
    index_path = kb_root / 'index.json'
    index = load_json(index_path)
    
    # Ensure structure
    if 'trigger_index' not in index:
        index['trigger_index'] = {}
    if 'category_index' not in index:
        index['category_index'] = {d: [] for d in CATEGORY_DIRS.values()}
    if 'stats' not in index:
        index['stats'] = {'total_entries': 0, 'by_category': {}}
    
    # Update trigger index
    for trigger in triggers:
        if trigger not in index['trigger_index']:
            index['trigger_index'][trigger] = []
        if entry_id not in index['trigger_index'][trigger]:
            index['trigger_index'][trigger].append(entry_id)
    
    # Update category index
    cat_dir = CATEGORY_DIRS.get(category, category)
    if cat_dir not in index['category_index']:
        index['category_index'][cat_dir] = []
    if entry_id not in index['category_index'][cat_dir]:
        index['category_index'][cat_dir].append(entry_id)
    
    # Update stats
    index['stats']['total_entries'] = sum(
        len(entries) for entries in index['category_index'].values()
    )
    index['stats']['by_category'] = {
        cat: len(entries) for cat, entries in index['category_index'].items()
    }
    
    # Update recent entries (keep last 20)
    if 'recent_entries' not in index:
        index['recent_entries'] = []
    index['recent_entries'].insert(0, entry_id)
    index['recent_entries'] = index['recent_entries'][:20]
    
    index['last_updated'] = datetime.now().isoformat()
    save_json(index_path, index)


def update_category_index(kb_root: Path, category: str, entry_id: str, name: str) -> None:
    """Update the category-specific index."""
    cat_dir = CATEGORY_DIRS.get(category, category)
    index_path = kb_root / cat_dir / 'index.json'
    index = load_json(index_path)
    
    if 'entries' not in index:
        index['entries'] = []
    
    # Check if entry already exists
    existing = next((e for e in index['entries'] if e.get('id') == entry_id), None)
    if existing:
        existing['name'] = name
        existing['updated_at'] = datetime.now().isoformat()
    else:
        index['entries'].append({
            'id': entry_id,
            'name': name,
            'created_at': datetime.now().isoformat()
        })
    
    index['last_updated'] = datetime.now().isoformat()
    save_json(index_path, index)


def store_knowledge(
    category: str,
    name: str,
    content: Dict[str, Any],
    sources: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    triggers: Optional[List[str]] = None,
    entry_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    存储知识条目到统一知识库。
    
    Args:
        category: 知识分类 (experience, tech-stack, scenario, problem, testing, pattern, skill)
        name: 知识条目名称
        content: 知识内容 (符合对应分类的 schema)
        sources: 来源列表 (GitHub URL, 会话 ID 等)
        tags: 额外标签
        triggers: 显式指定的触发关键字 (可选，会自动提取)
        entry_id: 已有条目ID (用于更新)
    
    Returns:
        创建/更新的知识条目
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Must be one of: {VALID_CATEGORIES}")
    
    kb_root = get_kb_root()
    cat_dir = CATEGORY_DIRS[category]
    
    # Generate or use existing ID
    if not entry_id:
        entry_id = generate_id(category, name)
    
    # Auto-extract triggers if not provided
    if triggers is None:
        triggers = extract_triggers(name, content, tags)
    else:
        # Merge auto-extracted with explicit triggers
        auto_triggers = extract_triggers(name, content, tags)
        triggers = list(set(triggers + auto_triggers))
    
    # Build entry
    now = datetime.now().isoformat()
    entry_path = kb_root / cat_dir / f"{entry_id}.json"
    
    # Load existing entry if updating
    existing = load_json(entry_path) if entry_path.exists() else {}
    
    entry: Dict[str, Any] = {
        'id': entry_id,
        'category': category,
        'name': name,
        'triggers': triggers,
        'content': content,
        'sources': sources or existing.get('sources', []),
        'tags': tags or existing.get('tags', []),
        'created_at': existing.get('created_at', now),
        'updated_at': now,
        'usage_count': existing.get('usage_count', 0),
        'effectiveness': existing.get('effectiveness', 0.5)
    }
    
    # Merge sources if updating
    if existing.get('sources'):
        all_sources = list(set(existing['sources'] + (sources or [])))
        entry['sources'] = all_sources
    
    # Save entry
    save_json(entry_path, entry)
    
    # Update indexes
    update_category_index(kb_root, category, entry_id, name)
    update_global_index(kb_root, entry_id, category, triggers)
    
    return entry


def store_experience(
    name: str,
    description: str,
    solution: str,
    context: Optional[str] = None,
    pitfalls: Optional[List[str]] = None,
    related_tech: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储经验类知识。"""
    content = {
        'description': description,
        'context': context or '',
        'solution': solution,
        'pitfalls': pitfalls or [],
        'related_tech': related_tech or []
    }
    return store_knowledge('experience', name, content, sources, tags)


def store_tech_stack(
    tech_name: str,
    best_practices: Optional[List[str]] = None,
    conventions: Optional[List[str]] = None,
    common_patterns: Optional[List[str]] = None,
    gotchas: Optional[List[str]] = None,
    version: Optional[str] = None,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储技术栈知识。"""
    content = {
        'tech_name': tech_name,
        'version': version or '',
        'best_practices': best_practices or [],
        'conventions': conventions or [],
        'common_patterns': common_patterns or [],
        'gotchas': gotchas or []
    }
    return store_knowledge('tech-stack', tech_name, content, sources, [tech_name.lower()])


def store_scenario(
    scenario_name: str,
    description: str,
    typical_approach: str,
    steps: Optional[List[str]] = None,
    considerations: Optional[List[str]] = None,
    related_tech: Optional[List[str]] = None,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储场景知识。"""
    content = {
        'scenario_name': scenario_name,
        'description': description,
        'typical_approach': typical_approach,
        'steps': steps or [],
        'considerations': considerations or [],
        'related_tech': related_tech or []
    }
    return store_knowledge('scenario', scenario_name, content, sources)


def store_problem(
    problem_name: str,
    symptoms: List[str],
    root_causes: List[str],
    solutions: List[Dict[str, str]],
    prevention: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储问题知识。"""
    content = {
        'problem_name': problem_name,
        'symptoms': symptoms,
        'root_causes': root_causes,
        'solutions': solutions,
        'prevention': prevention or []
    }
    return store_knowledge('problem', problem_name, content, sources, tags)


def store_testing(
    name: str,
    testing_type: str,
    framework: Optional[str] = None,
    best_practices: Optional[List[str]] = None,
    patterns: Optional[List[str]] = None,
    anti_patterns: Optional[List[str]] = None,
    example_structure: Optional[str] = None,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储测试知识。"""
    content = {
        'testing_type': testing_type,
        'framework': framework or '',
        'best_practices': best_practices or [],
        'patterns': patterns or [],
        'anti_patterns': anti_patterns or [],
        'example_structure': example_structure or ''
    }
    tags = [testing_type, 'testing']
    if framework:
        tags.append(framework.lower())
    return store_knowledge('testing', name, content, sources, tags)


def store_pattern(
    pattern_name: str,
    pattern_category: str,
    description: str,
    when_to_use: str,
    structure: Optional[str] = None,
    example: Optional[str] = None,
    pros: Optional[List[str]] = None,
    cons: Optional[List[str]] = None,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储编程范式。"""
    content = {
        'pattern_name': pattern_name,
        'category': pattern_category,
        'description': description,
        'when_to_use': when_to_use,
        'structure': structure or '',
        'example': example or '',
        'pros': pros or [],
        'cons': cons or []
    }
    return store_knowledge('pattern', pattern_name, content, sources, [pattern_category])


def store_skill(
    skill_name: str,
    level: str,
    description: str,
    key_concepts: Optional[List[str]] = None,
    practical_tips: Optional[List[str]] = None,
    common_mistakes: Optional[List[str]] = None,
    sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """便捷方法：存储编程技能。"""
    content = {
        'skill_name': skill_name,
        'level': level,
        'description': description,
        'key_concepts': key_concepts or [],
        'practical_tips': practical_tips or [],
        'common_mistakes': common_mistakes or []
    }
    return store_knowledge('skill', skill_name, content, sources, [level])


def main():
    parser = argparse.ArgumentParser(
        description='Store knowledge to unified knowledge base',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Store from JSON input
  echo '{"name": "CORS Issue", "content": {...}}' | python knowledge_store.py --category problem
  
  # Store with explicit parameters
  python knowledge_store.py --category tech-stack --name "React" --content '{"best_practices": [...]}'
  
  # Import from stdin
  python knowledge_store.py --from-json --source "https://github.com/..."
        """
    )
    
    parser.add_argument('--category', '-c', choices=VALID_CATEGORIES,
                        help='Knowledge category')
    parser.add_argument('--name', '-n', help='Knowledge entry name')
    parser.add_argument('--content', help='JSON content string')
    parser.add_argument('--source', '-s', help='Source URL or identifier')
    parser.add_argument('--tags', '-t', help='Comma-separated tags')
    parser.add_argument('--from-json', action='store_true',
                        help='Read full entry from stdin as JSON')
    
    args = parser.parse_args()
    
    if args.from_json:
        # Read from stdin
        try:
            data = json.load(sys.stdin)
            entry = store_knowledge(
                category=data.get('category', 'experience'),
                name=data.get('name', 'Unnamed'),
                content=data.get('content', {}),
                sources=[args.source] if args.source else data.get('sources'),
                tags=data.get('tags'),
                triggers=data.get('triggers')
            )
            print(json.dumps(entry, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.category and args.name:
        content = json.loads(args.content) if args.content else {}
        sources = [args.source] if args.source else None
        tags = args.tags.split(',') if args.tags else None
        
        entry = store_knowledge(
            category=args.category,
            name=args.name,
            content=content,
            sources=sources,
            tags=tags
        )
        print(json.dumps(entry, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
