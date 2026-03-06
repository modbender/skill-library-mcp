#!/usr/bin/env python3
"""
Telegram Bot - 命令监听与处理
- 轮询 Telegram updates
- 处理 /status, /pause, /resume, /skip, /approve, /retry, /tasks, /log 命令
- 所有命令支持 @项目名 限定
"""

import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


@dataclass
class TelegramCommand:
    """解析后的 Telegram 命令"""
    command: str           # 命令名（不含 /）
    project_name: Optional[str] = None  # @项目名（可选）
    args: List[str] = field(default_factory=list)  # 其他参数
    chat_id: str = ""
    message_id: int = 0
    from_user: str = ""
    timestamp: int = 0


@dataclass
class CommandResult:
    """命令执行结果"""
    success: bool
    message: str
    data: Optional[Any] = None


class TelegramCommandHandler:
    """
    Telegram 命令处理器
    
    支持的命令:
    - /status [@项目名] - 查看状态
    - /pause [@项目名] - 暂停项目
    - /resume [@项目名] - 恢复项目
    - /skip [@项目名] - 跳过当前任务
    - /approve [@项目名] - 确认人工检查点
    - /retry [@项目名] - 重试当前任务
    - /tasks [@项目名] - 查看任务列表
    - /log [@项目名] - 查看操作日志
    """
    
    # 支持的命令列表
    SUPPORTED_COMMANDS = ['status', 'pause', 'resume', 'skip', 'approve', 'retry', 'tasks', 'log']
    
    def __init__(self, bot_token: str, allowed_chat_ids: Optional[List[str]] = None):
        """
        初始化命令处理器
        
        Args:
            bot_token: Telegram Bot Token
            allowed_chat_ids: 允许的 Chat ID 列表（为空则允许所有）
        """
        self.bot_token = bot_token
        self.allowed_chat_ids = allowed_chat_ids or []
        self.api_base = f"https://api.telegram.org/bot{bot_token}"
        self._last_update_id = 0
        self._max_daily_total = 200  # 可通过 config 覆盖
    
    def poll_commands(self, timeout: int = 0) -> List[TelegramCommand]:
        """
        轮询 Telegram updates，解析命令
        
        使用 getUpdates API 的 offset 机制，确保不重复处理
        
        Args:
            timeout: long polling 超时（秒），0 表示不等待
        
        Returns:
            解析出的命令列表
        """
        url = f"{self.api_base}/getUpdates"
        
        params = {
            "offset": self._last_update_id + 1,
            "limit": 10,
            "timeout": timeout,
        }
        
        try:
            response = requests.get(url, params=params, timeout=timeout + 10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("ok"):
                logger.warning(f"Telegram API 返回错误: {data}")
                return []
            
            commands = []
            updates = data.get("result", [])
            
            for update in updates:
                update_id = update.get("update_id", 0)
                if update_id > self._last_update_id:
                    self._last_update_id = update_id
                
                # 解析消息
                message = update.get("message", {})
                text = message.get("text", "")
                
                if not text or not text.startswith("/"):
                    continue
                
                # 检查 Chat ID
                chat_id = str(message.get("chat", {}).get("id", ""))
                if self.allowed_chat_ids and chat_id not in self.allowed_chat_ids:
                    logger.debug(f"忽略未授权的 Chat: {chat_id}")
                    continue
                
                # 解析命令
                cmd = self._parse_command(text, message)
                if cmd and cmd.command in self.SUPPORTED_COMMANDS:
                    commands.append(cmd)
                    logger.info(f"收到命令: /{cmd.command} {cmd.project_name or ''}")
            
            return commands
            
        except requests.Timeout:
            return []
        except requests.RequestException as e:
            logger.warning(f"轮询 Telegram 失败: {e}")
            return []
        except Exception as e:
            logger.exception(f"轮询 Telegram 异常: {e}")
            return []
    
    def _parse_command(self, text: str, message: Dict) -> Optional[TelegramCommand]:
        """
        解析命令文本
        
        格式: /command[@botname] [@project] [args...]
        
        Args:
            text: 命令文本
            message: 原始消息
        
        Returns:
            解析后的命令，或 None
        """
        # 匹配: /command[@botname] @project args...
        # 或: /command[@botname] args...
        pattern = r'^/(\w+)(?:@\w+)?\s*(?:@(\S+))?\s*(.*)$'
        match = re.match(pattern, text.strip())
        
        if not match:
            return None
        
        command = match.group(1).lower()
        project_name = match.group(2)
        args_str = match.group(3).strip()
        
        args = args_str.split() if args_str else []
        
        return TelegramCommand(
            command=command,
            project_name=project_name,
            args=args,
            chat_id=str(message.get("chat", {}).get("id", "")),
            message_id=message.get("message_id", 0),
            from_user=message.get("from", {}).get("username", ""),
            timestamp=message.get("date", 0),
        )
    
    def send_reply(self, chat_id: str, text: str, reply_to: Optional[int] = None) -> bool:
        """
        发送回复消息
        
        Args:
            chat_id: Chat ID
            text: 消息文本
            reply_to: 回复的消息 ID（可选）
        
        Returns:
            是否成功
        """
        url = f"{self.api_base}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text,
        }
        
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.warning(f"发送回复失败: {e}")
            return False
    
    # ==================== 命令处理器 ====================
    
    def handle_status(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
        sessions: Dict[str, Any],
    ) -> CommandResult:
        """
        处理 /status 命令
        
        Args:
            cmd: 命令对象
            projects: 项目列表
            global_state: 全局状态
            sessions: Session 映射
        
        Returns:
            命令结果
        """
        if cmd.project_name:
            # 查看特定项目
            from .scheduler import get_project_by_name
            from .state_manager import get_project_state
            
            project = get_project_by_name(projects, cmd.project_name)
            if not project:
                return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
            
            proj_state = get_project_state(global_state, project.dir)
            
            # 格式化项目详情
            lines = [
                f"📊 项目详情: {project.name}",
                "",
                f"状态: {project.lifecycle.value}",
                f"优先级: {project.priority}",
                f"目录: {project.dir}",
            ]
            
            if proj_state.current_task:
                lines.append(f"当前任务: {proj_state.current_task}")
            
            if project.tasks_config:
                total = len(project.tasks_config.tasks)
                completed = sum(
                    1 for ts in proj_state.task_states.values()
                    if ts.status == "COMPLETED"
                )
                lines.append(f"任务进度: {completed}/{total}")
            
            lines.extend([
                "",
                f"今日发送: {proj_state.daily_sends}",
                f"连续失败: {proj_state.consecutive_failures}",
            ])
            
            if proj_state.last_send_at:
                lines.append(f"上次发送: {proj_state.last_send_at}")
            
            return CommandResult(True, "\n".join(lines))
        
        # 查看所有项目概览
        dashboard = self.format_dashboard(projects, global_state, sessions)
        return CommandResult(True, dashboard)
    
    def handle_pause(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /pause 命令"""
        from .scheduler import get_project_by_name, update_project_lifecycle, ProjectLifecycle
        
        if cmd.project_name:
            # 暂停特定项目
            project = get_project_by_name(projects, cmd.project_name)
            if not project:
                return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
            
            if project.lifecycle == ProjectLifecycle.PAUSED:
                return CommandResult(False, f"⚠️ 项目 {project.name} 已经是暂停状态")
            
            update_project_lifecycle(project, ProjectLifecycle.PAUSED, global_state)
            return CommandResult(True, f"⏸ 已暂停项目: {project.name}")
        
        # 暂停所有项目
        paused = []
        for project in projects:
            if project.lifecycle in (ProjectLifecycle.ENABLED, ProjectLifecycle.RUNNING):
                update_project_lifecycle(project, ProjectLifecycle.PAUSED, global_state)
                paused.append(project.name)
        
        if paused:
            return CommandResult(True, f"⏸ 已暂停 {len(paused)} 个项目: {', '.join(paused)}")
        else:
            return CommandResult(False, "⚠️ 没有可暂停的项目")
    
    def handle_resume(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /resume 命令"""
        from .scheduler import get_project_by_name, update_project_lifecycle, ProjectLifecycle
        
        if cmd.project_name:
            # 恢复特定项目
            project = get_project_by_name(projects, cmd.project_name)
            if not project:
                return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
            
            if project.lifecycle != ProjectLifecycle.PAUSED:
                return CommandResult(False, f"⚠️ 项目 {project.name} 不是暂停状态")
            
            update_project_lifecycle(project, ProjectLifecycle.RUNNING, global_state)
            return CommandResult(True, f"▶️ 已恢复项目: {project.name}")
        
        # 恢复所有暂停的项目
        resumed = []
        for project in projects:
            if project.lifecycle == ProjectLifecycle.PAUSED:
                update_project_lifecycle(project, ProjectLifecycle.RUNNING, global_state)
                resumed.append(project.name)
        
        if resumed:
            return CommandResult(True, f"▶️ 已恢复 {len(resumed)} 个项目: {', '.join(resumed)}")
        else:
            return CommandResult(False, "⚠️ 没有可恢复的项目")
    
    def handle_skip(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /skip 命令 - 跳过当前任务"""
        from .scheduler import get_project_by_name
        from .state_manager import get_project_state
        from .task_orchestrator import mark_task_complete
        
        if not cmd.project_name:
            return CommandResult(False, "❌ 请指定项目: /skip @项目名")
        
        project = get_project_by_name(projects, cmd.project_name)
        if not project:
            return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
        
        proj_state = get_project_state(global_state, project.dir)
        
        if not proj_state.current_task:
            return CommandResult(False, f"⚠️ 项目 {project.name} 没有正在进行的任务")
        
        task_id = proj_state.current_task
        mark_task_complete(task_id, proj_state.task_states, "手动跳过")
        proj_state.current_task = None
        
        return CommandResult(True, f"⏭ 已跳过任务: {task_id}")
    
    def handle_approve(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /approve 命令 - 确认人工检查点"""
        from .scheduler import get_project_by_name
        from .state_manager import get_project_state
        from .task_orchestrator import approve_task
        
        if not cmd.project_name:
            return CommandResult(False, "❌ 请指定项目: /approve @项目名")
        
        project = get_project_by_name(projects, cmd.project_name)
        if not project:
            return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
        
        proj_state = get_project_state(global_state, project.dir)
        
        # 查找 BLOCKED 状态的任务
        blocked_task = None
        for task_id, task_state in proj_state.task_states.items():
            if task_state.status == "BLOCKED":
                blocked_task = task_id
                break
        
        if not blocked_task:
            return CommandResult(False, f"⚠️ 项目 {project.name} 没有需要确认的任务")
        
        if approve_task(blocked_task, proj_state.task_states):
            return CommandResult(True, f"✅ 已批准任务: {blocked_task}")
        else:
            return CommandResult(False, f"❌ 批准任务失败: {blocked_task}")
    
    def handle_retry(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /retry 命令 - 重试当前任务"""
        from .scheduler import get_project_by_name
        from .state_manager import get_project_state
        
        if not cmd.project_name:
            return CommandResult(False, "❌ 请指定项目: /retry @项目名")
        
        project = get_project_by_name(projects, cmd.project_name)
        if not project:
            return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
        
        proj_state = get_project_state(global_state, project.dir)
        
        if not proj_state.current_task:
            return CommandResult(False, f"⚠️ 项目 {project.name} 没有正在进行的任务")
        
        # 重置连续失败计数
        proj_state.consecutive_failures = 0
        
        # 重置任务状态为 RUNNING
        task_id = proj_state.current_task
        if task_id in proj_state.task_states:
            proj_state.task_states[task_id].status = "RUNNING"
        
        return CommandResult(True, f"🔄 已重置任务 {task_id}，下次 tick 将重试")
    
    def handle_tasks(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /tasks 命令 - 查看任务列表"""
        from .scheduler import get_project_by_name
        from .state_manager import get_project_state
        from .task_orchestrator import format_task_progress
        
        if not cmd.project_name:
            return CommandResult(False, "❌ 请指定项目: /tasks @项目名")
        
        project = get_project_by_name(projects, cmd.project_name)
        if not project:
            return CommandResult(False, f"❌ 未找到项目: {cmd.project_name}")
        
        if not project.tasks_config or not project.tasks_config.tasks:
            return CommandResult(False, f"⚠️ 项目 {project.name} 没有配置任务")
        
        proj_state = get_project_state(global_state, project.dir)
        
        progress = format_task_progress(
            project.tasks_config.tasks,
            proj_state.task_states
        )
        
        return CommandResult(True, f"📋 项目 {project.name} 任务列表\n\n{progress}")
    
    def handle_log(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
    ) -> CommandResult:
        """处理 /log 命令 - 查看操作日志"""
        history = getattr(global_state, 'history', []) or []
        
        if cmd.project_name:
            # 过滤特定项目的日志
            history = [h for h in history if h.get('project') == cmd.project_name]
        
        # 取最近 10 条
        recent = history[-10:]
        
        if not recent:
            return CommandResult(True, "📝 暂无操作记录")
        
        lines = ["📝 操作日志（最近 10 条）", ""]
        
        for entry in reversed(recent):
            ts = entry.get('timestamp', '')[:19]  # 截取日期时间部分
            action = entry.get('action', '')
            project = entry.get('project', '')
            
            status = "✅" if entry.get('success', True) else "❌"
            
            lines.append(f"{status} [{ts}] {action} - {project}")
            
            if entry.get('error'):
                lines.append(f"   错误: {entry['error'][:50]}")
        
        return CommandResult(True, "\n".join(lines))
    
    def handle_command(
        self,
        cmd: TelegramCommand,
        projects: List[Any],
        global_state: Any,
        sessions: Dict[str, Any],
    ) -> CommandResult:
        """
        分发命令到对应的处理器
        
        Args:
            cmd: 命令对象
            projects: 项目列表
            global_state: 全局状态
            sessions: Session 映射
        
        Returns:
            命令结果
        """
        handlers = {
            'status': lambda: self.handle_status(cmd, projects, global_state, sessions),
            'pause': lambda: self.handle_pause(cmd, projects, global_state),
            'resume': lambda: self.handle_resume(cmd, projects, global_state),
            'skip': lambda: self.handle_skip(cmd, projects, global_state),
            'approve': lambda: self.handle_approve(cmd, projects, global_state),
            'retry': lambda: self.handle_retry(cmd, projects, global_state),
            'tasks': lambda: self.handle_tasks(cmd, projects, global_state),
            'log': lambda: self.handle_log(cmd, projects, global_state),
        }
        
        handler = handlers.get(cmd.command)
        if handler:
            try:
                return handler()
            except Exception as e:
                logger.exception(f"处理命令 /{cmd.command} 失败")
                return CommandResult(False, f"❌ 命令处理失败: {str(e)}")
        
        return CommandResult(False, f"❌ 未知命令: /{cmd.command}")
    
    def format_dashboard(
        self,
        projects: List[Any],
        global_state: Any,
        sessions: Dict[str, Any],
    ) -> str:
        """
        格式化多项目 Dashboard 视图
        
        参考设计文档 8.1 节的状态概览格式
        
        Args:
            projects: 项目列表
            global_state: 全局状态
            sessions: Session 映射
        
        Returns:
            格式化的 Dashboard 字符串
        """
        from .scheduler import ProjectLifecycle
        from .state_manager import get_project_state, get_total_daily_sends
        
        lines = ["📊 Autopilot Dashboard", ""]
        
        # 统计
        running_count = sum(1 for p in projects if p.lifecycle == ProjectLifecycle.RUNNING)
        paused_count = sum(1 for p in projects if p.lifecycle == ProjectLifecycle.PAUSED)
        total_sends = get_total_daily_sends(global_state)
        max_total = self._max_daily_total
        
        for project in projects:
            proj_state = get_project_state(global_state, project.dir)
            
            # 状态图标
            if project.lifecycle == ProjectLifecycle.PAUSED:
                icon = "⏸"
            elif project.lifecycle == ProjectLifecycle.COMPLETED:
                icon = "✅"
            elif project.lifecycle == ProjectLifecycle.ERROR:
                icon = "❌"
            elif project.dir in sessions:
                icon = "🟢"
            else:
                icon = "🟡"
            
            # 任务进度
            if project.tasks_config and project.tasks_config.tasks:
                total = len(project.tasks_config.tasks)
                completed = sum(
                    1 for ts in proj_state.task_states.values()
                    if ts.status == "COMPLETED"
                )
                progress_pct = int(completed / total * 100) if total > 0 else 0
                bar_filled = int(completed / total * 18) if total > 0 else 0
                bar = "█" * bar_filled + "░" * (18 - bar_filled)
                task_info = f"({completed}/{total} tasks)"
            else:
                progress_pct = 0
                bar = "░" * 18
                task_info = ""
            
            lines.append(f"{icon} {project.name} {task_info}")
            
            # 当前任务
            if proj_state.current_task:
                task_status = proj_state.task_states.get(proj_state.current_task)
                status_text = task_status.status if task_status else "UNKNOWN"
                lines.append(f"   当前: {proj_state.current_task} [{status_text}]")
            
            lines.append(f"   {bar} {progress_pct}%")
            lines.append("")
        
        # 汇总
        started_at = getattr(global_state, 'started_at', '')
        if started_at:
            try:
                start_time = datetime.fromisoformat(started_at)
                runtime = datetime.now() - start_time
                hours = int(runtime.total_seconds() // 3600)
                mins = int((runtime.total_seconds() % 3600) // 60)
                runtime_str = f"{hours}h{mins}m"
            except ValueError:
                runtime_str = "N/A"
        else:
            runtime_str = "N/A"
        
        lines.append(f"⏱ 运行时间: {runtime_str} | 今日发送: {total_sends}/{max_total}")
        
        return "\n".join(lines)


def create_command_handler_from_config(config: Dict[str, Any]) -> Optional[TelegramCommandHandler]:
    """
    从配置创建命令处理器
    
    Args:
        config: 配置字典
    
    Returns:
        TelegramCommandHandler 或 None
    """
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token")
    chat_id = telegram_config.get("chat_id")
    
    if not bot_token:
        logger.debug("Telegram bot_token 未配置，命令处理器禁用")
        return None
    
    allowed_chat_ids = [str(chat_id)] if chat_id else []
    
    handler = TelegramCommandHandler(bot_token, allowed_chat_ids)
    handler._max_daily_total = config.get('max_daily_sends_total', 200)
    return handler
