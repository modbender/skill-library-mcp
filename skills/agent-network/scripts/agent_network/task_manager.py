#!/usr/bin/env python3
"""
Agent 群聊协作系统 - 任务管理模块
负责任务的创建、指派、状态更新、评论等
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from database import db
    from agent_manager import AgentManager
    from message_manager import MessageManager
except ImportError:
    from .database import db
    from .agent_manager import AgentManager
    from .message_manager import MessageManager


class TaskStatus:
    """任务状态常量"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority:
    """任务优先级常量"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Task:
    """任务类"""
    
    def __init__(self, id: int = None, task_db_id: int = None, task_id: str = "", title: str = "",
                 description: str = "", assigner_id: int = None, assignee_id: int = None,
                 group_id: Optional[int] = None, status: str = "pending", priority: str = "normal",
                 due_date: Optional[str] = None, completed_at: Optional[str] = None,
                 created_at: str = "", **kwargs):
        self.id = id if id is not None else task_db_id
        self.task_id = task_id
        self.title = title
        self.description = description
        self.assigner_id = assigner_id
        self.assignee_id = assignee_id
        self.group_id = group_id
        self.status = status
        self.priority = priority
        self.due_date = due_date
        self.completed_at = completed_at
        self.created_at = created_at
        
        # 额外字段
        self.assigner_name: Optional[str] = kwargs.get('assigner_name')
        self.assignee_name: Optional[str] = kwargs.get('assignee_name')
        self.group_name: Optional[str] = kwargs.get('group_name')
        self.comments: List[Dict] = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'assigner_id': self.assigner_id,
            'assigner_name': self.assigner_name,
            'assignee_id': self.assignee_id,
            'assignee_name': self.assignee_name,
            'group_id': self.group_id,
            'group_name': self.group_name,
            'status': self.status,
            'priority': self.priority,
            'due_date': self.due_date,
            'completed_at': self.completed_at,
            'created_at': self.created_at,
            'comments': self.comments
        }
    
    def __repr__(self):
        return f"Task({self.task_id}: {self.title} -> {self.assignee_name})"


class TaskManager:
    """任务管理器"""
    
    _task_counter = 0
    
    @staticmethod
    def generate_task_id() -> str:
        """生成任务唯一标识"""
        TaskManager._task_counter += 1
        return f"TASK-{datetime.now().strftime('%Y%m%d')}-{TaskManager._task_counter:03d}"
    
    @staticmethod
    def create(title: str, assigner_id: int, assignee_id: int,
               description: str = "", group_id: Optional[int] = None,
               priority: str = "normal", due_date: Optional[str] = None) -> Optional[Task]:
        """创建新任务"""
        task_id = TaskManager.generate_task_id()
        
        try:
            db_id = db.insert(
                """INSERT INTO tasks (task_id, title, description, assigner_id, assignee_id,
                    group_id, status, priority, due_date, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)""",
                (task_id, title, description, assigner_id, assignee_id,
                 group_id, priority, due_date, datetime.now().isoformat())
            )
            
            # 发送任务指派消息
            assigner = AgentManager.get_by_id(assigner_id)
            assignee = AgentManager.get_by_id(assignee_id)
            
            if assigner and assignee:
                content = f"📝 新任务指派给 @{assignee.name}\n\n**{title}**\n{description}\n\n优先级: {priority}"
                if due_date:
                    content += f" | 截止: {due_date}"
                content += f" | 任务ID: {task_id}"
                
                MessageManager.send_message(
                    from_agent_id=assigner_id,
                    content=content,
                    group_id=group_id,
                    to_agent_id=assignee_id,
                    msg_type="task_assign"
                )
            
            return TaskManager.get_by_id(db_id)
        except Exception as e:
            print(f"创建任务失败: {e}")
            return None
    
    @staticmethod
    def get_by_id(task_db_id: int) -> Optional[Task]:
        """通过 ID 获取任务"""
        row = db.fetch_one(
            """SELECT t.*, 
                      a1.name as assigner_name, 
                      a2.name as assignee_name,
                      g.name as group_name
               FROM tasks t
               LEFT JOIN agents a1 ON t.assigner_id = a1.id
               LEFT JOIN agents a2 ON t.assignee_id = a2.id
               LEFT JOIN groups g ON t.group_id = g.id
               WHERE t.id = ?""",
            (task_db_id,)
        )
        if row:
            task = Task(**row)
            task.assigner_name = row.get('assigner_name')
            task.assignee_name = row.get('assignee_name')
            task.group_name = row.get('group_name')
            task.comments = TaskManager.get_comments(task_db_id)
            return task
        return None
    
    @staticmethod
    def get_by_task_id(task_id: str) -> Optional[Task]:
        """通过任务标识获取任务"""
        row = db.fetch_one(
            """SELECT t.*, 
                      a1.name as assigner_name, 
                      a2.name as assignee_name,
                      g.name as group_name
               FROM tasks t
               LEFT JOIN agents a1 ON t.assigner_id = a1.id
               LEFT JOIN agents a2 ON t.assignee_id = a2.id
               LEFT JOIN groups g ON t.group_id = g.id
               WHERE t.task_id = ?""",
            (task_id,)
        )
        if row:
            task = Task(**row)
            task.assigner_name = row.get('assigner_name')
            task.assignee_name = row.get('assignee_name')
            task.group_name = row.get('group_name')
            task.comments = TaskManager.get_comments(row['id'])
            return task
        return None
    
    @staticmethod
    def get_all(status: Optional[str] = None, assignee_id: Optional[int] = None) -> List[Task]:
        """获取所有任务"""
        query = """SELECT t.*, 
                          a1.name as assigner_name, 
                          a2.name as assignee_name,
                          g.name as group_name
                   FROM tasks t
                   LEFT JOIN agents a1 ON t.assigner_id = a1.id
                   LEFT JOIN agents a2 ON t.assignee_id = a2.id
                   LEFT JOIN groups g ON t.group_id = g.id"""
        params = []
        conditions = []
        
        if status:
            conditions.append("t.status = ?")
            params.append(status)
        if assignee_id:
            conditions.append("t.assignee_id = ?")
            params.append(assignee_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY t.created_at DESC"
        
        rows = db.fetch_all(query, tuple(params))
        tasks = []
        for row in rows:
            task = Task(**row)
            task.assigner_name = row.get('assigner_name')
            task.assignee_name = row.get('assignee_name')
            task.group_name = row.get('group_name')
            task.comments = TaskManager.get_comments(row['id'])
            tasks.append(task)
        return tasks
    
    @staticmethod
    def update_status(task_db_id: int, new_status: str, updater_id: int, comment: str = "") -> bool:
        """更新任务状态"""
        valid_status = ['pending', 'in_progress', 'completed', 'cancelled']
        if new_status not in valid_status:
            print(f"无效的状态: {new_status}")
            return False
        
        task = TaskManager.get_by_id(task_db_id)
        if not task:
            return False
        
        completed_at = datetime.now().isoformat() if new_status == 'completed' else None
        
        affected = db.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (new_status, completed_at, task_db_id)
        )
        
        if affected > 0:
            # 添加评论记录状态变更
            status_text = {
                'pending': '待处理',
                'in_progress': '进行中',
                'completed': '已完成',
                'cancelled': '已取消'
            }.get(new_status, new_status)
            
            updater = AgentManager.get_by_id(updater_id)
            updater_name = updater.name if updater else f"Agent-{updater_id}"
            
            comment_text = f"状态变更为: {status_text}"
            if comment:
                comment_text += f" | 备注: {comment}"
            
            TaskManager.add_comment(task_db_id, updater_id, comment_text)
            
            # 发送状态变更通知
            content = f"✅ 任务 {task.task_id} 状态更新\n\n**{task.title}**\n新状态: {status_text}"
            if comment:
                content += f"\n备注: {comment}"
            
            MessageManager.send_message(
                from_agent_id=updater_id,
                content=content,
                group_id=task.group_id,
                to_agent_id=task.assignee_id if updater_id != task.assignee_id else task.assigner_id,
                msg_type="task_complete" if new_status == 'completed' else "chat"
            )
            
            return True
        return False
    
    @staticmethod
    def start_task(task_db_id: int, agent_id: int) -> bool:
        """开始任务（状态变为 in_progress）"""
        return TaskManager.update_status(task_db_id, 'in_progress', agent_id, "开始处理任务")
    
    @staticmethod
    def complete_task(task_db_id: int, agent_id: int, result: str = "") -> bool:
        """完成任务"""
        return TaskManager.update_status(task_db_id, 'completed', agent_id, result)
    
    @staticmethod
    def add_comment(task_db_id: int, agent_id: int, comment: str) -> bool:
        """添加任务评论"""
        try:
            db.execute(
                "INSERT INTO task_comments (task_id, agent_id, comment, created_at) VALUES (?, ?, ?, ?)",
                (task_db_id, agent_id, comment, datetime.now().isoformat())
            )
            return True
        except Exception as e:
            print(f"添加评论失败: {e}")
            return False
    
    @staticmethod
    def get_comments(task_db_id: int) -> List[Dict]:
        """获取任务评论"""
        rows = db.fetch_all(
            """SELECT tc.*, a.name as agent_name
               FROM task_comments tc
               JOIN agents a ON tc.agent_id = a.id
               WHERE tc.task_id = ?
               ORDER BY tc.created_at""",
            (task_db_id,)
        )
        return [dict(row) for row in rows]
    
    @staticmethod
    def delete(task_db_id: int) -> bool:
        """删除任务"""
        affected = db.execute("DELETE FROM tasks WHERE id = ?", (task_db_id,))
        return affected > 0
    
    @staticmethod
    def get_agent_tasks(agent_id: int, status: Optional[str] = None) -> List[Task]:
        """获取指定 Agent 的任务列表"""
        return TaskManager.get_all(status=status, assignee_id=agent_id)
    
    @staticmethod
    def format_task_for_display(task: Task) -> str:
        """格式化任务用于显示"""
        priority_emoji = {
            'low': '🔵',
            'normal': '🟡',
            'high': '🟠',
            'urgent': '🔴'
        }.get(task.priority, '⚪')
        
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅',
            'cancelled': '❌'
        }.get(task.status, '⚪')
        
        lines = [
            f"{status_emoji} {priority_emoji} [{task.task_id}] {task.title}",
            f"   指派给: {task.assignee_name} | 来自: {task.assigner_name}",
        ]
        
        if task.description:
            lines.append(f"   描述: {task.description[:50]}{'...' if len(task.description) > 50 else ''}")
        
        if task.due_date:
            lines.append(f"   截止: {task.due_date}")
        
        if task.comments:
            lines.append(f"   💬 {len(task.comments)} 条评论")
        
        return "\n".join(lines)
