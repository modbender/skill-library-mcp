#!/usr/bin/env python3
"""
Path Resolver - 统一路径解析模块

为 Evolving Programming Agent 提供跨平台的路径解析能力。
支持 OpenCode、Claude Code、Cursor 等多个平台。

使用方式：
    from path_resolver import get_skills_dir, get_venv_python, get_knowledge_base_dir

平台支持：
    - OpenCode: ~/.config/opencode/skills/
    - Claude Code / Cursor: ~/.claude/skills/
"""

import os
import sys
from pathlib import Path
from typing import Optional


# 平台配置
PLATFORM_CONFIGS = {
    'opencode': {
        'skills_dir': Path.home() / '.config' / 'opencode' / 'skills',
        'priority': 1,  # 优先级越小越优先
    },
    'claude': {
        'skills_dir': Path.home() / '.claude' / 'skills',
        'priority': 2,
    },
}

# 共享 venv 所在的 skill 名称
VENV_SKILL = 'evolving-agent'

# 知识数据目录配置 (独立于 skills 目录)
KNOWLEDGE_DIRS = {
    'opencode': Path.home() / '.config' / 'opencode' / 'knowledge',
    'claude': Path.home() / '.claude' / 'knowledge',
}


def detect_platform() -> str:
    """
    自动检测当前运行的平台。
    
    检测逻辑：
    1. 检查环境变量 SKILLS_PLATFORM (显式指定)
    2. 检查哪个 skills 目录存在且包含 evolving-agent
    3. 如果都存在，优先选择 OpenCode
    
    Returns:
        平台名称: 'opencode' 或 'claude'
    """
    # 1. 检查环境变量
    env_platform = os.environ.get('SKILLS_PLATFORM', '').lower()
    if env_platform in PLATFORM_CONFIGS:
        return env_platform
    
    # 2. 检查哪个目录存在 evolving-agent
    platforms_found = []
    for name, config in PLATFORM_CONFIGS.items():
        venv_dir = config['skills_dir'] / VENV_SKILL / '.venv'
        if venv_dir.exists():
            platforms_found.append((name, config['priority']))
    
    # 按优先级排序
    if platforms_found:
        platforms_found.sort(key=lambda x: x[1])
        return platforms_found[0][0]
    
    # 3. 如果都不存在，检查哪个 skills 目录存在
    for name, config in sorted(PLATFORM_CONFIGS.items(), key=lambda x: x[1]['priority']):
        if config['skills_dir'].exists():
            return name
    
    # 4. 默认返回 opencode
    return 'opencode'


def get_skills_dir(platform: Optional[str] = None) -> Path:
    """
    获取 skills 基础目录。
    
    优先级：
    1. 环境变量 SKILLS_BASE_DIR (显式覆盖)
    2. 根据平台自动检测
    
    Args:
        platform: 可选，指定平台名称 ('opencode' 或 'claude')
    
    Returns:
        skills 目录路径
    """
    # 1. 检查环境变量覆盖
    env_dir = os.environ.get('SKILLS_BASE_DIR')
    if env_dir:
        return Path(env_dir)
    
    # 2. 根据平台获取
    if platform is None:
        platform = detect_platform()
    
    if platform not in PLATFORM_CONFIGS:
        raise ValueError(f"Unknown platform: {platform}. Must be one of: {list(PLATFORM_CONFIGS.keys())}")
    
    return PLATFORM_CONFIGS[platform]['skills_dir']


def get_venv_python(platform: Optional[str] = None) -> Path:
    """
    获取共享 venv 的 Python 解释器路径。
    
    Args:
        platform: 可选，指定平台名称
    
    Returns:
        Python 解释器路径
    """
    skills_dir = get_skills_dir(platform)
    return skills_dir / VENV_SKILL / '.venv' / 'bin' / 'python'


def get_knowledge_base_dir(platform: Optional[str] = None) -> Path:
    """
    获取知识库目录。
    
    知识数据存储在独立目录，与 skills 代码分离：
    - OpenCode: ~/.config/opencode/knowledge/
    - Claude: ~/.claude/knowledge/
    
    优先级：
    1. 环境变量 KNOWLEDGE_BASE_PATH (显式覆盖)
    2. 已存在的知识库目录（优先 OpenCode）
    3. 根据平台自动确定
    
    Args:
        platform: 可选，指定平台名称
    
    Returns:
        知识库目录路径
    """
    # 1. 检查环境变量覆盖
    env_path = os.environ.get('KNOWLEDGE_BASE_PATH')
    if env_path:
        kb_path = Path(env_path)
        if kb_path.exists():
            return kb_path
    
    # 2. 检查哪个平台有知识库
    for name, config in sorted(PLATFORM_CONFIGS.items(), key=lambda x: x[1]['priority']):
        kb_dir = KNOWLEDGE_DIRS.get(name)
        if kb_dir and kb_dir.exists():
            return kb_dir
    
    # 3. 根据平台确定（如果不存在则创建）
    if platform:
        kb_dir = KNOWLEDGE_DIRS.get(platform)
    else:
        detected = detect_platform()
        kb_dir = KNOWLEDGE_DIRS.get(detected)
    
    if kb_dir:
        kb_dir.mkdir(parents=True, exist_ok=True)
        return kb_dir
    
    # Fallback to opencode
    fallback_dir = KNOWLEDGE_DIRS['opencode']
    fallback_dir.mkdir(parents=True, exist_ok=True)
    return fallback_dir


def get_script_path(skill_name: str, script_name: str, platform: Optional[str] = None) -> Path:
    """
    获取指定脚本的完整路径。
    
    Args:
        skill_name: skill 名称 (如 'evolving-agent', 'knowledge-base')
        script_name: 脚本名称 (如 'toggle_mode.py', 'knowledge_query.py')
        platform: 可选，指定平台名称
    
    Returns:
        脚本完整路径
    """
    skills_dir = get_skills_dir(platform)
    return skills_dir / skill_name / 'scripts' / script_name


def get_run_command(skill_name: str, script_name: str, *args, platform: Optional[str] = None) -> str:
    """
    获取运行脚本的完整命令。
    
    Args:
        skill_name: skill 名称
        script_name: 脚本名称
        *args: 传递给脚本的参数
        platform: 可选，指定平台名称
    
    Returns:
        完整的运行命令字符串
    """
    python_path = get_venv_python(platform)
    script_path = get_script_path(skill_name, script_name, platform)
    
    cmd_parts = [str(python_path), str(script_path)]
    cmd_parts.extend(str(arg) for arg in args)
    
    return ' '.join(cmd_parts)


def print_paths(platform: Optional[str] = None):
    """打印所有关键路径信息，用于调试。"""
    if platform is None:
        platform = detect_platform()
    
    print(f"Platform: {platform}")
    print(f"Skills Directory: {get_skills_dir(platform)}")
    print(f"Venv Python: {get_venv_python(platform)}")
    print(f"Knowledge Base: {get_knowledge_base_dir(platform)}")
    print()
    print("Script paths:")
    print(f"  toggle_mode.py: {get_script_path('evolving-agent', 'toggle_mode.py', platform)}")
    print(f"  knowledge_query.py: {get_script_path('knowledge-base', 'knowledge_query.py', platform)}")


# 便捷函数：用于其他脚本直接导入
def get_kb_root() -> Path:
    """
    兼容旧接口：获取知识库根目录。
    
    这个函数提供与原有 knowledge_store.py 中 get_kb_root() 相同的接口。
    """
    return get_knowledge_base_dir()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Path Resolver - 路径解析工具')
    parser.add_argument('--platform', '-p', choices=['opencode', 'claude'],
                        help='指定平台')
    parser.add_argument('--skills-dir', action='store_true',
                        help='输出 skills 目录')
    parser.add_argument('--venv-python', action='store_true',
                        help='输出 venv Python 路径')
    parser.add_argument('--knowledge-base', action='store_true',
                        help='输出知识库目录')
    parser.add_argument('--script', nargs=2, metavar=('SKILL', 'SCRIPT'),
                        help='输出指定脚本路径')
    parser.add_argument('--run-cmd', nargs='+', metavar='ARG',
                        help='输出运行命令 (格式: SKILL SCRIPT [ARGS...])')
    parser.add_argument('--all', '-a', action='store_true',
                        help='输出所有路径信息')
    
    args = parser.parse_args()
    
    if args.all:
        print_paths(args.platform)
    elif args.skills_dir:
        print(get_skills_dir(args.platform))
    elif args.venv_python:
        print(get_venv_python(args.platform))
    elif args.knowledge_base:
        print(get_knowledge_base_dir(args.platform))
    elif args.script:
        print(get_script_path(args.script[0], args.script[1], args.platform))
    elif args.run_cmd and len(args.run_cmd) >= 2:
        skill, script = args.run_cmd[0], args.run_cmd[1]
        extra_args = args.run_cmd[2:] if len(args.run_cmd) > 2 else []
        print(get_run_command(skill, script, *extra_args, platform=args.platform))
    else:
        # 默认输出检测到的平台
        print(f"Detected platform: {detect_platform()}")
        print(f"Skills directory: {get_skills_dir()}")
