#!/usr/bin/env python3
"""
Evolution Mode Toggle Script

Controls the persistent evolution mode state for a session.
The marker file is created in the CURRENT WORKING DIRECTORY,
allowing multiple projects to have independent evolution mode states.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def get_workspace_root() -> Path:
    """
    Get the current working directory as workspace root.
    
    This ensures each project directory has its own evolution mode state,
    supporting parallel development across multiple projects.
    
    Returns:
        Path: The current working directory
    """
    return Path.cwd()


def get_mode_marker_path() -> Path:
    """
    Get the path to the evolution mode marker file.
    
    The marker file is always created in the current working directory's
    .opencode subdirectory, ensuring project-level isolation.
    
    Returns:
        Path: Path to .evolution_mode_active file
    """
    root = get_workspace_root()
    return root / '.opencode' / '.evolution_mode_active'


def check_write_permission(path: Path) -> bool:
    """
    Check if we have write permission for the given path.
    
    Args:
        path: The path to check
        
    Returns:
        bool: True if writable, False otherwise
    """
    # Check the path itself or its parent
    check_path = path if path.exists() else path.parent
    if not check_path.exists():
        # Check parent of parent
        check_path = path.parent.parent
        if not check_path.exists():
            check_path = Path.cwd()
    
    return os.access(check_path, os.W_OK)


def run_with_sudo(command: list[str]) -> tuple[bool, str]:
    """
    Run a command with sudo after user confirmation.
    
    Args:
        command: The command to run
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Ask for user confirmation
        print(f"需要管理员权限来写入文件")
        response = input("是否使用 sudo 继续? [y/N]: ").strip().lower()
        
        if response not in ('y', 'yes'):
            return False, "用户取消操作"
        
        # Run with sudo
        result = subprocess.run(
            ['sudo'] + command,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True, "操作成功"
        else:
            return False, f"命令执行失败: {result.stderr}"
            
    except KeyboardInterrupt:
        return False, "用户取消操作"
    except Exception as e:
        return False, f"执行出错: {e}"


def enable_mode() -> str:
    """
    Enable evolution mode by creating the marker file.
    Handles permission issues with sudo if needed.
    
    Returns:
        str: Success message
    """
    marker_path = get_mode_marker_path()
    parent_dir = marker_path.parent
    
    # Try to create directory and file normally first
    try:
        parent_dir.mkdir(parents=True, exist_ok=True)
        marker_path.touch()
        return f"✓ Evolution Mode ENABLED for this session\n  Marker: {marker_path}"
    except PermissionError:
        pass
    
    # Permission denied - try with sudo
    print(f"无法写入 {marker_path}")
    
    # Create directory with sudo if needed
    if not parent_dir.exists():
        success, msg = run_with_sudo(['mkdir', '-p', str(parent_dir)])
        if not success:
            return f"✗ 无法创建目录: {msg}"
    
    # Create marker file with sudo
    success, msg = run_with_sudo(['touch', str(marker_path)])
    if success:
        return f"✓ Evolution Mode ENABLED for this session (with sudo)\n  Marker: {marker_path}"
    else:
        return f"✗ 无法启用进化模式: {msg}"


def disable_mode() -> str:
    """
    Disable evolution mode by removing the marker file.
    Handles permission issues with sudo if needed.
    
    Returns:
        str: Success message
    """
    marker_path = get_mode_marker_path()
    
    if not marker_path.exists():
        return "ℹ Evolution Mode was not active"
    
    # Try to remove normally first
    try:
        marker_path.unlink()
        return f"✓ Evolution Mode DISABLED for this session"
    except PermissionError:
        pass
    
    # Permission denied - try with sudo
    print(f"无法删除 {marker_path}")
    success, msg = run_with_sudo(['rm', '-f', str(marker_path)])
    
    if success:
        return f"✓ Evolution Mode DISABLED for this session (with sudo)"
    else:
        return f"✗ 无法禁用进化模式: {msg}"


def is_mode_active() -> bool:
    """
    Check if evolution mode is currently active.
    
    Returns:
        bool: True if mode is active
    """
    return get_mode_marker_path().exists()


def get_status_message() -> str:
    """
    Get the current status message.
    
    Returns:
        str: Status message
    """
    status = "ACTIVE" if is_mode_active() else "INACTIVE"
    marker_path = get_mode_marker_path()
    return f"Evolution Mode Status: {status}\nMarker file: {marker_path}"


def get_context_prompt() -> str:
    """
    Get the context prompt that should be injected into the AI's context.
    
    Returns:
        str: The reinforcement prompt
    """
    if not is_mode_active():
        return ""
    
    return """
## Evolution Mode Active
This session is in EVOLUTION MODE.
- After completing tasks, automatically check for extractable knowledge
- Run trigger detection even without explicit user commands
- Store valuable experiences to the knowledge base
- Only report to user when new knowledge is extracted
""".strip()


def main():
    parser = argparse.ArgumentParser(
        description='Toggle or check evolution mode status',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python toggle_mode.py                    # Show current status
  python toggle_mode.py --init            # Full init: start coordinator + enable mode
  python toggle_mode.py --on              # Enable evolution mode
  python toggle_mode.py --off              # Disable evolution mode
  python toggle_mode.py --on --inject      # Enable and print context prompt
  python toggle_mode.py --status           # Show detailed status
        """
    )

    parser.add_argument('--init', '-i', action='store_true',
                        help='Full initialization: start coordinator and enable evolution mode')
    parser.add_argument('--on', '-e', action='store_true',
                        help='Enable evolution mode')
    parser.add_argument('--off', '-d', action='store_true',
                        help='Disable evolution mode')
    parser.add_argument('--toggle', '-t', action='store_true',
                        help='Toggle current state')
    parser.add_argument('--inject', action='store_true',
                        help='Print context prompt for injection')
    parser.add_argument('--status', '-s', action='store_true',
                        help='Show detailed status')
    
    args = parser.parse_args()

    # Full initialization (manual trigger /evolve)
    if args.init:
        was_active = is_mode_active()
        result = enable_mode()

        # Only show message if this is a fresh activation
        if not was_active:
            print(result)  # Print the enable message
            print("\n" + "="*60)
            print("🚀 协调器已启动")
            print("="*60)
            print("\n📋 下一步建议：")
            print("   - 输入编程任务（如：帮我实现一个登录功能）")
            print("   - 或直接开始描述您的需求")
            print("\n💡 提示：")
            print("   - programming-assistant 将自动加载")
            print("   - 进化模式已激活，会自动提取有价值经验")
            print("   - 使用 'python toggle_mode.py --off' 可关闭进化模式")
            print("="*60 + "\n")
        return 0

    # Inject context prompt (can be combined with other operations)
    if args.inject:
        if args.on or args.off or args.toggle:
            # Combine with state change
            if args.on:
                print(enable_mode())
            elif args.off:
                print(disable_mode())
            elif args.toggle:
                if is_mode_active():
                    print(disable_mode())
                else:
                    print(enable_mode())
            # Then print context if enabled
            if is_mode_active():
                print("\n--- Context Prompt ---")
                print(get_context_prompt())
            else:
                print("\n--- Context Prompt ---")
                print("(No context prompt - evolution mode is inactive)")
        else:
            # Just print context
            if is_mode_active():
                print("--- Context Prompt ---")
                print(get_context_prompt())
            else:
                print("Evolution mode is not active. No context prompt to inject.")
        return 0

    # Enable
    if args.on:
        print(enable_mode())
        return 0
    
    # Disable
    if args.off:
        print(disable_mode())
        return 0
    
    # Toggle
    if args.toggle:
        if is_mode_active():
            print(disable_mode())
        else:
            print(enable_mode())
        return 0
    
    # Status query
    if args.status:
        print(get_status_message())
        return 0
    
    # Default: show status
    print(get_status_message())
    return 0


if __name__ == '__main__':
    sys.exit(main())
