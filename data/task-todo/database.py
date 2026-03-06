import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class TaskDatabase:
    """Database handler for task-todo agent skill."""
    
    def __init__(self, db_path: str = "tasks.db"):
        """Initialize the database connection."""
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_table()
    
    def _connect(self):
        """Establish database connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def _create_table(self):
        """Create the tasks table if it doesn't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed', 'blocked')),
                priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
    
    def add_task(self, title: str, description: str = "", status: str = "pending", priority: str = "medium") -> int:
        """
        Add a new task to the database.
        
        Args:
            title: Task title
            description: Task description
            status: Task status (pending, in_progress, completed, blocked)
            priority: Task priority (low, medium, high, urgent)
        
        Returns:
            The ID of the newly created task
        """
        now = datetime.now().isoformat()
        self.cursor.execute("""
            INSERT INTO tasks (title, description, status, priority, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, status, priority, now, now))
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        """
        Get a task by ID.
        
        Args:
            task_id: The task ID
        
        Returns:
            Task dictionary or None if not found
        """
        self.cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None
    
    def get_all_tasks(self) -> List[Dict]:
        """
        Get all tasks from the database.
        
        Returns:
            List of task dictionaries
        """
        self.cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_tasks_by_status(self, status: str) -> List[Dict]:
        """
        Get tasks filtered by status.
        
        Args:
            status: Task status to filter by
        
        Returns:
            List of task dictionaries
        """
        self.cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_tasks_by_priority(self, priority: str) -> List[Dict]:
        """
        Get tasks filtered by priority.
        
        Args:
            priority: Task priority to filter by
        
        Returns:
            List of task dictionaries
        """
        self.cursor.execute("SELECT * FROM tasks WHERE priority = ? ORDER BY created_at DESC", (priority,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_task(self, task_id: int, title: Optional[str] = None, 
                   description: Optional[str] = None, status: Optional[str] = None,
                   priority: Optional[str] = None) -> bool:
        """
        Update a task's fields.
        
        Args:
            task_id: The task ID to update
            title: New title (optional)
            description: New description (optional)
            status: New status (optional)
            priority: New priority (optional)
        
        Returns:
            True if task was updated, False if not found
        """
        # Build dynamic update query
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
        self.cursor.execute(query, params)
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task from the database.
        
        Args:
            task_id: The task ID to delete
        
        Returns:
            True if task was deleted, False if not found
        """
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()
        return self.cursor.rowcount > 0
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
