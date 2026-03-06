#!/usr/bin/env python3
"""
Workflow Progress Tracker
Tracks and reports workflow decomposition progress.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

class WorkflowTracker:
    def __init__(self, workflow_file=None):
        self.workflow_file = workflow_file or "workflow-state.json"
        self.state = self.load_state()
    
    def load_state(self):
        if Path(self.workflow_file).exists():
            with open(self.workflow_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "workflow_id": None,
            "task": "",
            "decomposer_model": "",
            "steps": [],
            "current_step": 0,
            "started_at": None,
            "updated_at": None
        }
    
    def save_state(self):
        self.state["updated_at"] = datetime.now().isoformat()
        with open(self.workflow_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def initialize_workflow(self, task, model, steps):
        self.state.update({
            "workflow_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "task": task,
            "decomposer_model": model,
            "steps": steps,
            "current_step": 1,
            "started_at": datetime.now().isoformat()
        })
        self.save_state()
    
    def update_step_status(self, step_num, status, model_used=None, notes=None):
        for step in self.state["steps"]:
            if step["number"] == step_num:
                step["status"] = status
                if model_used:
                    step["model_used"] = model_used
                if notes:
                    step["notes"] = notes
                break
        self.save_state()
    
    def advance_step(self):
        if self.state["current_step"] < len(self.state["steps"]):
            self.state["current_step"] += 1
            self.save_state()
    
    def get_progress_report(self):
        total = len(self.state["steps"])
        current = self.state["current_step"]
        completed = sum(1 for s in self.state["steps"] if s.get("status") == "✅")
        
        report = {
            "task": self.state["task"],
            "decomposer_model": self.state["decomposer_model"],
            "total_steps": total,
            "current_step": current,
            "completed": completed,
            "progress_percent": round((completed / total) * 100) if total > 0 else 0,
            "steps": self.state["steps"]
        }
        return report
    
    def print_status(self):
        report = self.get_progress_report()
        print(f"\n📋 工作流进度报告")
        print(f"任务：{report['task']}")
        print(f"拆解模型：{report['decomposer_model']}")
        print(f"进度：{report['current_step']}/{report['total_steps']} ({report['progress_percent']}%)")
        print(f"\n步骤状态:")
        for step in report['steps']:
            status_icon = step.get('status', '⏳')
            model = step.get('model_used', '未指定')
            print(f"  {status_icon} 步骤 {step['number']}: {step['description']} [{model}]")

if __name__ == "__main__":
    tracker = WorkflowTracker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init" and len(sys.argv) > 3:
            task = sys.argv[2]
            model = sys.argv[3]
            # Steps would be passed as JSON
            steps = json.loads(sys.argv[4]) if len(sys.argv) > 4 else []
            tracker.initialize_workflow(task, model, steps)
            print("工作流已初始化")
        
        elif command == "status":
            tracker.print_status()
        
        elif command == "advance":
            tracker.advance_step()
            print("已推进到下一步")
        
        else:
            print(f"未知命令：{command}")
            print("可用命令：init, status, advance")
    else:
        tracker.print_status()
