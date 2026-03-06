#!/usr/bin/env python3
"""
Session Catchup Script - 会话恢复工具

跨会话扫描：找到最近一次 planning 文件更新，
然后收集从该点到当前的所有对话上下文。

用法: python3 session-catchup.py [项目路径]

适配: Claude Code / Gemini CLI (可根据实际存储路径修改)
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Planning 三文件
PLANNING_FILES = ['task_plan.md', 'progress.md', 'findings.md']


def get_project_dir(project_path: str) -> Path:
    """
    将项目路径转换为 AI 工具存储路径格式。
    
    Claude Code: ~/.claude/projects/-path-to-project/
    Gemini CLI: 可能需要调整
    """
    sanitized = project_path.replace('/', '-')
    if not sanitized.startswith('-'):
        sanitized = '-' + sanitized
    sanitized = sanitized.replace('_', '-')
    
    # 尝试 Claude Code 路径
    claude_path = Path.home() / '.claude' / 'projects' / sanitized
    if claude_path.exists():
        return claude_path
    
    # 尝试 Gemini 路径 (如有)
    gemini_path = Path.home() / '.gemini' / 'projects' / sanitized
    if gemini_path.exists():
        return gemini_path
    
    return claude_path  # 默认返回 Claude 路径


def get_sessions_sorted(project_dir: Path) -> List[Path]:
    """获取所有会话文件，按修改时间排序（最新在前）。"""
    sessions = list(project_dir.glob('*.jsonl'))
    main_sessions = [s for s in sessions if not s.name.startswith('agent-')]
    return sorted(main_sessions, key=lambda p: p.stat().st_mtime, reverse=True)


def get_session_first_timestamp(session_file: Path) -> Optional[str]:
    """获取会话第一条消息的时间戳。"""
    try:
        with open(session_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    ts = data.get('timestamp')
                    if ts:
                        return ts
                except:
                    continue
    except:
        pass
    return None


def scan_for_planning_update(session_file: Path) -> Tuple[int, Optional[str]]:
    """
    快速扫描会话文件中的 planning 文件更新。
    返回 (行号, 文件名)，如未找到返回 (-1, None)。
    """
    last_update_line = -1
    last_update_file = None

    try:
        with open(session_file, 'r') as f:
            for line_num, line in enumerate(f):
                if '"Write"' not in line and '"Edit"' not in line:
                    continue

                try:
                    data = json.loads(line)
                    if data.get('type') != 'assistant':
                        continue

                    content = data.get('message', {}).get('content', [])
                    if not isinstance(content, list):
                        continue

                    for item in content:
                        if item.get('type') != 'tool_use':
                            continue
                        tool_name = item.get('name', '')
                        if tool_name not in ('Write', 'Edit'):
                            continue

                        file_path = item.get('input', {}).get('file_path', '')
                        for pf in PLANNING_FILES:
                            if file_path.endswith(pf):
                                last_update_line = line_num
                                last_update_file = pf
                                break
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass

    return last_update_line, last_update_file


def extract_messages_from_session(session_file: Path, after_line: int = -1) -> List[Dict]:
    """
    从会话文件中提取对话消息。
    如果 after_line >= 0，只提取该行之后的消息。
    如果 after_line < 0，提取所有消息。
    """
    result = []

    try:
        with open(session_file, 'r') as f:
            for line_num, line in enumerate(f):
                if after_line >= 0 and line_num <= after_line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                msg_type = msg.get('type')
                is_meta = msg.get('isMeta', False)

                if msg_type == 'user' and not is_meta:
                    content = msg.get('message', {}).get('content', '')
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                content = item.get('text', '')
                                break
                        else:
                            content = ''

                    if content and isinstance(content, str):
                        # 跳过系统/命令消息
                        if content.startswith(('<local-command', '<command-', '<task-notification')):
                            continue
                        if len(content) > 20:
                            result.append({
                                'role': 'user',
                                'content': content,
                                'line': line_num,
                                'session': session_file.stem[:8]
                            })

                elif msg_type == 'assistant':
                    msg_content = msg.get('message', {}).get('content', '')
                    text_content = ''
                    tool_uses = []

                    if isinstance(msg_content, str):
                        text_content = msg_content
                    elif isinstance(msg_content, list):
                        for item in msg_content:
                            if item.get('type') == 'text':
                                text_content = item.get('text', '')
                            elif item.get('type') == 'tool_use':
                                tool_name = item.get('name', '')
                                tool_input = item.get('input', {})
                                if tool_name == 'Edit':
                                    tool_uses.append(f"Edit: {tool_input.get('file_path', 'unknown')}")
                                elif tool_name == 'Write':
                                    tool_uses.append(f"Write: {tool_input.get('file_path', 'unknown')}")
                                elif tool_name == 'Bash':
                                    cmd = tool_input.get('command', '')[:80]
                                    tool_uses.append(f"Bash: {cmd}")
                                elif tool_name == 'AskUserQuestion':
                                    tool_uses.append("AskUserQuestion")
                                else:
                                    tool_uses.append(f"{tool_name}")

                    if text_content or tool_uses:
                        result.append({
                            'role': 'assistant',
                            'content': text_content[:600] if text_content else '',
                            'tools': tool_uses,
                            'line': line_num,
                            'session': session_file.stem[:8]
                        })
    except Exception:
        pass

    return result


def main():
    project_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    project_dir = get_project_dir(project_path)

    if not project_dir.exists():
        print(f"未找到项目存储目录: {project_dir}")
        print("提示: 确保已在此项目中使用过 AI 助手")
        return

    sessions = get_sessions_sorted(project_dir)
    if len(sessions) < 2:
        print("会话数量不足，无需恢复")
        return

    # 跳过当前会话 (最新修改的 = 索引 0)
    previous_sessions = sessions[1:]

    # 在所有之前的会话中找到最近的 planning 文件更新
    update_session = None
    update_line = -1
    update_file = None
    update_session_idx = -1

    for idx, session in enumerate(previous_sessions):
        line, filename = scan_for_planning_update(session)
        if line >= 0:
            update_session = session
            update_line = line
            update_file = filename
            update_session_idx = idx
            break

    if not update_session:
        print("在之前的会话中未找到 planning 文件更新")
        return

    # 收集从更新点开始的所有消息
    all_messages = []

    # 1. 获取包含更新的会话中的消息（在更新行之后）
    messages_from_update_session = extract_messages_from_session(update_session, after_line=update_line)
    all_messages.extend(messages_from_update_session)

    # 2. 获取更新会话到当前会话之间的所有消息
    intermediate_sessions = previous_sessions[:update_session_idx]

    # 按时间顺序处理（从旧到新）
    for session in reversed(intermediate_sessions):
        messages = extract_messages_from_session(session, after_line=-1)
        all_messages.extend(messages)

    if not all_messages:
        print("未发现需要恢复的上下文")
        return

    # 输出恢复报告
    print("\n[会话恢复] 检测到未同步的上下文")
    print(f"最后 planning 更新: {update_file} (会话 {update_session.stem[:8]}...)")

    sessions_covered = update_session_idx + 1
    if sessions_covered > 1:
        print(f"扫描了 {sessions_covered} 个会话")

    print(f"未同步消息数: {len(all_messages)}")

    print("\n--- 未同步的上下文 ---")

    # 最多显示 100 条消息
    MAX_MESSAGES = 100
    if len(all_messages) > MAX_MESSAGES:
        print(f"(显示最后 {MAX_MESSAGES} 条，共 {len(all_messages)} 条)\n")
        messages_to_show = all_messages[-MAX_MESSAGES:]
    else:
        messages_to_show = all_messages

    current_session = None
    for msg in messages_to_show:
        # 会话切换时显示标记
        if msg.get('session') != current_session:
            current_session = msg.get('session')
            print(f"\n[会话: {current_session}...]")

        if msg['role'] == 'user':
            print(f"用户: {msg['content'][:300]}")
        else:
            if msg.get('content'):
                print(f"AI: {msg['content'][:300]}")
            if msg.get('tools'):
                print(f"  工具: {', '.join(msg['tools'][:4])}")

    print("\n--- 建议操作 ---")
    print("1. 运行: git diff --stat")
    print("2. 阅读: task_plan.md, progress.md, findings.md")
    print("3. 根据上述上下文更新 planning 文件")
    print("4. 继续任务")


if __name__ == '__main__':
    main()
