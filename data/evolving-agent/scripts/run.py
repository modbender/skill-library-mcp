#!/usr/bin/env python3
"""
Evolving Agent - Unified CLI Entry Point

统一的命令行入口，具备环境检测、路径自动解析，根据参数调用不同的脚本。

用法:
    python run.py <module> <action> [options]

模块:
    mode        进化模式控制
    knowledge   知识库操作
    github      GitHub 仓库学习
    project     项目检测和经验管理
    info        显示环境信息

示例:
    python run.py mode --status
    python run.py knowledge query --trigger "react,hooks"
    python run.py github fetch https://github.com/user/repo
    python run.py project detect .
    python run.py info
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


__version__ = "2.0.0"


# =============================================================================
# 路径解析
# =============================================================================

def get_scripts_dir() -> Path:
    """
    获取 scripts 目录路径。
    
    自动检测运行模式：
    - 开发模式: run.py 在源码的 scripts/ 目录下
    - 安装模式: run.py 在 ~/.config/opencode/skills/evolving-agent/scripts/ 下
    """
    return Path(__file__).parent


def get_skill_root() -> Path:
    """获取 evolving-agent skill 根目录"""
    return get_scripts_dir().parent


def get_script_path(module: str, script: str) -> Path:
    """
    获取目标脚本的完整路径。
    
    Args:
        module: 模块目录名 (core, knowledge, github, programming)
        script: 脚本文件名 (不含 .py 后缀)
    
    Returns:
        脚本的完整路径
    """
    return get_scripts_dir() / module / f"{script}.py"


def is_development_mode() -> bool:
    """
    检测是否在开发模式下运行。
    
    开发模式: 存在 .git 目录或 README.md 在上级目录
    安装模式: 在 ~/.config/opencode/skills/ 或 ~/.claude/skills/ 下
    """
    skill_root = get_skill_root()
    project_root = skill_root.parent
    home = Path.home()
    
    opencode_skills = home / '.config' / 'opencode' / 'skills'
    claude_skills = home / '.claude' / 'skills'
    
    # 检查是否在 skills 安装目录
    if str(skill_root).startswith(str(opencode_skills)) or \
       str(skill_root).startswith(str(claude_skills)):
        return False
    
    # 检查是否有开发标志
    if (project_root / '.git').exists() or (project_root / 'README.md').exists():
        return True
    
    return False


def detect_platform() -> str:
    """
    检测当前平台。
    
    Returns:
        'opencode' 或 'claude'
    """
    # 检查环境变量
    env_platform = os.environ.get('SKILLS_PLATFORM', '').lower()
    if env_platform in ('opencode', 'claude'):
        return env_platform
    
    # 检查哪个 skills 目录存在 evolving-agent
    home = Path.home()
    opencode_skills = home / '.config' / 'opencode' / 'skills' / 'evolving-agent'
    claude_skills = home / '.claude' / 'skills' / 'evolving-agent'
    
    if opencode_skills.exists():
        return 'opencode'
    if claude_skills.exists():
        return 'claude'
    
    # 默认 opencode
    return 'opencode'


def get_skills_dir() -> Path:
    """获取 skills 安装目录"""
    platform = detect_platform()
    home = Path.home()
    
    if platform == 'claude':
        return home / '.claude' / 'skills'
    return home / '.config' / 'opencode' / 'skills'


def get_knowledge_dir() -> Path:
    """获取知识库数据目录"""
    # 检查环境变量
    env_path = os.environ.get('KNOWLEDGE_BASE_PATH')
    if env_path:
        return Path(env_path)
    
    platform = detect_platform()
    home = Path.home()
    
    if platform == 'claude':
        return home / '.claude' / 'knowledge'
    return home / '.config' / 'opencode' / 'knowledge'


def get_python_executable() -> str:
    """
    获取 Python 解释器路径。
    
    优先使用虚拟环境中的 Python（根据平台检测），否则使用当前 Python。
    
    Returns:
        Python 解释器的完整路径
    """
    # 1. 首先检查运行目录下的 .venv（开发模式）
    skill_root = get_skill_root()
    local_venv_python = skill_root / '.venv' / 'bin' / 'python'
    
    if local_venv_python.exists() and local_venv_python.is_file():
        return str(local_venv_python)
    
    # 2. 根据平台检测安装目录的 venv
    platform = detect_platform()
    home = Path.home()
    
    if platform == 'opencode':
        installed_skill_dir = home / '.config' / 'opencode' / 'skills' / 'evolving-agent'
    else:  # claude
        installed_skill_dir = home / '.claude' / 'skills' / 'evolving-agent'
    
    installed_venv_python = installed_skill_dir / '.venv' / 'bin' / 'python'
    
    if installed_venv_python.exists() and installed_venv_python.is_file():
        return str(installed_venv_python)
    
    # 3. 使用当前 Python（作为后备）
    return sys.executable


# =============================================================================
# 环境检测
# =============================================================================

def check_python_version() -> Dict[str, Any]:
    """检查 Python 版本"""
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    is_ok = version_info >= (3, 8)
    
    return {
        "version": version_str,
        "ok": is_ok,
        "message": None if is_ok else "需要 Python 3.8+"
    }


def check_dependencies() -> Dict[str, Any]:
    """检查依赖"""
    deps = {}
    
    # 检查 PyYAML
    try:
        import yaml
        deps["PyYAML"] = {"version": yaml.__version__, "ok": True}
    except ImportError:
        deps["PyYAML"] = {"version": None, "ok": False, "message": "pip install PyYAML"}
    
    return deps


def get_evolution_mode_status() -> str:
    """获取进化模式状态"""
    marker = Path.cwd() / '.opencode' / '.evolution_mode_active'
    return "ACTIVE" if marker.exists() else "INACTIVE"


def get_environment_info() -> Dict[str, Any]:
    """获取完整的环境信息"""
    python_info = check_python_version()
    deps = check_dependencies()
    
    return {
        "version": __version__,
        "python": python_info,
        "platform": detect_platform(),
        "is_dev_mode": is_development_mode(),
        "paths": {
            "scripts_dir": str(get_scripts_dir()),
            "skill_root": str(get_skill_root()),
            "skills_dir": str(get_skills_dir()),
            "knowledge_dir": str(get_knowledge_dir()),
            "python_executable": get_python_executable(),
        },
        "dependencies": deps,
        "evolution_mode": get_evolution_mode_status(),
    }


def print_environment_info():
    """打印环境信息"""
    info = get_environment_info()
    
    print("=" * 60)
    print("Evolving Agent Environment")
    print("=" * 60)
    print()
    
    # 版本信息
    print(f"Version:         {info['version']}")
    py = info['python']
    py_status = "✓" if py['ok'] else "✗"
    print(f"Python:          {py['version']} {py_status}")
    if py.get('message'):
        print(f"                 {py['message']}")
    
    # 平台和模式
    print(f"Platform:        {info['platform']}")
    mode_str = "development (源码目录)" if info['is_dev_mode'] else "installed (安装目录)"
    print(f"Mode:            {mode_str}")
    print()
    
    # 路径
    print("Paths:")
    paths = info['paths']
    print(f"  Scripts:       {paths['scripts_dir']}")
    print(f"  Skill Root:    {paths['skill_root']}")
    print(f"  Skills Dir:    {paths['skills_dir']}")
    print(f"  Knowledge:     {paths['knowledge_dir']}")
    print(f"  Python:        {paths['python_executable']}")
    print()
    
    # 依赖
    print("Dependencies:")
    for name, dep in info['dependencies'].items():
        status = "✓" if dep['ok'] else "✗"
        version = dep.get('version') or 'not installed'
        print(f"  {name}:".ljust(15) + f"{version} {status}")
        if dep.get('message'):
            print(f"                 → {dep['message']}")
    print()
    
    # 进化模式
    print(f"Evolution Mode:  {info['evolution_mode']}")
    print()
    print("=" * 60)


# =============================================================================
# 脚本执行
# =============================================================================

def run_script(module: str, script: str, args: List[str]) -> int:
    """
    执行目标脚本。
    
    Args:
        module: 模块目录名
        script: 脚本文件名 (不含 .py)
        args: 传递给脚本的参数列表
    
    Returns:
        脚本的退出码
    """
    script_path = get_script_path(module, script)
    
    if not script_path.exists():
        print(f"Error: Script not found: {script_path}", file=sys.stderr)
        print("Please check your installation.", file=sys.stderr)
        return 1
    
    python_exe = get_python_executable()
    cmd = [python_exe, str(script_path)] + args
    
    # 设置环境变量，确保子进程能找到正确的路径
    env = os.environ.copy()
    env['PYTHONUNBUFFERED'] = '1'  # 确保 Python 输出不缓冲
    
    try:
        result = subprocess.run(cmd, env=env)
        return result.returncode
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error executing script: {e}", file=sys.stderr)
        return 1


# =============================================================================
# 命令处理器
# =============================================================================

def handle_mode(args: argparse.Namespace, remaining: List[str]) -> int:
    """处理 mode 命令"""
    script_args = []
    
    if args.status:
        script_args.append("--status")
    elif args.init:
        script_args.append("--init")
    elif args.on:
        script_args.append("--on")
    elif args.off:
        script_args.append("--off")
    else:
        # 默认显示状态
        script_args.append("--status")
    
    return run_script("core", "toggle_mode", script_args)


def handle_knowledge(args: argparse.Namespace, remaining: List[str]) -> int:
    """处理 knowledge 命令"""
    action = args.action
    
    mapping = {
        "query": ("knowledge", "query"),
        "store": ("knowledge", "store"),
        "summarize": ("knowledge", "summarizer"),
        "trigger": ("knowledge", "trigger"),
    }
    
    if action in mapping:
        mod, script = mapping[action]
        return run_script(mod, script, remaining)
    
    print(f"Unknown action: {action}", file=sys.stderr)
    print("Available actions: query, store, summarize, trigger", file=sys.stderr)
    return 1


def handle_github(args: argparse.Namespace, remaining: List[str]) -> int:
    """处理 github 命令"""
    action = args.action
    
    mapping = {
        "fetch": ("github", "fetch_info"),
        "extract": ("github", "extract_patterns"),
        "store": ("github", "store_to_knowledge"),
    }
    
    if action in mapping:
        mod, script = mapping[action]
        return run_script(mod, script, remaining)
    
    print(f"Unknown action: {action}", file=sys.stderr)
    print("Available actions: fetch, extract, store", file=sys.stderr)
    return 1


def handle_project(args: argparse.Namespace, remaining: List[str]) -> int:
    """处理 project 命令"""
    action = args.action
    
    mapping = {
        "detect": ("programming", "detect_project"),
        "store": ("programming", "store_experience"),
        "query": ("programming", "query_experience"),
    }
    
    if action in mapping:
        mod, script = mapping[action]
        return run_script(mod, script, remaining)
    
    print(f"Unknown action: {action}", file=sys.stderr)
    print("Available actions: detect, store, query", file=sys.stderr)
    return 1


def handle_info(args: argparse.Namespace, remaining: List[str]) -> int:
    """处理 info 命令"""
    if args.json:
        info = get_environment_info()
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print_environment_info()
    return 0


# =============================================================================
# 参数解析
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """创建参数解析器"""
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Evolving Agent - 统一命令行入口",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py mode --status              查看进化模式状态
  python run.py mode --init                初始化进化模式
  python run.py knowledge query --stats    查看知识库统计
  python run.py github fetch <url>         获取 GitHub 仓库信息
  python run.py project detect .           检测当前项目技术栈
  python run.py info                       显示环境信息
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="module", help="可用模块")
    
    # -------------------------------------------------------------------------
    # mode 子命令
    # -------------------------------------------------------------------------
    mode_parser = subparsers.add_parser(
        "mode",
        help="进化模式控制",
        description="控制进化模式的开启、关闭和状态查看"
    )
    mode_group = mode_parser.add_mutually_exclusive_group()
    mode_group.add_argument("--status", action="store_true", help="查看状态")
    mode_group.add_argument("--init", action="store_true", help="完整初始化")
    mode_group.add_argument("--on", action="store_true", help="开启进化模式")
    mode_group.add_argument("--off", action="store_true", help="关闭进化模式")
    
    # -------------------------------------------------------------------------
    # knowledge 子命令
    # -------------------------------------------------------------------------
    knowledge_parser = subparsers.add_parser(
        "knowledge",
        help="知识库操作",
        description="知识库的查询、存储、归纳和触发"
    )
    knowledge_parser.add_argument(
        "action",
        choices=["query", "store", "summarize", "trigger"],
        help="操作: query(查询), store(存储), summarize(归纳), trigger(触发)"
    )
    
    # -------------------------------------------------------------------------
    # github 子命令
    # -------------------------------------------------------------------------
    github_parser = subparsers.add_parser(
        "github",
        help="GitHub 仓库学习",
        description="从 GitHub 仓库提取和存储知识"
    )
    github_parser.add_argument(
        "action",
        choices=["fetch", "extract", "store"],
        help="操作: fetch(获取信息), extract(提取模式), store(存储知识)"
    )
    
    # -------------------------------------------------------------------------
    # project 子命令
    # -------------------------------------------------------------------------
    project_parser = subparsers.add_parser(
        "project",
        help="项目检测和经验管理",
        description="检测项目技术栈，管理项目经验"
    )
    project_parser.add_argument(
        "action",
        choices=["detect", "store", "query"],
        help="操作: detect(检测技术栈), store(存储经验), query(查询经验)"
    )
    
    # -------------------------------------------------------------------------
    # info 子命令
    # -------------------------------------------------------------------------
    info_parser = subparsers.add_parser(
        "info",
        help="显示环境信息",
        description="显示运行环境、路径和依赖信息"
    )
    info_parser.add_argument(
        "--json",
        action="store_true",
        help="以 JSON 格式输出"
    )
    
    return parser


# =============================================================================
# 主入口
# =============================================================================

def main() -> int:
    """主入口函数"""
    parser = create_parser()
    
    # 使用 parse_known_args 来捕获剩余参数传递给子脚本
    args, remaining = parser.parse_known_args()
    
    if args.module is None:
        parser.print_help()
        return 0
    
    # 分发到对应的处理器
    handlers = {
        "mode": handle_mode,
        "knowledge": handle_knowledge,
        "github": handle_github,
        "project": handle_project,
        "info": handle_info,
    }
    
    handler = handlers.get(args.module)
    if handler:
        return handler(args, remaining)
    else:
        print(f"Unknown module: {args.module}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
