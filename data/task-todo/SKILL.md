---
name: Task-Todo Agent Skill
description: A task management agent skill that provides persistent task storage
  and management using SQLite database. This skill enables AI agents to create,
  read, update, delete, and query tasks with status t...
---

# Task-Todo Agent Skill

## Overview

A task management agent skill that provides persistent task storage and management using SQLite database. This skill enables AI agents to create, read, update, delete, and query tasks with status tracking and priority management.

## Capabilities

- **Task Creation**: Add new tasks with title, description, status, and priority
- **Task Retrieval**: Get single tasks or list all tasks
- **Task Filtering**: Filter tasks by status or priority
- **Task Updates**: Modify any task field (title, description, status, priority)
- **Task Deletion**: Remove tasks from the database
- **Persistent Storage**: All tasks stored in SQLite database with automatic timestamps

## Usage

### Command Line Interface

```bash
# Add task
python task_skill.py add "Task title" "Description" --status pending --priority high

# List all tasks
python task_skill.py list

# Filter by status
python task_skill.py list --status in_progress

# Filter by priority
python task_skill.py list --priority urgent

# Get task details
python task_skill.py get 1

# Update task
python task_skill.py update 1 --status completed --priority low

# Delete task
python task_skill.py delete 1
```

## Data Model

### Task Fields

| Field | Type | Description | Required | Default |
|-------|------|-------------|----------|---------|
| id | INTEGER | Auto-generated task ID | Auto | - |
| title | TEXT | Task title | Yes | - |
| description | TEXT | Task description | No | "" |
| status | TEXT | Task status | Yes | "pending" |
| priority | TEXT | Task priority | Yes | "medium" |
| created_at | TIMESTAMP | Creation timestamp | Auto | Current time |
| updated_at | TIMESTAMP | Last update timestamp | Auto | Current time |

### Status Values

- `pending` - Task is pending and not started
- `in_progress` - Task is currently being worked on
- `completed` - Task is finished
- `blocked` - Task is blocked and cannot proceed

### Priority Values

- `low` - Low priority task
- `medium` - Medium priority task (default)
- `high` - High priority task
- `urgent` - Urgent task requiring immediate attention

## Response Format

All agent methods return a dictionary with a `success` field:

### Successful Add
```python
{
    "success": True,
    "task_id": 1,
    "message": "Task created with ID: 1"
}
```

### Successful List
```python
{
    "success": True,
    "tasks": [
        {
            "id": 1,
            "title": "Task title",
            "description": "Task description",
            "status": "pending",
            "priority": "medium",
            "created_at": "2026-02-11T10:30:00",
            "updated_at": "2026-02-11T10:30:00"
        }
    ],
    "count": 1
}
```

### Successful Get
```python
{
    "success": True,
    "task": {
        "id": 1,
        "title": "Task title",
        "description": "Task description",
        "status": "pending",
        "priority": "medium",
        "created_at": "2026-02-11T10:30:00",
        "updated_at": "2026-02-11T10:30:00"
    }
}
```

### Failed Operation
```python
{
    "success": False,
    "message": "Task 1 not found"
}
```

## Database

- **Database File**: `tasks.db` (created automatically in current directory)
- **Database Type**: SQLite3
- **Schema Constraints**: Status and priority values are validated at database level
- **Timestamps**: Automatically managed by the database

## Dependencies

None - uses Python's built-in `sqlite3` module.

## Use Cases

1. **Task Tracking**: Track personal or project tasks with status and priority
2. **TODO Management**: Maintain a persistent TODO list
3. **Workflow Automation**: Integrate task management into automated workflows
4. **Project Management**: Simple project task tracking
5. **Agent Memory**: Provide AI agents with persistent task storage

## Notes

- The database connection is persistent across operations
- Always call `agent.close()` when finished to properly close the database
- Use context manager pattern for automatic cleanup:
  ```python
  with TaskAgent() as agent:
      agent.add_task("Task", "Description")
  ```
- Task IDs are auto-incrementing integers starting from 1
- All timestamps are in ISO 8601 format
