#!/usr/bin/env python3
"""
Abby Autonomy - 状态检查

检查任务状态和紧急事项
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


# 状态文件路径
STATE_FILE = Path(__file__).parent.parent / "memory" / "task_state.json"


class TaskState:
    """任务状态追踪"""
    
    def __init__(self, state_file: str = None):
        self.state_file = state_file or str(STATE_FILE)
    
    def get_state(self) -> Dict:
        """获取当前状态"""
        if not os.path.exists(self.state_file):
            return {
                "current_task": None,
                "task_status": None,
                "estimated_completion": None,
                "progress": None,
                "started_at": None
            }
        
        try:
            with open(self.state_file) as f:
                return json.load(f)
        except Exception:
            return {
                "current_task": None,
                "task_status": None,
                "estimated_completion": None,
                "progress": None,
                "started_at": None
            }
    
    def set_state(self, state: Dict) -> bool:
        """设置状态"""
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
            return True
        except Exception:
            return False
    
    def start_task(self, task: str, estimated_minutes: int = 30) -> bool:
        """
        开始任务
        
        Args:
            task: 任务内容
            estimated_minutes: 预计完成时间
        
        Returns:
            bool: 是否成功
        """
        now = datetime.now()
        # 计算预计完成时间
        completion = now.fromtimestamp(now.timestamp() + estimated_minutes * 60)
        
        state = {
            "current_task": task,
            "task_status": "running",
            "estimated_completion": completion.strftime('%Y-%m-%d %H:%M'),
            "progress": "0%",
            "started_at": now.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.set_state(state)
    
    def update_progress(self, progress: str) -> bool:
        """更新进度"""
        state = self.get_state()
        if state.get('task_status') == 'running':
            state['progress'] = progress
            return self.set_state(state)
        return False
    
    def complete_task(self) -> bool:
        """完成任务"""
        return self.set_state({
            "current_task": None,
            "task_status": None,
            "estimated_completion": None,
            "progress": None,
            "started_at": None
        })
    
    def has_running_task(self) -> bool:
        """是否有正在执行的任务"""
        state = self.get_state()
        return state.get('task_status') == 'running'
    
    def get_current_task(self) -> Optional[str]:
        """获取当前任务"""
        state = self.get_state()
        return state.get('current_task')


# 全局状态检查
_state = None


def has_running_task() -> bool:
    """检查是否有正在执行的任务"""
    global _state
    if _state is None:
        _state = TaskState()
    return _state.has_running_task()


def get_current_task() -> Optional[str]:
    """获取当前任务"""
    global _state
    if _state is None:
        _state = TaskState()
    return _state.get_current_task()


def start_task(task: str, estimated_minutes: int = 30) -> bool:
    """开始任务"""
    global _state
    if _state is None:
        _state = TaskState()
    return _state.start_task(task, estimated_minutes)


def update_progress(progress: str) -> bool:
    """更新进度"""
    global _state
    if _state is None:
        _state = TaskState()
    return _state.update_progress(progress)


def complete_task() -> bool:
    """完成任务"""
    global _state
    if _state is None:
        _state = TaskState()
    return _state.complete_task()
