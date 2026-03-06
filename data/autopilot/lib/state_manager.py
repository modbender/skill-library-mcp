#!/usr/bin/env python3
"""
State Manager
- 状态持久化 (state.json)
- 配置读取 (config.yaml)
- 操作历史记录
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)

# 默认路径
AUTOPILOT_DIR = os.path.expanduser("~/.autopilot")
CONFIG_PATH = os.path.join(AUTOPILOT_DIR, "config.yaml")
STATE_PATH = os.path.join(AUTOPILOT_DIR, "state.json")
MAX_HISTORY_ENTRIES = 200


@dataclass
class HistoryEntry:
    timestamp: str
    action: str
    project: Optional[str] = None
    intent: Optional[str] = None
    reply: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class TaskStateInfo:
    """任务状态信息（用于持久化）- Phase 2"""
    status: str = "PENDING"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    sends: int = 0
    codex_summary: Optional[str] = None
    last_codex_output: Optional[str] = None
    last_send_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        d = {"status": self.status}
        if self.started_at:
            d["started_at"] = self.started_at
        if self.completed_at:
            d["completed_at"] = self.completed_at
        if self.sends > 0:
            d["sends"] = self.sends
        if self.codex_summary:
            d["codex_summary"] = self.codex_summary
        if self.last_codex_output:
            d["last_codex_output"] = self.last_codex_output[:500]  # 截断
        if self.last_send_at:
            d["last_send_at"] = self.last_send_at
        return d
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskStateInfo":
        """从字典创建"""
        return cls(
            status=data.get("status", "PENDING"),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            sends=data.get("sends", 0),
            codex_summary=data.get("codex_summary"),
            last_codex_output=data.get("last_codex_output"),
            last_send_at=data.get("last_send_at"),
        )


@dataclass
class ProjectState:
    daily_sends: int = 0
    daily_sends_date: str = ""
    last_send_at: Optional[str] = None
    consecutive_failures: int = 0
    last_output_hash: Optional[str] = None
    loop_count: int = 0
    # Phase 2: 任务编排字段
    current_task: Optional[str] = None
    task_states: Dict[str, TaskStateInfo] = field(default_factory=dict)
    # Phase 3: 多项目调度字段
    lifecycle: str = "enabled"  # disabled, enabled, running, paused, completed, error
    priority: int = 1


@dataclass
class GlobalState:
    projects: Dict[str, ProjectState] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    started_at: Optional[str] = None
    last_tick_at: Optional[str] = None
    # Phase 3: 多项目调度字段
    active_projects: List[str] = field(default_factory=list)
    paused_projects: List[str] = field(default_factory=list)
    project_send_order: List[str] = field(default_factory=list)  # round-robin 记录


def load_config() -> Dict[str, Any]:
    """
    读取配置文件
    
    Returns:
        配置字典
    """
    if not os.path.exists(CONFIG_PATH):
        logger.warning(f"配置文件不存在: {CONFIG_PATH}")
        return {}
    
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config or {}
    except Exception as e:
        logger.error(f"读取配置文件失败: {e}")
        return {}


def load_state() -> GlobalState:
    """
    读取状态文件
    
    Returns:
        GlobalState 对象
    """
    if not os.path.exists(STATE_PATH):
        return GlobalState(started_at=datetime.now().isoformat())
    
    try:
        with open(STATE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 解析项目状态
        projects = {}
        for name, proj_data in data.get('projects', {}).items():
            # 解析任务状态（Phase 2）
            task_states = {}
            for task_id, task_data in proj_data.get('task_states', {}).items():
                task_states[task_id] = TaskStateInfo.from_dict(task_data)
            
            projects[name] = ProjectState(
                daily_sends=proj_data.get('daily_sends', 0),
                daily_sends_date=proj_data.get('daily_sends_date', ''),
                last_send_at=proj_data.get('last_send_at'),
                consecutive_failures=proj_data.get('consecutive_failures', 0),
                last_output_hash=proj_data.get('last_output_hash'),
                loop_count=proj_data.get('loop_count', 0),
                # Phase 2 字段
                current_task=proj_data.get('current_task'),
                task_states=task_states,
                # Phase 3 字段
                lifecycle=proj_data.get('lifecycle', 'enabled'),
                priority=proj_data.get('priority', 1),
            )
        
        return GlobalState(
            projects=projects,
            history=data.get('history', []),
            started_at=data.get('started_at'),
            last_tick_at=data.get('last_tick_at'),
            # Phase 3 字段
            active_projects=data.get('active_projects', []),
            paused_projects=data.get('paused_projects', []),
            project_send_order=data.get('project_send_order', []),
        )
    
    except Exception as e:
        logger.error(f"读取状态文件失败: {e}")
        return GlobalState(started_at=datetime.now().isoformat())


def save_state(state: GlobalState) -> bool:
    """
    保存状态文件
    
    Args:
        state: GlobalState 对象
    
    Returns:
        是否成功
    """
    # 确保目录存在
    os.makedirs(AUTOPILOT_DIR, exist_ok=True)
    
    # 避免 history 无限增长
    if len(state.history) > MAX_HISTORY_ENTRIES:
        state.history = state.history[-MAX_HISTORY_ENTRIES:]
    
    # 转换为字典
    data = {
        'started_at': state.started_at,
        'last_tick_at': state.last_tick_at,
        'projects': {},
        'history': state.history,  # 只保留最近 MAX_HISTORY_ENTRIES 条历史
        # Phase 3 字段
        'active_projects': state.active_projects,
        'paused_projects': state.paused_projects,
        'project_send_order': state.project_send_order,
    }
    
    for name, proj in state.projects.items():
        proj_data = {
            'daily_sends': proj.daily_sends,
            'daily_sends_date': proj.daily_sends_date,
            'last_send_at': proj.last_send_at,
            'consecutive_failures': proj.consecutive_failures,
            'last_output_hash': proj.last_output_hash,
            'loop_count': proj.loop_count,
        }
        
        # Phase 2: 保存任务状态
        if proj.current_task:
            proj_data['current_task'] = proj.current_task
        if proj.task_states:
            proj_data['task_states'] = {
                task_id: ts.to_dict()
                for task_id, ts in proj.task_states.items()
            }
        
        # Phase 3: 保存生命周期和优先级
        proj_data['lifecycle'] = proj.lifecycle
        proj_data['priority'] = proj.priority
        
        data['projects'][name] = proj_data
    
    tmp_state_path = f"{STATE_PATH}.tmp"
    try:
        with open(tmp_state_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_state_path, STATE_PATH)
        return True
    except Exception as e:
        if os.path.exists(tmp_state_path):
            try:
                os.remove(tmp_state_path)
            except OSError:
                pass
        logger.error(f"保存状态文件失败: {e}")
        return False


def record_history(state: GlobalState, 
                   action: str,
                   project: Optional[str] = None,
                   intent: Optional[str] = None,
                   reply: Optional[str] = None,
                   success: bool = True,
                   error: Optional[str] = None) -> None:
    """
    追加操作记录
    
    Args:
        state: GlobalState 对象
        action: 操作类型
        project: 项目名称
        intent: 意图
        reply: 发送的回复
        success: 是否成功
        error: 错误信息
    """
    entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
    }
    
    if project:
        entry['project'] = project
    if intent:
        entry['intent'] = intent
    if reply:
        entry['reply'] = reply[:500]  # 截断
    if not success:
        entry['success'] = False
    if error:
        entry['error'] = error
    
    state.history.append(entry)
    if len(state.history) > MAX_HISTORY_ENTRIES:
        state.history = state.history[-MAX_HISTORY_ENTRIES:]


def get_project_state(state: GlobalState, project_dir: str) -> ProjectState:
    """
    获取项目状态（如果不存在则创建）
    
    Args:
        state: GlobalState 对象
        project_dir: 项目目录
    
    Returns:
        ProjectState 对象
    """
    if project_dir not in state.projects:
        state.projects[project_dir] = ProjectState()
    return state.projects[project_dir]


def reset_daily_sends_if_needed(proj_state: ProjectState) -> None:
    """
    如果是新的一天，重置每日发送计数
    """
    today = datetime.now().strftime('%Y-%m-%d')
    if proj_state.daily_sends_date != today:
        proj_state.daily_sends = 0
        proj_state.daily_sends_date = today


def increment_send_count(proj_state: ProjectState) -> None:
    """增加发送计数"""
    reset_daily_sends_if_needed(proj_state)
    proj_state.daily_sends += 1
    proj_state.last_send_at = datetime.now().isoformat()


def check_cooldown(proj_state: ProjectState, cooldown_seconds: int) -> bool:
    """
    检查是否在冷却期
    
    Args:
        proj_state: 项目状态
        cooldown_seconds: 冷却时间（秒）
    
    Returns:
        是否在冷却期（True = 需要等待）
    """
    if not proj_state.last_send_at:
        return False
    
    try:
        last_send = datetime.fromisoformat(proj_state.last_send_at)
        elapsed = (datetime.now() - last_send).total_seconds()
        return elapsed < cooldown_seconds
    except ValueError:
        return False


def check_daily_limit(proj_state: ProjectState, max_daily_sends: int) -> bool:
    """
    检查是否超过每日发送限制
    
    Args:
        proj_state: 项目状态
        max_daily_sends: 每日最大发送次数
    
    Returns:
        是否超限（True = 已达限制）
    """
    reset_daily_sends_if_needed(proj_state)
    return proj_state.daily_sends >= max_daily_sends


def get_total_daily_sends(state: GlobalState) -> int:
    """获取所有项目的今日总发送次数"""
    today = datetime.now().strftime('%Y-%m-%d')
    total = 0
    for proj in state.projects.values():
        if proj.daily_sends_date == today:
            total += proj.daily_sends
    return total
