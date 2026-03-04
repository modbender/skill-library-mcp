#!/usr/bin/env python3
"""
Layer 4: Multi-Project Scheduler (多项目调度器)
- 项目注册 & 生命周期管理
- 轮询调度 (round-robin / priority)
- 全局资源控制
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .task_orchestrator import TasksConfig, load_tasks

logger = logging.getLogger(__name__)

# 默认路径
AUTOPILOT_DIR = os.path.expanduser("~/.autopilot")
PROJECTS_DIR = os.path.join(AUTOPILOT_DIR, "projects")


class ProjectLifecycle(Enum):
    """项目生命周期状态"""
    DISABLED = "disabled"     # tasks.yaml 中 enabled: false
    ENABLED = "enabled"       # 已注册但还没开始
    RUNNING = "running"       # 正在自动驾驶中
    PAUSED = "paused"         # 用户手动暂停
    COMPLETED = "completed"   # 所有任务完成
    ERROR = "error"           # 连续失败超限


@dataclass
class ProjectInfo:
    """项目元信息"""
    name: str
    dir: str
    enabled: bool = True
    priority: int = 1
    lifecycle: ProjectLifecycle = ProjectLifecycle.ENABLED
    tasks_config: Optional[TasksConfig] = None
    description: str = ""
    
    # 项目级覆盖配置
    overrides: Dict[str, Any] = field(default_factory=dict)
    
    def get_override(self, key: str, default: Any = None) -> Any:
        """获取项目级覆盖配置"""
        return self.overrides.get(key, default)
    
    @classmethod
    def from_tasks_config(cls, tasks_config: TasksConfig, 
                           tasks_yaml_path: str) -> "ProjectInfo":
        """从 TasksConfig 创建 ProjectInfo"""
        # 从 tasks.yaml 提取项目级覆盖
        overrides = {}
        
        # 尝试读取完整的 YAML 获取 overrides
        try:
            with open(tasks_yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                project_data = data.get("project", {})
                overrides = project_data.get("overrides", {})
        except Exception:
            pass
        
        return cls(
            name=tasks_config.project_name or os.path.basename(tasks_config.project_dir),
            dir=tasks_config.project_dir,
            enabled=tasks_config.enabled,
            priority=tasks_config.priority,
            lifecycle=ProjectLifecycle.ENABLED if tasks_config.enabled else ProjectLifecycle.DISABLED,
            tasks_config=tasks_config,
            description=tasks_config.description,
            overrides=overrides,
        )


def load_all_projects(config: Dict[str, Any]) -> List[ProjectInfo]:
    """
    扫描并加载所有项目
    
    来源:
    1. ~/.autopilot/projects/*/tasks.yaml
    2. config.yaml 的 project_dirs
    
    Args:
        config: 全局配置字典
    
    Returns:
        项目列表（已去重）
    """
    projects: Dict[str, ProjectInfo] = {}  # name -> ProjectInfo
    
    # 1. 扫描 ~/.autopilot/projects/*/tasks.yaml
    if os.path.isdir(PROJECTS_DIR):
        for entry in os.listdir(PROJECTS_DIR):
            project_path = os.path.join(PROJECTS_DIR, entry)
            if not os.path.isdir(project_path):
                continue
            
            tasks_yaml = os.path.join(project_path, "tasks.yaml")
            if not os.path.exists(tasks_yaml):
                continue
            
            tasks_config = load_tasks(tasks_yaml)
            if not tasks_config:
                logger.warning(f"无法加载项目 {entry} 的 tasks.yaml")
                continue
            
            project = ProjectInfo.from_tasks_config(tasks_config, tasks_yaml)
            projects[project.name] = project
            logger.info(f"从 projects/ 加载项目: {project.name} (priority={project.priority})")
    
    # 2. 从 config.yaml 的 project_dirs 加载
    project_dirs = config.get('project_dirs', [])
    for project_dir in project_dirs:
        if not os.path.isdir(project_dir):
            logger.warning(f"项目目录不存在: {project_dir}")
            continue
        
        project_name = os.path.basename(project_dir)
        
        # 检查是否已从 projects/ 加载
        if project_name in projects:
            logger.debug(f"项目 {project_name} 已从 projects/ 加载，跳过 project_dirs")
            continue
        
        # 查找 tasks.yaml
        tasks_yaml = None
        
        # 优先查找 ~/.autopilot/projects/{name}/tasks.yaml
        autopilot_tasks = os.path.join(PROJECTS_DIR, project_name, "tasks.yaml")
        if os.path.exists(autopilot_tasks):
            tasks_yaml = autopilot_tasks
        else:
            # 回退到项目内的 .autopilot/tasks.yaml
            project_tasks = os.path.join(project_dir, ".autopilot", "tasks.yaml")
            if os.path.exists(project_tasks):
                tasks_yaml = project_tasks
        
        if tasks_yaml:
            tasks_config = load_tasks(tasks_yaml)
            if tasks_config:
                # 确保 project_dir 正确
                tasks_config.project_dir = project_dir
                project = ProjectInfo.from_tasks_config(tasks_config, tasks_yaml)
                projects[project.name] = project
                logger.info(f"从 project_dirs 加载项目: {project.name}")
            else:
                # tasks.yaml 解析失败，创建一个空项目
                projects[project_name] = ProjectInfo(
                    name=project_name,
                    dir=project_dir,
                    enabled=True,
                    priority=10,  # 低优先级
                    lifecycle=ProjectLifecycle.ENABLED,
                )
                logger.info(f"从 project_dirs 加载项目（无任务）: {project_name}")
        else:
            # 没有 tasks.yaml，创建一个空项目（Phase 1 模式）
            projects[project_name] = ProjectInfo(
                name=project_name,
                dir=project_dir,
                enabled=True,
                priority=10,  # 低优先级
                lifecycle=ProjectLifecycle.ENABLED,
            )
            logger.info(f"从 project_dirs 加载项目（无任务）: {project_name}")
    
    return list(projects.values())


def schedule_projects(
    projects: List[ProjectInfo],
    sessions: Dict[str, Any],
    config: Dict[str, Any],
    global_state: Any,
) -> List[ProjectInfo]:
    """
    根据调度策略返回本轮应处理的项目列表
    
    过滤条件:
    - 只包含 ENABLED/RUNNING 生命周期的项目
    - 排除没有活跃 session 的项目
    - 排除在冷却期的项目
    - 排除达到每日限额的项目
    
    Args:
        projects: 所有项目列表
        sessions: {project_dir -> SessionInfo} 映射
        config: 全局配置
        global_state: 全局状态
    
    Returns:
        本轮应处理的项目列表（已按策略排序）
    """
    from .state_manager import check_cooldown, check_daily_limit, get_project_state
    
    scheduler_config = config.get('scheduler', {})
    strategy = scheduler_config.get('strategy', 'round-robin')
    max_sends_per_tick = scheduler_config.get('max_sends_per_tick', 1)
    
    # 过滤可操作的项目
    actionable: List[Tuple[ProjectInfo, float]] = []  # (project, sort_key)
    
    for project in projects:
        # 检查生命周期
        if project.lifecycle not in (ProjectLifecycle.ENABLED, ProjectLifecycle.RUNNING):
            logger.debug(f"跳过项目 {project.name}: 生命周期 {project.lifecycle.value}")
            continue
        
        # 检查是否启用
        if not project.enabled:
            continue
        
        # 检查是否有活跃 session
        if project.dir not in sessions:
            logger.debug(f"跳过项目 {project.name}: 没有活跃 session")
            continue
        
        # 检查冷却期
        proj_state = get_project_state(global_state, project.dir)
        cooldown = project.get_override('cooldown', config.get('cooldown', 120))
        if check_cooldown(proj_state, cooldown):
            logger.debug(f"跳过项目 {project.name}: 在冷却期")
            continue
        
        # 检查每日限额
        max_daily = project.get_override('max_daily_sends', config.get('max_daily_sends', 50))
        if check_daily_limit(proj_state, max_daily):
            logger.debug(f"跳过项目 {project.name}: 达到每日限额")
            continue
        
        # 计算排序键
        if strategy == "priority":
            sort_key = project.priority
        else:
            # round-robin: 按上次发送时间排序（最久未发送的优先）
            last_send = proj_state.last_send_at
            if last_send:
                try:
                    sort_key = datetime.fromisoformat(last_send).timestamp()
                except ValueError:
                    sort_key = 0
            else:
                sort_key = 0  # 从未发送过的优先
        
        actionable.append((project, sort_key))
    
    # 排序
    if strategy == "priority":
        # 优先级：数字越小越高
        actionable.sort(key=lambda x: x[1])
    else:
        # round-robin: 所有可操作项目都应轮流处理
        # 按上次发送时间排序（最久未发送的优先）
        actionable.sort(key=lambda x: x[1])
    
    # 返回所有可操作项目（不截断），让主循环控制发送次数
    result = [p for p, _ in actionable]
    
    logger.info(f"调度策略 {strategy}: 选中 {len(result)} 个项目 (共 {len(projects)} 个)")
    return result


def update_project_lifecycle(
    project: ProjectInfo,
    new_lifecycle: ProjectLifecycle,
    global_state: Any,
) -> None:
    """
    更新项目生命周期状态
    
    同时更新 global_state 中的 active_projects/paused_projects
    
    Args:
        project: 项目信息
        new_lifecycle: 新生命周期状态
        global_state: 全局状态
    """
    old_lifecycle = project.lifecycle
    project.lifecycle = new_lifecycle
    
    # 更新 global_state
    active_projects = getattr(global_state, 'active_projects', []) or []
    paused_projects = getattr(global_state, 'paused_projects', []) or []
    
    # 从旧列表中移除
    if project.name in active_projects:
        active_projects.remove(project.name)
    if project.name in paused_projects:
        paused_projects.remove(project.name)
    
    # 添加到新列表
    if new_lifecycle in (ProjectLifecycle.ENABLED, ProjectLifecycle.RUNNING):
        if project.name not in active_projects:
            active_projects.append(project.name)
    elif new_lifecycle == ProjectLifecycle.PAUSED:
        if project.name not in paused_projects:
            paused_projects.append(project.name)
    
    # 更新 global_state
    global_state.active_projects = active_projects
    global_state.paused_projects = paused_projects
    
    logger.info(f"项目 {project.name} 生命周期: {old_lifecycle.value} -> {new_lifecycle.value}")


def update_project_send_order(
    project_name: str,
    global_state: Any,
) -> None:
    """
    更新 round-robin 发送顺序
    
    将刚发送的项目移到列表末尾
    
    Args:
        project_name: 项目名称
        global_state: 全局状态
    """
    send_order = getattr(global_state, 'project_send_order', []) or []
    
    # 移除已有的
    if project_name in send_order:
        send_order.remove(project_name)
    
    # 添加到末尾
    send_order.append(project_name)
    
    # 保持列表不超过 100 项
    if len(send_order) > 100:
        send_order = send_order[-100:]
    
    global_state.project_send_order = send_order


def get_project_by_name(
    projects: List[ProjectInfo],
    name: str,
) -> Optional[ProjectInfo]:
    """
    根据名称查找项目
    
    支持模糊匹配（不区分大小写）
    
    Args:
        projects: 项目列表
        name: 项目名称
    
    Returns:
        匹配的项目，或 None
    """
    name_lower = name.lower()
    
    # 精确匹配
    for project in projects:
        if project.name.lower() == name_lower:
            return project
    
    # 前缀匹配
    for project in projects:
        if project.name.lower().startswith(name_lower):
            return project
    
    return None
