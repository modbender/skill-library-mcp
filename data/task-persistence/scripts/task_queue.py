#!/usr/bin/env python3
"""
Task Queue Manager for OpenClaw

Manages a persistent task queue that survives gateway restarts.
Provides task scheduling, prioritization, and recovery capabilities.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

class TaskQueueManager:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.tasks_dir = self.workspace_path / "tasks"
        self.queue_file = self.tasks_dir / "task_queue.json"
        self.completed_dir = self.tasks_dir / "completed"
        self.failed_dir = self.tasks_dir / "failed"
        
        # Initialize directories
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.completed_dir.mkdir(parents=True, exist_ok=True)
        self.failed_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize queue
        self.task_queue = self._load_queue()
    
    def _load_queue(self) -> List[Dict[str, Any]]:
        """Load task queue from disk."""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load task queue: {e}")
                return []
        return []
    
    def _save_queue(self):
        """Save task queue to disk."""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.task_queue, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error: Failed to save task queue: {e}")
    
    def add_task(self, task_id: str, task_type: str, description: str, 
                 priority: str = "normal", data: Dict[str, Any] = None,
                 dependencies: List[str] = None) -> bool:
        """
        Add a new task to the queue.
        
        Args:
            task_id: Unique identifier for the task
            task_type: Type of task (e.g., "file_processing", "skill_installation")
            description: Human-readable description
            priority: "high", "normal", "low"
            data: Task-specific data
            dependencies: List of task IDs that must complete before this task
        
        Returns:
            bool: True if task was added successfully
        """
        if any(task['id'] == task_id for task in self.task_queue):
            print(f"Task {task_id} already exists in queue")
            return False
        
        task = {
            "id": task_id,
            "type": task_type,
            "description": description,
            "priority": priority,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            "data": data or {},
            "dependencies": dependencies or [],
            "retry_count": 0,
            "max_retries": 3
        }
        
        self.task_queue.append(task)
        self._save_queue()
        print(f"Added task {task_id} to queue")
        return True
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task to execute based on priority and dependencies."""
        if not self.task_queue:
            return None
        
        # Sort by priority (high > normal > low)
        priority_order = {"high": 0, "normal": 1, "low": 2}
        sorted_tasks = sorted(
            self.task_queue, 
            key=lambda x: (priority_order.get(x['priority'], 1), x['created_at'])
        )
        
        for task in sorted_tasks:
            if task['status'] != 'queued':
                continue
            
            # Check dependencies
            if self._are_dependencies_satisfied(task['dependencies']):
                return task
        
        return None
    
    def _are_dependencies_satisfied(self, dependencies: List[str]) -> bool:
        """Check if all dependency tasks are completed."""
        if not dependencies:
            return True
        
        completed_tasks = set()
        for file in self.completed_dir.glob("*.json"):
            try:
                with open(file, 'r') as f:
                    task_data = json.load(f)
                    completed_tasks.add(task_data['id'])
            except (json.JSONDecodeError, IOError):
                continue
        
        return all(dep_id in completed_tasks for dep_id in dependencies)
    
    def start_task(self, task_id: str) -> bool:
        """Mark a task as started."""
        for task in self.task_queue:
            if task['id'] == task_id and task['status'] == 'queued':
                task['status'] = 'running'
                task['started_at'] = datetime.now().isoformat()
                self._save_queue()
                return True
        return False
    
    def complete_task(self, task_id: str, result_data: Dict[str, Any] = None) -> bool:
        """Mark a task as completed and move it to completed directory."""
        for i, task in enumerate(self.task_queue):
            if task['id'] == task_id and task['status'] == 'running':
                task['status'] = 'completed'
                task['completed_at'] = datetime.now().isoformat()
                if result_data:
                    task['result'] = result_data
                
                # Save to completed directory
                completed_file = self.completed_dir / f"{task_id}.json"
                try:
                    with open(completed_file, 'w', encoding='utf-8') as f:
                        json.dump(task, f, indent=2, ensure_ascii=False)
                except IOError as e:
                    print(f"Warning: Failed to save completed task {task_id}: {e}")
                
                # Remove from queue
                self.task_queue.pop(i)
                self._save_queue()
                return True
        return False
    
    def fail_task(self, task_id: str, error_message: str = None) -> bool:
        """Mark a task as failed and handle retries."""
        for task in self.task_queue:
            if task['id'] == task_id:
                task['retry_count'] += 1
                
                if task['retry_count'] < task['max_retries']:
                    # Reset to queued status for retry
                    task['status'] = 'queued'
                    task['started_at'] = None
                    self._save_queue()
                    print(f"Task {task_id} will be retried ({task['retry_count']}/{task['max_retries']})")
                    return True
                else:
                    # Mark as permanently failed
                    task['status'] = 'failed'
                    task['completed_at'] = datetime.now().isoformat()
                    if error_message:
                        task['error'] = error_message
                    
                    # Save to failed directory
                    failed_file = self.failed_dir / f"{task_id}.json"
                    try:
                        with open(failed_file, 'w', encoding='utf-8') as f:
                            json.dump(task, f, indent=2, ensure_ascii=False)
                    except IOError as e:
                        print(f"Warning: Failed to save failed task {task_id}: {e}")
                    
                    # Remove from queue
                    self.task_queue = [t for t in self.task_queue if t['id'] != task_id]
                    self._save_queue()
                    return True
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status summary."""
        status_counts = {"queued": 0, "running": 0, "completed": 0, "failed": 0}
        for task in self.task_queue:
            status_counts[task['status']] += 1
        
        # Count completed and failed tasks from disk
        status_counts["completed"] = len(list(self.completed_dir.glob("*.json")))
        status_counts["failed"] = len(list(self.failed_dir.glob("*.json")))
        
        return {
            "total_queued": len(self.task_queue),
            "status_counts": status_counts,
            "queue_size": len(self.task_queue),
            "next_task": self.get_next_task()
        }
    
    def clear_completed_tasks(self, days_old: int = 7) -> int:
        """Remove completed task files older than specified days."""
        cutoff_time = time.time() - (days_old * 24 * 3600)
        removed_count = 0
        
        for file in self.completed_dir.glob("*.json"):
            if file.stat().st_mtime < cutoff_time:
                try:
                    file.unlink()
                    removed_count += 1
                except OSError:
                    pass
        
        return removed_count
    
    def recover_from_crash(self) -> List[str]:
        """
        Recover tasks that were running when the system crashed.
        Moves running tasks back to queued status.
        """
        recovered_tasks = []
        
        for task in self.task_queue:
            if task['status'] == 'running':
                task['status'] = 'queued'
                task['started_at'] = None
                task['retry_count'] += 1
                recovered_tasks.append(task['id'])
        
        if recovered_tasks:
            self._save_queue()
            print(f"Recovered {len(recovered_tasks)} tasks from crash")
        
        return recovered_tasks

def main():
    """Command line interface for task queue management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenClaw Task Queue Manager")
    parser.add_argument("--workspace", required=True, help="OpenClaw workspace path")
    parser.add_argument("--action", choices=["status", "recover", "clear"], required=True)
    parser.add_argument("--days", type=int, default=7, help="Days for clearing old tasks")
    
    args = parser.parse_args()
    
    queue_manager = TaskQueueManager(args.workspace)
    
    if args.action == "status":
        status = queue_manager.get_queue_status()
        print(json.dumps(status, indent=2))
    elif args.action == "recover":
        recovered = queue_manager.recover_from_crash()
        print(f"Recovered tasks: {recovered}")
    elif args.action == "clear":
        removed = queue_manager.clear_completed_tasks(args.days)
        print(f"Removed {removed} old completed tasks")

if __name__ == "__main__":
    main()