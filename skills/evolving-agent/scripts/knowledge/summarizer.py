#!/usr/bin/env python3
"""
Knowledge Summarizer

知识归纳总结器 - 分析会话内容，自动提取、分类并存储知识。

功能：
1. 从会话记录中提取有价值的知识
2. 自动分类到正确的 category (experience, problem, scenario, etc.)
3. 生成触发关键字
4. 合并相似知识条目
5. 更新知识有效性评分
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from store import (
    store_experience, store_tech_stack, store_scenario,
    store_problem, store_testing, store_pattern, store_skill,
    store_knowledge, get_kb_root, load_json, save_json,
    CATEGORY_DIRS
)
from query import query_by_triggers, search_content


# 知识提取模式
EXTRACTION_PATTERNS = {
    # 问题-解决方案模式
    'problem_solution': [
        r'问题[：:]\s*(.+?)[\n。].*?解决[：:方案]\s*(.+?)[\n。]',
        r'遇到.+?(错误|问题|bug).+?通过(.+?)解决',
        r'(error|issue|bug).+?fixed by (.+)',
        r'修复了(.+?)(?:，|,)(.+)',
    ],
    
    # 最佳实践模式
    'best_practice': [
        r'最佳实践[：:]\s*(.+?)(?:[\n。]|$)',
        r'建议[：:]\s*(.+?)(?:[\n。]|$)',
        r'(?:应该|推荐|最好)(.+?)(?:，|,|。|\n|$)',
        r'best practice[：:]\s*(.+?)(?:[\n.]|$)',
    ],
    
    # 注意事项模式
    'gotcha': [
        r'注意[：:]\s*(.+?)(?:[\n。]|$)',
        r'(?:需要|要)注意(.+?)(?:，|。|\n|$)',
        r'(?:坑|陷阱)[：:]\s*(.+?)(?:[\n。]|$)',
        r'gotcha[：:]\s*(.+?)(?:[\n.]|$)',
        r'(?:don\'t|avoid|不要)(.+?)(?:，|。|\n|$)',
    ],
    
    # 用户反馈/偏好模式 - 使用贪婪匹配捕获完整内容
    'user_feedback': [
        r'(?:记住|保存|重要)[：:]\s*(.+)',
        r'(以后.+)',
        r'((?:总是|一直|统一)(?:使用|用).+)',
        r'(.+(?:项目|工程)(?:都|一直|统一)(?:使用|用).+)',
    ]
}

# 分类推断关键字
CATEGORY_INDICATORS = {
    'experience': ['经验', '教训', '学到', 'learned', '发现'],
    'problem': ['问题', '错误', 'error', 'bug', 'issue', '报错', '失败'],
    'scenario': ['场景', '需求', '实现', 'implement', 'create', '开发'],
    'testing': ['测试', 'test', 'mock', 'jest', 'pytest', '单元测试', 'e2e'],
    'pattern': ['模式', 'pattern', '架构', 'architecture', '设计'],
    'tech-stack': ['框架', 'framework', '库', 'library', '工具', 'tool'],
    'skill': ['技巧', '方法', 'technique', 'skill', '技能']
}


def extract_knowledge_from_text(text: str) -> List[Dict[str, Any]]:
    """
    从文本中提取知识条目。
    
    Args:
        text: 会话文本或代码注释
    
    Returns:
        提取的知识条目列表
    """
    extracted: List[Dict[str, Any]] = []
    text = text.strip()
    
    # 问题-解决方案
    for pattern in EXTRACTION_PATTERNS['problem_solution']:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if isinstance(match, tuple) and len(match) >= 2:
                problem, solution = match[0].strip(), match[1].strip()
                if len(problem) > 5 and len(solution) > 5:
                    extracted.append({
                        'type': 'problem',
                        'name': problem[:50],
                        'content': {
                            'problem_name': problem,
                            'symptoms': [problem],
                            'root_causes': [],
                            'solutions': [{'description': solution}],
                            'prevention': []
                        }
                    })
    
    # 最佳实践
    for pattern in EXTRACTION_PATTERNS['best_practice']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            practice = match.strip() if isinstance(match, str) else match[0].strip()
            if len(practice) > 10:
                extracted.append({
                    'type': 'experience',
                    'name': f"最佳实践: {practice[:30]}",
                    'content': {
                        'description': practice,
                        'context': '',
                        'solution': practice,
                        'pitfalls': [],
                        'related_tech': []
                    }
                })
    
    # 注意事项 (gotchas)
    for pattern in EXTRACTION_PATTERNS['gotcha']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            gotcha = match.strip() if isinstance(match, str) else match[0].strip()
            if len(gotcha) > 5:
                extracted.append({
                    'type': 'experience',
                    'name': f"注意: {gotcha[:30]}",
                    'content': {
                        'description': gotcha,
                        'context': '需要特别注意',
                        'solution': '',
                        'pitfalls': [gotcha],
                        'related_tech': []
                    }
                })
    
    # 用户偏好/反馈 - 使用 set 去重
    seen_preferences: Set[str] = set()
    for pattern in EXTRACTION_PATTERNS['user_feedback']:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                # 多组捕获，合并为完整内容
                preference = ' '.join(m.strip() for m in match if m.strip())
            else:
                preference = match.strip()
            
            # 去重：使用小写和去除空格的版本作为 key
            preference_key = preference.lower().replace(' ', '')
            if len(preference) > 5 and preference_key not in seen_preferences:
                seen_preferences.add(preference_key)
                extracted.append({
                    'type': 'experience',
                    'name': f"偏好: {preference[:40]}",
                    'content': {
                        'description': preference,
                        'context': '用户偏好设置',
                        'solution': preference,
                        'pitfalls': [],
                        'related_tech': []
                    }
                })
    
    # 如果没有匹配到任何模式，但输入足够短且有意义，作为通用经验存储
    if not extracted and 5 < len(text) < 200:
        # 简短输入，直接作为经验存储
        extracted.append({
            'type': 'experience',
            'name': f"经验: {text[:40]}",
            'content': {
                'description': text,
                'context': '用户记录的经验',
                'solution': text,
                'pitfalls': [],
                'related_tech': []
            }
        })
    
    return extracted


def infer_category(text: str, default: str = 'experience') -> str:
    """
    根据文本内容推断知识分类。
    
    Args:
        text: 知识内容文本
        default: 默认分类
    
    Returns:
        推断的分类
    """
    text_lower = text.lower()
    scores: Dict[str, int] = {cat: 0 for cat in CATEGORY_INDICATORS}
    
    for category, indicators in CATEGORY_INDICATORS.items():
        for indicator in indicators:
            if indicator in text_lower:
                scores[category] += 1
    
    # 返回得分最高的分类
    max_score = max(scores.values())
    if max_score > 0:
        for cat, score in scores.items():
            if score == max_score:
                return cat
    
    return default


def extract_tech_stack(text: str) -> List[str]:
    """从文本中提取技术栈关键字。"""
    # 常见技术栈列表
    tech_keywords = [
        'react', 'vue', 'angular', 'svelte', 'next', 'nuxt',
        'express', 'fastify', 'nest', 'koa',
        'django', 'flask', 'fastapi',
        'spring', 'springboot', 'quarkus',
        'gin', 'fiber', 'echo',
        'typescript', 'javascript', 'python', 'java', 'go', 'rust',
        'mysql', 'postgres', 'mongodb', 'redis',
        'docker', 'kubernetes', 'k8s',
        'jest', 'vitest', 'pytest', 'junit',
        'webpack', 'vite', 'rollup',
        'graphql', 'rest', 'grpc'
    ]
    
    text_lower = text.lower()
    found: Set[str] = set()
    
    for tech in tech_keywords:
        if tech in text_lower:
            found.add(tech)
    
    return list(found)


def find_similar_entries(name: str, content: Dict[str, Any], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    查找相似的知识条目，用于去重和合并。
    
    Args:
        name: 知识名称
        content: 知识内容
        threshold: 相似度阈值
    
    Returns:
        相似条目列表
    """
    # 使用名称关键字搜索
    keywords = name.lower().split()[:3]
    similar: List[Dict[str, Any]] = []
    
    for kw in keywords:
        if len(kw) > 3:
            results = search_content(kw, limit=5)
            similar.extend(results)
    
    # 去重
    seen_ids: Set[str] = set()
    unique: List[Dict[str, Any]] = []
    for entry in similar:
        entry_id = entry.get('id', '')
        if entry_id and entry_id not in seen_ids:
            seen_ids.add(entry_id)
            unique.append(entry)
    
    return unique


def summarize_session(
    session_content: str,
    session_id: Optional[str] = None,
    auto_store: bool = False
) -> Dict[str, Any]:
    """
    分析会话内容，提取并归纳知识。
    
    Args:
        session_content: 会话内容文本
        session_id: 会话ID (作为来源标识)
        auto_store: 是否自动存储到知识库
    
    Returns:
        {
            'extracted': [...],      # 提取的知识条目
            'categorized': {...},    # 按分类整理
            'tech_stack': [...],     # 检测到的技术栈
            'stored': [...]          # 已存储的条目ID (如果 auto_store=True)
        }
    """
    result: Dict[str, Any] = {
        'extracted': [],
        'categorized': {cat: [] for cat in CATEGORY_DIRS.keys()},
        'tech_stack': [],
        'stored': [],
        'similar_found': []
    }
    
    # 1. 提取知识
    extracted = extract_knowledge_from_text(session_content)
    result['extracted'] = extracted
    
    # 2. 检测技术栈
    tech_stack = extract_tech_stack(session_content)
    result['tech_stack'] = tech_stack
    
    # 3. 分类知识
    for entry in extracted:
        entry_type = entry.get('type', 'experience')
        content_text = json.dumps(entry.get('content', {}), ensure_ascii=False)
        
        # 推断更精确的分类
        inferred_cat = infer_category(content_text, entry_type)
        entry['inferred_category'] = inferred_cat
        
        # 添加技术栈标签
        entry['related_tech'] = tech_stack
        
        result['categorized'][inferred_cat].append(entry)
    
    # 4. 查找相似条目
    for entry in extracted:
        similar = find_similar_entries(entry.get('name', ''), entry.get('content', {}))
        if similar:
            result['similar_found'].append({
                'entry': entry.get('name'),
                'similar': [s.get('name') for s in similar[:3]]
            })
    
    # 5. 自动存储
    if auto_store:
        sources = [session_id] if session_id else []
        
        for entry in extracted:
            category = entry.get('inferred_category', 'experience')
            name = entry.get('name', 'Unknown')
            content = entry.get('content', {})
            
            # 添加技术栈到内容
            if 'related_tech' not in content:
                content['related_tech'] = tech_stack
            
            try:
                stored = store_knowledge(
                    category=category,
                    name=name,
                    content=content,
                    sources=sources,
                    tags=tech_stack
                )
                result['stored'].append(stored.get('id'))
            except Exception as e:
                result['stored'].append(f"Error: {str(e)}")
    
    return result


def update_effectiveness(entry_id: str, positive: bool = True) -> bool:
    """
    根据反馈更新知识有效性评分。
    
    Args:
        entry_id: 知识条目ID
        positive: 是否为正面反馈
    
    Returns:
        是否更新成功
    """
    kb_root = get_kb_root()
    
    # 找到条目文件
    for cat_dir in CATEGORY_DIRS.values():
        entry_path = kb_root / cat_dir / f"{entry_id}.json"
        if entry_path.exists():
            entry = load_json(entry_path)
            
            # 更新使用次数
            entry['usage_count'] = entry.get('usage_count', 0) + 1
            
            # 更新有效性评分 (滑动平均)
            current = entry.get('effectiveness', 0.5)
            delta = 0.1 if positive else -0.1
            new_score = max(0, min(1, current + delta))
            entry['effectiveness'] = new_score
            entry['updated_at'] = datetime.now().isoformat()
            
            save_json(entry_path, entry)
            return True
    
    return False


def main():
    parser = argparse.ArgumentParser(
        description='Summarize and extract knowledge from session content',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze session from stdin
  cat session.txt | python knowledge_summarizer.py --session-id "session-123"
  
  # Analyze and auto-store
  cat session.txt | python knowledge_summarizer.py --auto-store
  
  # Update effectiveness
  python knowledge_summarizer.py --feedback positive --entry-id "problem-cors-abc123"
        """
    )
    
    parser.add_argument('--session-id', help='Session identifier for source tracking')
    parser.add_argument('--auto-store', action='store_true', help='Automatically store extracted knowledge')
    parser.add_argument('--feedback', choices=['positive', 'negative'], 
                        help='Update entry effectiveness')
    parser.add_argument('--entry-id', help='Entry ID for feedback update')
    parser.add_argument('--format', '-f', choices=['json', 'summary'], default='json',
                        help='Output format')
    
    args = parser.parse_args()
    
    if args.feedback and args.entry_id:
        success = update_effectiveness(args.entry_id, args.feedback == 'positive')
        print(json.dumps({'success': success, 'entry_id': args.entry_id}))
        return
    
    # Read session content from stdin
    session_content = sys.stdin.read()
    
    if not session_content.strip():
        print("Error: No session content provided via stdin", file=sys.stderr)
        sys.exit(1)
    
    result = summarize_session(
        session_content=session_content,
        session_id=args.session_id,
        auto_store=args.auto_store
    )
    
    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.format == 'summary':
        print(f"提取的知识条目: {len(result['extracted'])}")
        print(f"检测到的技术栈: {', '.join(result['tech_stack']) or 'None'}")
        print("\n按分类:")
        for cat, entries in result['categorized'].items():
            if entries:
                print(f"  {cat}: {len(entries)}")
        if result['stored']:
            print(f"\n已存储: {len(result['stored'])} 条")
        if result['similar_found']:
            print(f"\n发现相似条目: {len(result['similar_found'])} 组")


if __name__ == '__main__':
    main()
