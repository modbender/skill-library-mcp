"""
状态管理模块
"""

import json
from datetime import datetime
from pathlib import Path


class StateManager:
    """管理版本状态"""
    
    def __init__(self, version_dir):
        self.version_dir = Path(version_dir)
        self.state_file = self.version_dir / ".state.json"
        self.data = {}
        
        if self.state_file.exists():
            self.load()
    
    def init(self, version):
        """初始化新版本状态"""
        self.data = {
            "version": version,
            "status": "initialized",
            "current_task": None,
            "tasks": [],
            "architecture_confirmed": False,
            "revision_feedback": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        self.save()
    
    def load(self):
        """加载状态"""
        with open(self.state_file) as f:
            self.data = json.load(f)
    
    def save(self):
        """保存状态"""
        self.data["updated_at"] = datetime.now().isoformat()
        self.version_dir.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.data, f, indent=2)
    
    def update_status(self, status):
        """更新状态"""
        self.data["status"] = status
        self.save()
    
    def set_tasks(self, tasks):
        """设置任务列表"""
        self.data["tasks"] = tasks
        self.save()
    
    def set_current_task(self, task_id):
        """设置当前任务"""
        self.data["current_task"] = task_id
        self.save()
    
    def get_task(self, task_id):
        """获取任务"""
        for task in self.data.get("tasks", []):
            if task["id"] == task_id:
                return task
        return None
    
    def update_task_status(self, task_id, status):
        """更新任务状态"""
        for task in self.data.get("tasks", []):
            if task["id"] == task_id:
                task["status"] = status
                break
        self.save()
    
    def get_next_pending_task(self):
        """获取下一个待处理任务"""
        for task in self.data.get("tasks", []):
            if task["status"] == "pending":
                return task
        return None
