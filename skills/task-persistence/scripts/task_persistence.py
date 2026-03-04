#!/usr/bin/env python3
"""
Task Persistence System - Comprehensive solution for session continuity,
task recovery, and gateway monitoring.

Features:
1. Task Persistence: Save/restore long-running tasks
2. Session Snapshots: Automatic context backup and restore  
3. Gateway Monitoring: Detect restarts and provide feedback
4. State Management: Unified state tracking across all operations
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib

class TaskPersistenceManager:
    def __init__(self, workspace_path: str = None):
        self.workspace = workspace_path or os.getenv('OPENCLAW_WORKSPACE', '/home/admin/.openclaw/workspace')
        self.persistence_dir = Path(self.workspace) / 'persistence'
        self.tasks_file = self.persistence_dir / 'active_tasks.json'
        self.session_snapshots_dir = self.persistence_dir / 'session_snapshots'
        self.gateway_state_file = self.persistence_dir / 'gateway_state.json'
        
        # Initialize directories
        self.persistence_dir.mkdir(parents=True, exist_ok=True)
        self.session_snapshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Load current state
        self.active_tasks = self._load_active_tasks()
        self.gateway_state = self._load_gateway_state()
        
    def _load_active_tasks(self) -> Dict[str, Any]:
        """Load active tasks from disk"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _load_gateway_state(self) -> Dict[str, Any]:
        """Load gateway state from disk"""
        if self.gateway_state_file.exists():
            try:
                with open(self.gateway_state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {"last_restart": None, "startup_notified": False}
    
    def _save_active_tasks(self):
        """Save active tasks to disk"""
        with open(self.tasks_file, 'w') as f:
            json.dump(self.active_tasks, f, indent=2, default=str)
    
    def _save_gateway_state(self):
        """Save gateway state to disk"""
        with open(self.gateway_state_file, 'w') as f:
            json.dump(self.gateway_state, f, indent=2, default=str)
    
    def register_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Register a new task for persistence
        
        Args:
            task_id: Unique identifier for the task
            task_data: Task metadata including type, status, parameters, etc.
            
        Returns:
            bool: True if successfully registered
        """
        task_record = {
            "id": task_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "active",
            "data": task_data,
            "checkpoint": None
        }
        
        self.active_tasks[task_id] = task_record
        self._save_active_tasks()
        return True
    
    def update_task(self, task_id: str, status: str = None, checkpoint_data: Any = None) -> bool:
        """
        Update task status and/or checkpoint data
        
        Args:
            task_id: Task identifier
            status: New status (optional)
            checkpoint_data: Checkpoint data to save (optional)
            
        Returns:
            bool: True if successfully updated
        """
        if task_id not in self.active_tasks:
            return False
            
        if status:
            self.active_tasks[task_id]["status"] = status
        if checkpoint_data is not None:
            self.active_tasks[task_id]["checkpoint"] = checkpoint_data
            
        self.active_tasks[task_id]["updated_at"] = datetime.now().isoformat()
        self._save_active_tasks()
        return True
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as completed and remove from active tasks"""
        if task_id in self.active_tasks:
            del self.active_tasks[task_id]
            self._save_active_tasks()
            return True
        return False
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get list of all active tasks"""
        return list(self.active_tasks.values())
    
    def save_session_snapshot(self, session_data: Dict[str, Any]) -> str:
        """
        Save session snapshot for recovery
        
        Args:
            session_data: Complete session context and state
            
        Returns:
            str: Snapshot ID
        """
        snapshot_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        snapshot_file = self.session_snapshots_dir / f"snapshot_{snapshot_id}.json"
        
        snapshot_record = {
            "id": snapshot_id,
            "created_at": datetime.now().isoformat(),
            "session_data": session_data
        }
        
        with open(snapshot_file, 'w') as f:
            json.dump(snapshot_record, f, indent=2, default=str)
            
        return snapshot_id
    
    def get_latest_session_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the most recent session snapshot"""
        snapshot_files = list(self.session_snapshots_dir.glob("snapshot_*.json"))
        if not snapshot_files:
            return None
            
        latest_file = max(snapshot_files, key=os.path.getctime)
        try:
            with open(latest_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None
    
    def detect_gateway_restart(self) -> bool:
        """
        Detect if gateway has been restarted
        
        Returns:
            bool: True if restart detected
        """
        current_time = time.time()
        last_restart = self.gateway_state.get("last_restart", 0)
        
        # Simple detection: if we haven't recorded startup notification
        # and it's been more than 5 seconds since last check
        if not self.gateway_state.get("startup_notified", False):
            if current_time - last_restart > 5:
                self.gateway_state["last_restart"] = current_time
                self.gateway_state["startup_notified"] = True
                self._save_gateway_state()
                return True
        return False
    
    def mark_startup_notified(self):
        """Mark that startup notification has been sent"""
        self.gateway_state["startup_notified"] = True
        self.gateway_state["last_restart"] = time.time()
        self._save_gateway_state()
    
    def get_recovery_suggestions(self) -> List[str]:
        """
        Get suggestions for recovering from restart
        
        Returns:
            List of suggested recovery actions
        """
        suggestions = []
        
        # Check for active tasks
        active_tasks = self.get_active_tasks()
        if active_tasks:
            suggestions.append(f"Found {len(active_tasks)} active task(s) that may need recovery")
            
        # Check for session snapshots
        latest_snapshot = self.get_latest_session_snapshot()
        if latest_snapshot:
            suggestions.append("Session context available for restoration")
            
        return suggestions

def main():
    """Command line interface for task persistence system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Persistence System")
    parser.add_argument("--action", choices=["register", "update", "complete", "list", "snapshot", "recover", "detect-restart"], required=True)
    parser.add_argument("--task-id", help="Task identifier")
    parser.add_argument("--status", help="New task status")
    parser.add_argument("--data", help="Task data as JSON string")
    parser.add_argument("--session-file", help="Session data file for snapshot")
    
    args = parser.parse_args()
    
    manager = TaskPersistenceManager()
    
    if args.action == "register":
        if not args.task_id or not args.data:
            print("Error: --task-id and --data required for register action")
            return 1
        task_data = json.loads(args.data)
        success = manager.register_task(args.task_id, task_data)
        print(f"Task registered: {success}")
        
    elif args.action == "update":
        if not args.task_id:
            print("Error: --task-id required for update action")
            return 1
        success = manager.update_task(args.task_id, args.status)
        print(f"Task updated: {success}")
        
    elif args.action == "complete":
        if not args.task_id:
            print("Error: --task-id required for complete action")
            return 1
        success = manager.complete_task(args.task_id)
        print(f"Task completed: {success}")
        
    elif args.action == "list":
        tasks = manager.get_active_tasks()
        print(json.dumps(tasks, indent=2))
        
    elif args.action == "snapshot":
        if not args.session_file:
            print("Error: --session-file required for snapshot action")
            return 1
        with open(args.session_file, 'r') as f:
            session_data = json.load(f)
        snapshot_id = manager.save_session_snapshot(session_data)
        print(f"Snapshot saved: {snapshot_id}")
        
    elif args.action == "recover":
        suggestions = manager.get_recovery_suggestions()
        print("Recovery suggestions:")
        for suggestion in suggestions:
            print(f"- {suggestion}")
            
    elif args.action == "detect-restart":
        restart_detected = manager.detect_gateway_restart()
        print(f"Restart detected: {restart_detected}")
        if restart_detected:
            suggestions = manager.get_recovery_suggestions()
            if suggestions:
                print("Suggested actions:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")

if __name__ == "__main__":
    main()