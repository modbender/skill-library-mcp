#!/usr/bin/env python3
"""
Abby Autonomy - 任务队列管理

管理任务队列的读写和状态更新
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


# 任务队列文件路径
TASKS_DIR = Path(__file__).parent.parent / "tasks"
QUEUE_FILE = TASKS_DIR / "QUEUE.md"
STATE_FILE = Path(__file__).parent.parent / "memory" / "task_state.json"


class TaskQueue:
    """任务队列管理"""
    
    def __init__(self, queue_file: str = None, state_file: str = None):
        self.queue_file = queue_file or str(QUEUE_FILE)
        self.state_file = state_file or str(STATE_FILE)
        self.tasks_dir = TASKS_DIR
    
    def read_queue(self) -> Dict:
        """
        读取任务队列
        
        Returns:
            Dict: 队列内容
        """
        if not os.path.exists(self.queue_file):
            return {
                "ready": [],
                "in_progress": [],
                "done_today": [],
                "blocked": []
            }
        
        content = open(self.queue_file).read()
        return self._parse_queue(content)
    
    def _parse_queue(self, content: str) -> Dict:
        """解析队列 markdown"""
        result = {
            "ready": [],
            "in_progress": [],
            "done_today": [],
            "blocked": []
        }
        
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('## '):
                section_name = line.replace('## ', '').lower()
                if 'ready' in section_name:
                    current_section = 'ready'
                elif 'in progress' in section_name:
                    current_section = 'in_progress'
                elif 'done' in section_name:
                    current_section = 'done_today'
                elif 'blocked' in section_name:
                    current_section = 'blocked'
            
            elif line.startswith('- [ ]') and current_section:
                task = line.replace('- [ ]', '').strip()
                result[current_section].append(task)
        
        return result
    
    def write_queue(self, queue: Dict) -> bool:
        """写入队列"""
        lines = [
            "# Task Queue",
            f"最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Ready (可取用)",
        ]
        
        for task in queue.get('ready', []):
            lines.append(f"- [ ] {task}")
        
        lines.extend([
            "",
            "## In Progress (进行中)",
        ])
        
        for task in queue.get('in_progress', []):
            lines.append(f"- [x] {task}")
        
        lines.extend([
            "",
            "## Done Today (今日完成)",
        ])
        
        for task in queue.get('done_today', []):
            lines.append(f"- [x] {task}")
        
        lines.extend([
            "",
            "## Blocked (阻塞)",
        ])
        
        for task in queue.get('blocked', []):
            lines.append(f"- [ ] {task}")
        
        try:
            with open(self.queue_file, 'w') as f:
                f.write('\n'.join(lines))
            return True
        except Exception:
            return False
    
    def take_task(self, queue: Dict) -> Optional[str]:
        """
        取最高优先级的任务
        
        Args:
            queue: 当前队列
        
        Returns:
            str: 任务内容 或 None
        """
        if not queue.get('ready'):
            return None
        
        # 取第一个任务
        task = queue['ready'].pop(0)
        
        # 移到进行中
        queue['in_progress'].append(task)
        
        return task
    
    def complete_task(self, queue: Dict, task: str) -> bool:
        """
        完成任务
        
        Args:
            queue: 当前队列
            task: 任务内容
        
        Returns:
            bool: 是否成功
        """
        # 从进行中移除
        if task in queue.get('in_progress', []):
            queue['in_progress'].remove(task)
        
        # 移到已完成
        if 'done_today' not in queue:
            queue['done_today'] = []
        
        queue['done_today'].append(task)
        
        return self.write_queue(queue)
    
    def pause_task(self, queue: Dict, task: str) -> bool:
        """
        暂停任务
        
        Args:
            queue: 当前队列
            task: 任务内容
        
        Returns:
            bool: 是否成功
        """
        # 从进行中移除
        if task in queue.get('in_progress', []):
            queue['in_progress'].remove(task)
        
        # 放回 ready
        if 'ready' not in queue:
            queue['ready'] = []
        
        queue['ready'].insert(0, task)
        
        return self.write_queue(queue)


def get_queue() -> Dict:
    """获取队列"""
    q = TaskQueue()
    return q.read_queue()


def take_task() -> Optional[str]:
    """取任务"""
    q = TaskQueue()
    queue = q.read_queue()
    return q.take_task(queue)


def complete_task(task: str) -> bool:
    """完成任务"""
    q = TaskQueue()
    queue = q.read_queue()
    return q.complete_task(queue, task)


def pause_task(task: str) -> bool:
    """暂停任务"""
    q = TaskQueue()
    queue = q.read_queue()
    return q.pause_task(queue, task)
