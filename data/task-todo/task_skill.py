#!/usr/bin/env python3
"""
Task-Todo Agent Skill
A command-line agent for managing tasks with SQLite database.
"""

import sys
from typing import Optional
from database import TaskDatabase


class TaskAgent:
    """Agent for managing tasks."""
    
    def __init__(self, db_path: str = "tasks.db"):
        """Initialize the task agent."""
        self.db = TaskDatabase(db_path)
    
    def add_task(self, title: str, description: str = "", status: str = "pending", 
                 priority: str = "medium") -> dict:
        """Add a new task."""
        task_id = self.db.add_task(title, description, status, priority)
        return {"success": True, "task_id": task_id, "message": f"Task created with ID: {task_id}"}
    
    def get_task(self, task_id: int) -> dict:
        """Get a specific task."""
        task = self.db.get_task(task_id)
        if task:
            return {"success": True, "task": task}
        return {"success": False, "message": f"Task {task_id} not found"}
    
    def list_tasks(self, status: Optional[str] = None, priority: Optional[str] = None) -> dict:
        """List all tasks or filter by status/priority."""
        if status:
            tasks = self.db.get_tasks_by_status(status)
        elif priority:
            tasks = self.db.get_tasks_by_priority(priority)
        else:
            tasks = self.db.get_all_tasks()
        
        return {"success": True, "tasks": tasks, "count": len(tasks)}
    
    def update_task(self, task_id: int, title: Optional[str] = None,
                   description: Optional[str] = None, status: Optional[str] = None,
                   priority: Optional[str] = None) -> dict:
        """Update a task."""
        updated = self.db.update_task(task_id, title, description, status, priority)
        if updated:
            return {"success": True, "message": f"Task {task_id} updated"}
        return {"success": False, "message": f"Task {task_id} not found or no changes made"}
    
    def delete_task(self, task_id: int) -> dict:
        """Delete a task."""
        deleted = self.db.delete_task(task_id)
        if deleted:
            return {"success": True, "message": f"Task {task_id} deleted"}
        return {"success": False, "message": f"Task {task_id} not found"}
    
    def close(self):
        """Close the database connection."""
        self.db.close()


def print_task(task: dict):
    """Pretty print a single task."""
    print(f"\n{'='*60}")
    print(f"ID:          {task['id']}")
    print(f"Title:       {task['title']}")
    print(f"Description: {task['description']}")
    print(f"Status:      {task['status']}")
    print(f"Priority:    {task['priority']}")
    print(f"Created:     {task['created_at']}")
    print(f"Updated:     {task['updated_at']}")
    print(f"{'='*60}\n")


def print_task_list(tasks: list):
    """Pretty print a list of tasks."""
    if not tasks:
        print("\nNo tasks found.\n")
        return
    
    print(f"\n{'ID':<6} {'Title':<30} {'Status':<15} {'Priority':<10}")
    print("-" * 70)
    for task in tasks:
        title = task['title'][:27] + "..." if len(task['title']) > 30 else task['title']
        print(f"{task['id']:<6} {title:<30} {task['status']:<15} {task['priority']:<10}")
    print()


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("""
Task-Todo Agent Skill

Usage:
  python task_skill.py add <title> [description] [--status STATUS] [--priority PRIORITY]
  python task_skill.py list [--status STATUS] [--priority PRIORITY]
  python task_skill.py get <task_id>
  python task_skill.py update <task_id> [--title TITLE] [--description DESC] [--status STATUS] [--priority PRIORITY]
  python task_skill.py delete <task_id>

Status Options:  pending, in_progress, completed, blocked
Priority Options: low, medium, high, urgent

Examples:
  python task_skill.py add "Write documentation" "Create README file" --priority high
  python task_skill.py list --status pending
  python task_skill.py update 1 --status in_progress
  python task_skill.py delete 5
        """)
        sys.exit(1)
    
    agent = TaskAgent()
    command = sys.argv[1].lower()
    
    try:
        if command == "add":
            if len(sys.argv) < 3:
                print("Error: Title is required")
                sys.exit(1)
            
            title = sys.argv[2]
            description = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith("--") else ""
            
            # Parse optional arguments
            status = "pending"
            priority = "medium"
            i = 3 if description else 3
            while i < len(sys.argv):
                if sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                    status = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                    priority = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.add_task(title, description, status, priority)
            print(f"\n✓ {result['message']}\n")
        
        elif command == "list":
            status = None
            priority = None
            i = 2
            while i < len(sys.argv):
                if sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                    status = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                    priority = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.list_tasks(status, priority)
            print(f"\nFound {result['count']} task(s):")
            print_task_list(result['tasks'])
        
        elif command == "get":
            if len(sys.argv) < 3:
                print("Error: Task ID is required")
                sys.exit(1)
            
            task_id = int(sys.argv[2])
            result = agent.get_task(task_id)
            
            if result['success']:
                print_task(result['task'])
            else:
                print(f"\n✗ {result['message']}\n")
        
        elif command == "update":
            if len(sys.argv) < 3:
                print("Error: Task ID is required")
                sys.exit(1)
            
            task_id = int(sys.argv[2])
            title = None
            description = None
            status = None
            priority = None
            
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--title" and i + 1 < len(sys.argv):
                    title = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--description" and i + 1 < len(sys.argv):
                    description = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                    status = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                    priority = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            result = agent.update_task(task_id, title, description, status, priority)
            if result['success']:
                print(f"\n✓ {result['message']}\n")
            else:
                print(f"\n✗ {result['message']}\n")
        
        elif command == "delete":
            if len(sys.argv) < 3:
                print("Error: Task ID is required")
                sys.exit(1)
            
            task_id = int(sys.argv[2])
            result = agent.delete_task(task_id)
            
            if result['success']:
                print(f"\n✓ {result['message']}\n")
            else:
                print(f"\n✗ {result['message']}\n")
        
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        sys.exit(1)
    
    finally:
        agent.close()


if __name__ == "__main__":
    main()
