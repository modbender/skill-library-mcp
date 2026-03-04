# Task-Todo Agent Skill

A Python-based task management agent with SQLite database integration. Manage your tasks with statuses, priorities, and full CRUD operations via command-line interface.

## Features

- ✅ **CRUD Operations**: Create, read, update, and delete tasks
- 📊 **Status Tracking**: Track tasks with statuses: `pending`, `in_progress`, `completed`, `blocked`
- 🎯 **Priority Levels**: Organize by priority: `low`, `medium`, `high`, `urgent`
- 💾 **SQLite Database**: Persistent storage with automatic timestamps
- 🖥️ **CLI Interface**: Easy-to-use command-line interface
- 🔍 **Filtering**: List tasks by status or priority

## Installation

No external dependencies required! Uses Python's built-in `sqlite3` module.

```bash
cd task-todo
python task_skill.py
```

## Usage

### Add a Task

```bash
python task_skill.py add "Task title" ["Optional description"] [--status STATUS] [--priority PRIORITY]
```

Examples:
```bash
# Simple task
python task_skill.py add "Write documentation"

# Task with description
python task_skill.py add "Write documentation" "Create comprehensive README"

# Task with priority
python task_skill.py add "Fix critical bug" "System crashes on startup" --priority urgent --status in_progress
```

### List Tasks

```bash
# List all tasks
python task_skill.py list

# Filter by status
python task_skill.py list --status pending
python task_skill.py list --status in_progress

# Filter by priority
python task_skill.py list --priority urgent
python task_skill.py list --priority high
```

### Get Task Details

```bash
python task_skill.py get <task_id>
```

Example:
```bash
python task_skill.py get 1
```

### Update a Task

```bash
python task_skill.py update <task_id> [--title TITLE] [--description DESC] [--status STATUS] [--priority PRIORITY]
```

Examples:
```bash
# Update status
python task_skill.py update 1 --status completed

# Update priority
python task_skill.py update 2 --priority high

# Update multiple fields
python task_skill.py update 3 --title "New title" --status in_progress --priority urgent
```

### Delete a Task

```bash
python task_skill.py delete <task_id>
```

Example:
```bash
python task_skill.py delete 5
```

## Field Options

### Status
- `pending` - Task is pending (default)
- `in_progress` - Task is currently being worked on
- `completed` - Task is finished
- `blocked` - Task is blocked/cannot proceed

### Priority
- `low` - Low priority task
- `medium` - Medium priority task (default)
- `high` - High priority task
- `urgent` - Urgent task requiring immediate attention

## Database Schema

Tasks are stored with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Auto-incrementing primary key |
| title | TEXT | Task title (required) |
| description | TEXT | Task description |
| status | TEXT | Task status (constrained) |
| priority | TEXT | Task priority (constrained) |
| created_at | TIMESTAMP | Automatic creation timestamp |
| updated_at | TIMESTAMP | Automatic update timestamp |

## Programmatic Usage

You can also use the TaskAgent class in your Python code:

```python
from task_skill import TaskAgent

# Initialize agent
agent = TaskAgent()

# Add a task
result = agent.add_task(
    title="Implement new feature",
    description="Add user authentication",
    status="pending",
    priority="high"
)
print(f"Created task ID: {result['task_id']}")

# List all tasks
result = agent.list_tasks()
for task in result['tasks']:
    print(f"{task['id']}: {task['title']} [{task['status']}]")

# Update a task
agent.update_task(1, status="in_progress")

# Get specific task
result = agent.get_task(1)
if result['success']:
    print(result['task'])

# Delete a task
agent.delete_task(5)

# Close connection when done
agent.close()
```

## Database Location

By default, the database is stored as `tasks.db` in the current directory. The database file is created automatically on first use.

## Examples

### Typical Workflow

```bash
# Add some tasks
python task_skill.py add "Review pull requests" --priority high
python task_skill.py add "Update documentation" --priority medium
python task_skill.py add "Fix bug #123" "Memory leak in auth module" --priority urgent

# List all pending tasks
python task_skill.py list --status pending

# Start working on a task
python task_skill.py update 1 --status in_progress

# Complete a task
python task_skill.py update 1 --status completed

# List high priority tasks
python task_skill.py list --priority high

# View task details
python task_skill.py get 3

# Delete completed tasks
python task_skill.py delete 1
```

## License

MIT License - feel free to use and modify as needed!
