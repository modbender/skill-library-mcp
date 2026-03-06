#!/usr/bin/env python3
"""
Telegram Todo List Manager
Manage TODO.md file through file operations and text parsing.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Tuple

TODO_FILE = "/root/.openclaw/workspace/TODO.md"


def read_todo() -> str:
    """Read TODO.md file content."""
    try:
        with open(TODO_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return create_default_template()
    except Exception as e:
        print(f"Error reading TODO.md: {e}")
        return create_default_template()


def write_todo(content: str) -> bool:
    """Write content to TODO.md file."""
    try:
        with open(TODO_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing TODO.md: {e}")
        return False


def create_default_template() -> str:
    """Create default TODO.md template."""
    template = """# TODO List

## 今日任务 (2026-02-12)

- [ ] **学习并掌握 skill-creator 技能介绍**
  - 理解技能创建的核心原则
  - 学习渐进式披露设计模式
  - 掌握技能结构和创建流程
  - 实际创建一个简单的 skill

---

## 待完成任务

### 技能开发
- [ ] 创建第一个自定义 skill
- [ ] 学习参考文档输出模式
- [ ] 练习脚本资源的打包

### 技术研究
- [ ] 深入理解渐进式披露的实践应用
- [ ] 探索不同自由度的指令粒度选择

---

## 已完成任务

- [x] **介绍 skill-creator 技能**
  - 记录时间：2026-02-12 07:55 UTC
  - 内容：skill-creator 是一个技能开发指南，用于创建或更新 Agent 技能

---

## 临时笔记

**Skill-creator 学习要点：**
- 核心：模块化、自包含的能力包
- 原则：简洁优先、适度自由度
- 结构：SKILL.md + �script/（可选）
- 流程：6步创建流程
- 设计：渐进式披露、按需引用

**下一步：**
1. 选择一个具体场景创建 skill
2. 实践练习渐进式披露
3. 打包并测试创建的 skill
"""
    write_todo(template)
    return template


def parse_tasks(content: str) -> List[Dict]:
    """Parse TODO.md content into structured tasks."""
    tasks = []

    # Current date for "今日任务"
    today = datetime.now().strftime("%Y-%m-%d")
    section_headers = [
        f"今日任务 ({today})",
        "待完成任务",
        "已完成任务"
    ]

    current_section = None
    current_task = None
    current_subtasks = []

    for line in content.split('\n'):
        stripped = line.strip()

        # Check for section headers
        for header in section_headers:
            if stripped == f"## {header}":
                # Save previous task if exists
                if current_task and current_section == "今日任务":
                    tasks.append({
                        'section': '今日任务',
                        'main_task': current_task,
                        'subtasks': current_subtasks,
                        'completed': False
                    })
                    current_task = None
                    current_subtasks = []
                current_section = header
                break

        # Check for task lines
        if re.match(r'^-\s+\[([ x])\]\s*\*\*(.+?)\*\*.*?$', stripped):
            # Save previous task
            if current_task and current_subtasks:
                tasks.append({
                    'section': current_section,
                    'main_task': current_task,
                    'subtasks': current_subtasks,
                    'completed': stripped.startswith('[- ]')
                })
                current_subtasks = []

            # Parse new task
            match = re.match(r'^-\s+\[([ x])\]\s*\*\*(.+?)\*\*(.+)?$', stripped)
            if match:
                current_task = match.group(2)
                completed = match.group(1) == 'x'

        # Check for subtasks (indented lines)
        elif stripped.startswith('  -') or stripped.startswith('\t-'):
            subtask = stripped.replace('  - ', '').replace('\t- ', '').strip()
            if subtask and not subtask.startswith('- ['):
                current_subtasks.append(subtask)

        # Subsection headers
        elif stripped.startswith('### '):
            current_section = stripped.replace('### ', '')

    # Don't forget last task
    if current_task and current_subtasks:
        tasks.append({
            'section': current_section or '待完成任务',
            'main_task': current_task,
            'subtasks': current_subtasks,
            'completed': stripped.startswith('[- ]') if stripped.startswith('-') else False
        })

    return tasks


def format_tasks_display(tasks: List[Dict]) -> str:
    """Format tasks for display."""
    lines = []
    lines.append("📋 待办事项列表\n")

    for task in tasks:
        status = "✅" if task['completed'] else "⬜"
        lines.append(f"{status} {task['main_task']}")
        for subtask in task['subtasks']:
            lines.append(f"   - {subtask}")

        # Add section indicator
        if task['section'] != '待完成任务':
            lines.append(f"   📌 {task['section']}")

    # Calculate statistics
    total = len(tasks)
    completed = sum(1 for t in tasks if t['completed'])
    pending = total - completed

    lines.append("\n待办总数：{} 项未完成".format(pending))
    lines.append("已完成：{} 项".format(completed))

    return '\n'.join(lines)


def find_task_by_number(content: str, task_num: int) -> Tuple[int, str, bool]:
    """Find task by number and return line number, content, and status."""
    tasks = parse_tasks(content)
    if 1 <= task_num <= len(tasks):
        task = tasks[task_num - 1]
        # Find the line with this task in content
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('- [x]') and task_num == i + 1:
                return i, line, True
            elif line.strip().startswith('- [ ]') and task_num == i + 1:
                return i, line, False
    return -1, "", False


def mark_task_complete(content: str, task_num: int) -> Tuple[str, bool]:
    """Mark task as complete and return updated content."""
    line_num, line, is_complete = find_task_by_number(content, task_num)

    if line_num == -1:
        return content, False

    if is_complete:
        return content, True  # Already complete

    # Replace [ ] with [x]
    updated_line = line.replace('- [ ]', '- [x]')
    lines = content.split('\n')
    lines[line_num] = updated_line

    return '\n'.join(lines), True


def find_task_start(content: str, task_num: int) -> int:
    """Find the starting line number of a task."""
    tasks = parse_tasks(content)
    if 1 <= task_num <= len(tasks):
        current_count = 0
        for line in content.split('\n'):
            if line.strip().startswith('- [') and not line.strip().startswith('#'):
                current_count += 1
                if current_count == task_num:
                    # Find the section header line before this task
                    line_idx = content.split('\n').index(line)
                    # Check previous lines for section header
                    for i in range(max(0, line_idx - 10), line_idx):
                        if content.split('\n')[i].strip().startswith('## '):
                            return i
                    return 0  # Start of file
    return 0


def add_task(content: str, main_task: str, section: str = "今日任务", subtasks: List[str] = None) -> str:
    """Add a new task to the TODO.md file."""
    lines = content.split('\n')
    main_task_lines = [f"- [ ] **{main_task}**"]

    if subtasks:
        main_task_lines.extend([f"  - {st}" for st in subtasks])

    # Find section location
    section_index = -1
    for i, line in enumerate(lines):
        if f"## {section}" in line:
            section_index = i
            break

    if section_index != -1:
        # Insert after section header
        insert_pos = section_index + 1
        lines = lines[:insert_pos] + main_task_lines + lines[insert_pos:]
    else:
        # Add to end of content
        lines = lines + main_task_lines + ["", "---"]

    return '\n'.join(lines)


def delete_task(content: str, task_num: int) -> str:
    """Delete a task by number."""
    lines = content.split('\n')
    found = False

    for i in range(len(lines)):
        stripped = lines[i].strip()
        if stripped.startswith('- [') and stripped.startswith('- [x]'):
            task_count = int(stripped[3])  # Extract number after ' - ['
            if task_count == task_num:
                # Delete this line and any subtasks (next few lines)
                # Skip until we find a line not starting with indentation
                j = i + 1
                while j < len(lines) and (lines[j].strip().startswith('  -') or lines[j].strip().startswith('\t-')):
                    j += 1
                lines = lines[:i] + lines[j:]
                found = True
                break

    if not found:
        return content

    return '\n'.join(lines)


if __name__ == "__main__":
    # Example usage
    content = read_todo()
    tasks = parse_tasks(content)
    print(format_tasks_display(tasks))
