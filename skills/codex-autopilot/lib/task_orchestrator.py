#!/usr/bin/env python3
"""
Layer 3: Task Orchestrator
- 任务队列管理
- 完成条件检测
- 上下文传递
- 下一任务派发
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """任务状态"""
    PENDING = "PENDING"       # 等待依赖完成
    READY = "READY"           # 依赖已满足，可以开始
    RUNNING = "RUNNING"       # 正在执行
    VERIFYING = "VERIFYING"   # 验证完成条件
    COMPLETED = "COMPLETED"   # 已完成
    FAILED = "FAILED"         # 完成条件未满足
    BLOCKED = "BLOCKED"       # 需要人工处理


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    prompt: str
    depends_on: List[str] = field(default_factory=list)
    done_when: Optional[Dict[str, Any]] = None
    on_complete: Optional[str] = None
    requires_human_review: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """从字典创建 Task"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            prompt=data.get("prompt", ""),
            depends_on=data.get("depends_on", []),
            done_when=data.get("done_when"),
            on_complete=data.get("on_complete"),
            requires_human_review=data.get("requires_human_review", False),
        )


@dataclass
class TaskStateInfo:
    """任务状态信息（用于持久化）"""
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
class TasksConfig:
    """tasks.yaml 配置"""
    project_name: str = ""
    project_dir: str = ""
    description: str = ""
    enabled: bool = True
    priority: int = 1
    defaults: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Task] = field(default_factory=list)
    
    def get_default(self, key: str, fallback: Any = None) -> Any:
        """获取默认值"""
        return self.defaults.get(key, fallback)


class CyclicDependencyError(Exception):
    """循环依赖错误"""
    pass


def load_tasks(tasks_yaml_path: str) -> Optional[TasksConfig]:
    """
    加载 tasks.yaml 文件
    
    Args:
        tasks_yaml_path: tasks.yaml 文件路径
    
    Returns:
        TasksConfig 对象，如果文件不存在或解析失败返回 None
    """
    if not os.path.exists(tasks_yaml_path):
        logger.warning(f"tasks.yaml 不存在: {tasks_yaml_path}")
        return None
    
    try:
        with open(tasks_yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            logger.warning(f"tasks.yaml 为空: {tasks_yaml_path}")
            return None
        
        # 解析项目信息
        project_data = data.get("project", {})
        config = TasksConfig(
            project_name=project_data.get("name", ""),
            project_dir=project_data.get("dir", ""),
            description=project_data.get("description", ""),
            enabled=project_data.get("enabled", True),
            priority=project_data.get("priority", 1),
            defaults=data.get("defaults", {}),
        )
        
        # 解析任务列表
        tasks_data = data.get("tasks", [])
        for task_data in tasks_data:
            task = Task.from_dict(task_data)
            config.tasks.append(task)
        
        logger.info(f"加载了 {len(config.tasks)} 个任务从 {tasks_yaml_path}")
        return config
    
    except yaml.YAMLError as e:
        logger.error(f"解析 tasks.yaml 失败: {e}")
        return None
    except Exception as e:
        logger.error(f"加载 tasks.yaml 失败: {e}")
        return None


def detect_cyclic_dependencies(tasks: List[Task]) -> Optional[List[str]]:
    """
    检测循环依赖
    
    Args:
        tasks: 任务列表
    
    Returns:
        如果有循环，返回循环路径；否则返回 None
    """
    # 构建任务 ID 映射
    task_map = {t.id: t for t in tasks}
    
    # DFS 检测循环
    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {t.id: WHITE for t in tasks}
    path: List[str] = []
    
    def dfs(task_id: str) -> Optional[List[str]]:
        if task_id not in task_map:
            return None  # 依赖的任务不存在，忽略
        
        if color[task_id] == GRAY:
            # 找到循环
            cycle_start = path.index(task_id)
            return path[cycle_start:] + [task_id]
        
        if color[task_id] == BLACK:
            return None
        
        color[task_id] = GRAY
        path.append(task_id)
        
        task = task_map[task_id]
        for dep_id in task.depends_on:
            result = dfs(dep_id)
            if result:
                return result
        
        path.pop()
        color[task_id] = BLACK
        return None
    
    for task in tasks:
        if color[task.id] == WHITE:
            cycle = dfs(task.id)
            if cycle:
                return cycle
    
    return None


def get_ready_tasks(
    tasks: List[Task],
    task_states: Dict[str, TaskStateInfo]
) -> List[Task]:
    """
    找出所有依赖已满足的任务
    
    Args:
        tasks: 任务列表
        task_states: 任务状态字典
    
    Returns:
        所有状态为 PENDING 且依赖已完成的任务列表
    """
    ready_tasks = []
    
    for task in tasks:
        state = task_states.get(task.id)
        if not state:
            # 没有状态记录，视为 PENDING
            state = TaskStateInfo(status="PENDING")
            task_states[task.id] = state
        
        if state.status != "PENDING":
            continue
        
        # 检查所有依赖是否已完成
        deps_met = True
        for dep_id in task.depends_on:
            dep_state = task_states.get(dep_id)
            if not dep_state or dep_state.status != "COMPLETED":
                deps_met = False
                break
        
        if deps_met:
            ready_tasks.append(task)
    
    return ready_tasks


def build_prompt(
    task: Task,
    task_states: Dict[str, TaskStateInfo],
    tasks: List[Task]
) -> str:
    """
    构建带上下文的任务 prompt
    
    Args:
        task: 当前任务
        task_states: 任务状态字典
        tasks: 所有任务列表
    
    Returns:
        完整的 prompt 文本
    """
    parts = []
    
    # 1. 进度概览
    completed_count = sum(
        1 for s in task_states.values() if s.status == "COMPLETED"
    )
    total_count = len(tasks)
    parts.append(f"## 当前进度: {completed_count}/{total_count} 任务已完成\n")
    
    # 2. 前置上下文：之前任务的关键成果
    context_items = []
    for dep_id in task.depends_on:
        dep_state = task_states.get(dep_id)
        if dep_state and dep_state.codex_summary:
            # 找到依赖任务的名称
            dep_task = next((t for t in tasks if t.id == dep_id), None)
            dep_name = dep_task.name if dep_task else dep_id
            context_items.append(f"- {dep_name}: {dep_state.codex_summary}")
    
    if context_items:
        parts.append("## 已完成的前置工作\n")
        parts.append("\n".join(context_items))
        parts.append("\n")
    
    # 3. 当前任务
    parts.append(f"## 当前任务: {task.name}\n")
    parts.append(task.prompt)
    
    return "\n".join(parts)


def dispatch_next_task(
    tasks: List[Task],
    task_states: Dict[str, TaskStateInfo],
    current_task_id: Optional[str] = None,
    codex_summary: Optional[str] = None
) -> Tuple[Optional[Task], Optional[str]]:
    """
    派发下一个可执行任务
    
    Args:
        tasks: 任务列表
        task_states: 任务状态字典
        current_task_id: 当前任务 ID（如果要标记完成）
        codex_summary: 当前任务的 Codex 输出摘要
    
    Returns:
        (下一个任务, 生成的 prompt) 或 (None, None) 如果没有可执行任务
    """
    # 检测循环依赖
    cycle = detect_cyclic_dependencies(tasks)
    if cycle:
        cycle_str = " -> ".join(cycle)
        raise CyclicDependencyError(f"检测到循环依赖: {cycle_str}")
    
    # 标记当前任务完成（如果有）
    if current_task_id:
        mark_task_complete(current_task_id, task_states, codex_summary)
    
    # 查找下一个可执行任务
    ready_tasks = get_ready_tasks(tasks, task_states)
    
    if not ready_tasks:
        # 检查是否所有任务都完成了
        all_completed = all(
            task_states.get(t.id, TaskStateInfo()).status == "COMPLETED"
            for t in tasks
        )
        if all_completed:
            logger.info("所有任务已完成！")
        else:
            # 有任务被 BLOCKED 或依赖未满足
            logger.info("没有可执行的任务")
        return None, None
    
    # 取第一个 ready 的任务
    next_task = ready_tasks[0]
    
    # 检查是否需要人工审核
    if next_task.requires_human_review:
        # 标记为 BLOCKED，等待人工确认
        if next_task.id not in task_states:
            task_states[next_task.id] = TaskStateInfo()
        task_states[next_task.id].status = "BLOCKED"
        logger.info(f"任务 [{next_task.name}] 需要人工确认")
        return next_task, None
    
    # 生成 prompt
    prompt = build_prompt(next_task, task_states, tasks)
    
    # 更新任务状态
    if next_task.id not in task_states:
        task_states[next_task.id] = TaskStateInfo()
    
    state = task_states[next_task.id]
    state.status = "RUNNING"
    state.started_at = datetime.now().isoformat()
    state.sends += 1
    state.last_send_at = datetime.now().isoformat()
    
    logger.info(f"派发任务: {next_task.name}")
    return next_task, prompt


def mark_task_complete(
    task_id: str,
    task_states: Dict[str, TaskStateInfo],
    codex_summary: Optional[str] = None
) -> None:
    """
    标记任务完成
    
    Args:
        task_id: 任务 ID
        task_states: 任务状态字典
        codex_summary: Codex 输出摘要
    """
    if task_id not in task_states:
        task_states[task_id] = TaskStateInfo()
    
    state = task_states[task_id]
    state.status = "COMPLETED"
    state.completed_at = datetime.now().isoformat()
    
    if codex_summary:
        state.codex_summary = codex_summary
    
    logger.info(f"任务 [{task_id}] 已完成")


def mark_task_running(
    task_id: str,
    task_states: Dict[str, TaskStateInfo]
) -> None:
    """
    标记任务为运行状态
    
    Args:
        task_id: 任务 ID
        task_states: 任务状态字典
    """
    if task_id not in task_states:
        task_states[task_id] = TaskStateInfo()
    
    state = task_states[task_id]
    state.status = "RUNNING"
    if not state.started_at:
        state.started_at = datetime.now().isoformat()
    state.sends += 1
    state.last_send_at = datetime.now().isoformat()


def mark_task_failed(
    task_id: str,
    task_states: Dict[str, TaskStateInfo]
) -> None:
    """
    标记任务失败（验证未通过）
    
    Args:
        task_id: 任务 ID
        task_states: 任务状态字典
    """
    if task_id not in task_states:
        task_states[task_id] = TaskStateInfo()
    
    state = task_states[task_id]
    state.status = "RUNNING"  # 回到 RUNNING，让 Codex 继续
    

def approve_task(
    task_id: str,
    task_states: Dict[str, TaskStateInfo]
) -> bool:
    """
    人工批准任务开始
    
    Args:
        task_id: 任务 ID
        task_states: 任务状态字典
    
    Returns:
        是否成功批准
    """
    state = task_states.get(task_id)
    if not state or state.status != "BLOCKED":
        return False
    
    state.status = "PENDING"  # 改为 PENDING，下次会被 dispatch
    logger.info(f"任务 [{task_id}] 已获批准")
    return True


def get_task_by_id(tasks: List[Task], task_id: str) -> Optional[Task]:
    """根据 ID 获取任务"""
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def get_all_completed(
    tasks: List[Task],
    task_states: Dict[str, TaskStateInfo]
) -> bool:
    """检查是否所有任务都已完成"""
    for task in tasks:
        state = task_states.get(task.id)
        if not state or state.status != "COMPLETED":
            return False
    return True


def format_task_progress(
    tasks: List[Task],
    task_states: Dict[str, TaskStateInfo]
) -> str:
    """
    格式化任务进度为人类可读的字符串
    
    Returns:
        格式化的进度字符串
    """
    lines = []
    completed = 0
    
    for task in tasks:
        state = task_states.get(task.id, TaskStateInfo())
        status_emoji = {
            "PENDING": "⏳",
            "READY": "🔜",
            "RUNNING": "🔄",
            "VERIFYING": "🔍",
            "COMPLETED": "✅",
            "FAILED": "❌",
            "BLOCKED": "⏸",
        }.get(state.status, "❓")
        
        if state.status == "COMPLETED":
            completed += 1
        
        lines.append(f"{status_emoji} {task.name} [{state.status}]")
    
    # 进度条
    total = len(tasks)
    progress_pct = int(completed / total * 100) if total > 0 else 0
    bar_filled = int(completed / total * 20) if total > 0 else 0
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    
    header = f"进度: {bar} {progress_pct}% ({completed}/{total})\n\n"
    return header + "\n".join(lines)
