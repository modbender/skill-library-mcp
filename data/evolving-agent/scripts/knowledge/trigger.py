#!/usr/bin/env python3
"""
Knowledge Trigger Detector

知识触发检测器 - 根据用户输入和项目上下文自动检测并加载相关知识。

触发方式：
1. 项目检测 (package.json, go.mod, pom.xml 等)
2. 用户输入关键字匹配
3. 场景推断 (根据动词和上下文)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Import query functions
from query import (
    get_kb_root, load_json, get_global_index,
    query_by_triggers, query_by_category, get_entry
)


# 场景关键字映射
SCENARIO_KEYWORDS = {
    'api': ['api', 'rest', 'restful', 'graphql', 'endpoint', '接口', '请求'],
    'auth': ['auth', 'login', 'logout', '登录', '认证', '授权', 'jwt', 'oauth', 'session'],
    'database': ['database', 'db', 'sql', 'query', '数据库', 'mysql', 'postgres', 'mongodb', 'redis'],
    'testing': ['test', 'testing', 'unit', 'e2e', 'integration', '测试', 'jest', 'pytest', 'vitest'],
    'deploy': ['deploy', 'deployment', 'ci', 'cd', 'docker', 'k8s', '部署', '上线'],
    'performance': ['performance', 'optimize', 'slow', 'fast', '性能', '优化', '慢'],
    'security': ['security', 'secure', 'xss', 'csrf', 'injection', '安全', '漏洞'],
    'state': ['state', 'store', 'redux', 'vuex', 'zustand', '状态管理'],
    'form': ['form', 'validation', 'input', '表单', '校验'],
    'routing': ['route', 'router', 'navigation', '路由', '导航'],
    'error': ['error', 'bug', 'fix', 'debug', '错误', '报错', 'issue', '问题']
}

# 问题症状关键字
PROBLEM_SYMPTOMS = {
    'cors': ['cors', '跨域', 'cross-origin', 'access-control'],
    'memory': ['memory', 'leak', '内存', '泄露', 'oom'],
    'timeout': ['timeout', '超时', 'hang', '卡住'],
    'crash': ['crash', '崩溃', '闪退'],
    'import': ['import', 'module', 'cannot find', '找不到模块', 'not found'],
    'type': ['type', 'typescript', '类型错误', 'type error'],
    'null': ['null', 'undefined', 'cannot read', 'is not defined'],
    'async': ['async', 'await', 'promise', 'callback', '异步']
}

# 动作关键字映射到场景
ACTION_TO_SCENARIO = {
    'create': 'scenario', 'build': 'scenario', 'implement': 'scenario', 'add': 'scenario',
    '创建': 'scenario', '实现': 'scenario', '开发': 'scenario', '新增': 'scenario',
    'fix': 'problem', 'debug': 'problem', 'solve': 'problem', 'resolve': 'problem',
    '修复': 'problem', '解决': 'problem', '排查': 'problem',
    'optimize': 'experience', 'improve': 'experience', 'refactor': 'experience',
    '优化': 'experience', '重构': 'experience',
    'test': 'testing', 'mock': 'testing', '测试': 'testing', '验证': 'testing'
}


def extract_keywords(text: str) -> List[str]:
    """从文本中提取关键字。"""
    keywords: Set[str] = set()
    
    # 英文单词 (3+ 字符)
    english_words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9\-\.]+\b', text.lower())
    keywords.update(w for w in english_words if len(w) >= 3)
    
    # 中文词组 (2-4字)
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
    keywords.update(chinese_words)
    
    # 技术术语 (如 react-query, vue.js)
    tech_terms = re.findall(r'[a-zA-Z]+[\-\.][a-zA-Z]+', text.lower())
    keywords.update(tech_terms)
    
    return list(keywords)


def detect_scenarios(text: str) -> List[str]:
    """检测文本中涉及的场景。"""
    text_lower = text.lower()
    detected: Set[str] = set()
    
    for scenario, keywords in SCENARIO_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                detected.add(scenario)
                break
    
    return list(detected)


def detect_problems(text: str) -> List[str]:
    """检测文本中描述的问题类型。"""
    text_lower = text.lower()
    detected: Set[str] = set()
    
    for problem, symptoms in PROBLEM_SYMPTOMS.items():
        for symptom in symptoms:
            if symptom in text_lower:
                detected.add(problem)
                break
    
    return list(detected)


def detect_action_type(text: str) -> Optional[str]:
    """检测用户意图的动作类型。"""
    text_lower = text.lower()
    
    for action, category in ACTION_TO_SCENARIO.items():
        if action in text_lower:
            return category
    
    return None


def detect_project_tech(project_dir: str) -> Dict[str, Any]:
    """检测项目技术栈。"""
    detector_path = Path(__file__).parent.parent / 'programming'
    sys.path.insert(0, str(detector_path))
    
    try:
        from detect_project import detect_project
        return detect_project(project_dir)
    except ImportError:
        return {'error': 'Project detector not available'}


def trigger_knowledge(
    user_input: Optional[str] = None,
    project_dir: Optional[str] = None,
    explicit_triggers: Optional[List[str]] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    主触发函数 - 根据输入检测并加载相关知识。
    
    Args:
        user_input: 用户输入的文本
        project_dir: 项目目录路径
        explicit_triggers: 显式指定的触发关键字
        limit: 每类知识返回的条目数限制
    
    Returns:
        检测结果和匹配的知识
    """
    result: Dict[str, Any] = {
        'detected': {
            'keywords': [],
            'scenarios': [],
            'problems': [],
            'tech_stack': None,
            'action_type': None
        },
        'knowledge': {
            'high_relevance': [],
            'medium_relevance': [],
            'by_category': {}
        },
        'triggers_used': []
    }
    
    all_triggers: Set[str] = set()
    
    # 1. 处理显式触发关键字
    if explicit_triggers:
        all_triggers.update(explicit_triggers)
    
    # 2. 从用户输入提取
    if user_input:
        keywords = extract_keywords(user_input)
        result['detected']['keywords'] = keywords
        all_triggers.update(keywords)
        
        scenarios = detect_scenarios(user_input)
        result['detected']['scenarios'] = scenarios
        all_triggers.update(scenarios)
        
        problems = detect_problems(user_input)
        result['detected']['problems'] = problems
        all_triggers.update(problems)
        
        action_type = detect_action_type(user_input)
        result['detected']['action_type'] = action_type
    
    # 3. 从项目检测
    if project_dir:
        tech_detection = detect_project_tech(project_dir)
        if 'error' not in tech_detection:
            result['detected']['tech_stack'] = tech_detection
            all_triggers.update(tech_detection.get('base_tech', []))
            all_triggers.update(tech_detection.get('frameworks', []))
            all_triggers.update(tech_detection.get('tools', []))
    
    result['triggers_used'] = sorted(list(all_triggers))
    
    # 4. 查询知识库
    if all_triggers:
        matched = query_by_triggers(list(all_triggers), limit=limit * 2)
        
        high_threshold = 3
        for entry in matched:
            match_score = entry.get('_match_score', 0)
            if match_score >= high_threshold:
                result['knowledge']['high_relevance'].append(entry)
            else:
                result['knowledge']['medium_relevance'].append(entry)
        
        result['knowledge']['high_relevance'] = result['knowledge']['high_relevance'][:limit]
        result['knowledge']['medium_relevance'] = result['knowledge']['medium_relevance'][:limit]
    
    # 5. 根据检测到的场景/问题补充查询
    if result['detected']['scenarios']:
        for scenario in result['detected']['scenarios'][:2]:
            entries = query_by_category('scenario', limit=2)
            if entries:
                result['knowledge']['by_category'][f'scenario:{scenario}'] = entries
    
    if result['detected']['problems']:
        for problem in result['detected']['problems'][:2]:
            entries = query_by_category('problem', limit=2)
            if entries:
                result['knowledge']['by_category'][f'problem:{problem}'] = entries
    
    return result


def format_for_context(knowledge_result: Dict[str, Any]) -> str:
    """将知识结果格式化为可嵌入上下文的简洁格式。"""
    lines: List[str] = []
    
    high_rel = knowledge_result.get('knowledge', {}).get('high_relevance', [])
    if high_rel:
        lines.append("## 相关知识")
        for entry in high_rel[:3]:
            name = entry.get('name', 'Unknown')
            category = entry.get('category', '')
            content = entry.get('content', {})
            
            lines.append(f"\n### [{category}] {name}")
            
            if 'solution' in content:
                lines.append(f"**解决方案**: {content['solution'][:200]}")
            if 'best_practices' in content:
                practices = content['best_practices'][:3]
                lines.append("**最佳实践**:")
                for p in practices:
                    lines.append(f"- {p}")
            if 'symptoms' in content:
                symptoms = content['symptoms'][:2]
                lines.append(f"**症状**: {'; '.join(symptoms)}")
            if 'typical_approach' in content:
                lines.append(f"**典型方法**: {content['typical_approach'][:150]}")
    
    med_rel = knowledge_result.get('knowledge', {}).get('medium_relevance', [])
    if med_rel and len(lines) < 30:
        lines.append("\n## 可能相关")
        for entry in med_rel[:2]:
            name = entry.get('name', 'Unknown')
            category = entry.get('category', '')
            lines.append(f"- [{category}] {name}")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Detect and trigger relevant knowledge based on input',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python knowledge_trigger.py --input "帮我修复这个 CORS 跨域问题"
  python knowledge_trigger.py --project /path/to/react-app
  python knowledge_trigger.py --input "如何优化 API 性能" --project .
  python knowledge_trigger.py --trigger react,hooks,performance
  python knowledge_trigger.py --input "..." --format context
        """
    )
    
    parser.add_argument('--input', '-i', help='User input text')
    parser.add_argument('--project', '-p', help='Project directory path')
    parser.add_argument('--trigger', '-t', help='Comma-separated explicit triggers')
    parser.add_argument('--limit', '-l', type=int, default=5, help='Result limit')
    parser.add_argument('--format', '-f', choices=['json', 'context', 'triggers'],
                        default='json', help='Output format')
    
    args = parser.parse_args()
    
    if not any([args.input, args.project, args.trigger]):
        parser.print_help()
        sys.exit(1)
    
    explicit_triggers = None
    if args.trigger:
        explicit_triggers = [t.strip() for t in args.trigger.split(',')]
    
    result = trigger_knowledge(
        user_input=args.input,
        project_dir=args.project,
        explicit_triggers=explicit_triggers,
        limit=args.limit
    )
    
    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    elif args.format == 'context':
        print(format_for_context(result))
    elif args.format == 'triggers':
        print(','.join(result.get('triggers_used', [])))


if __name__ == '__main__':
    main()
