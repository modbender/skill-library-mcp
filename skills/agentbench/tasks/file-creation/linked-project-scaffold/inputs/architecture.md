# TaskFlow — Multi-Module Python Project Architecture

## Overview

TaskFlow is a task management library with 4 interdependent modules. The modules form a layered architecture where higher layers depend on lower ones, but never the reverse.

**Package name**: `taskflow`
**Python version**: 3.9+
**No external dependencies** — standard library only

---

## Module Dependency Graph

```
utils (no dependencies)
  ^
  |
models (imports from utils)
  ^       ^
  |       |
services  |  (imports from models AND utils)
  ^       |
  |       |
api ------+  (imports from services AND models)
```

---

## Module Specifications

### 1. `taskflow/utils/`

**Purpose**: Shared utility functions used across all other modules.

**Files**:
- `__init__.py` — exports public functions
- `validators.py` — input validation helpers
- `formatters.py` — string/date formatting utilities
- `constants.py` — shared constants (status codes, defaults)

**Public API**:
- `validate_email(email: str) -> bool`
- `validate_priority(priority: int) -> bool` — must be 1-5
- `format_date(dt: datetime) -> str` — ISO 8601 format
- `format_duration(seconds: int) -> str` — human-readable duration
- `STATUS_PENDING = "pending"`
- `STATUS_ACTIVE = "active"`
- `STATUS_COMPLETED = "completed"`
- `DEFAULT_PRIORITY = 3`

### 2. `taskflow/models/`

**Purpose**: Data model classes representing core domain objects.

**Files**:
- `__init__.py` — exports model classes
- `task.py` — Task model
- `project.py` — Project model
- `user.py` — User model

**Public API**:
- `Task` class with fields: `id: str`, `title: str`, `description: str`, `status: str`, `priority: int`, `assignee_id: str`, `project_id: str`
  - Must import and use `STATUS_PENDING` and `DEFAULT_PRIORITY` from utils for defaults
  - Must import and use `validate_priority` from utils in the constructor
- `Project` class with fields: `id: str`, `name: str`, `owner_id: str`, `task_ids: list[str]`
- `User` class with fields: `id: str`, `name: str`, `email: str`
  - Must import and use `validate_email` from utils in the constructor

### 3. `taskflow/services/`

**Purpose**: Business logic layer — orchestrates operations on models.

**Files**:
- `__init__.py` — exports service classes
- `task_service.py` — task CRUD and workflow operations
- `project_service.py` — project management operations

**Public API**:
- `TaskService` class:
  - `create_task(title: str, project_id: str, assignee_id: str, priority: int = DEFAULT_PRIORITY) -> Task`
    - Must import `Task` from `taskflow.models`
    - Must import `DEFAULT_PRIORITY` from `taskflow.utils`
  - `complete_task(task: Task) -> Task`
    - Must import `STATUS_COMPLETED` from `taskflow.utils`
  - `get_tasks_by_status(tasks: list[Task], status: str) -> list[Task]`
- `ProjectService` class:
  - `create_project(name: str, owner_id: str) -> Project`
    - Must import `Project` from `taskflow.models`
  - `add_task_to_project(project: Project, task: Task) -> Project`

### 4. `taskflow/api/`

**Purpose**: Public API layer — provides the high-level interface for consumers.

**Files**:
- `__init__.py` — exports API classes
- `task_api.py` — task-related API operations
- `project_api.py` — project-related API operations

**Public API**:
- `TaskAPI` class:
  - `__init__(self)` — creates a `TaskService` instance
    - Must import `TaskService` from `taskflow.services`
  - `create_task(title: str, project_id: str, assignee_id: str) -> dict`
    - Creates a task via service, returns dict representation
    - Must reference `Task` from `taskflow.models` for type context
  - `list_tasks(tasks: list, status: str = None) -> list[dict]`
- `ProjectAPI` class:
  - `__init__(self)` — creates a `ProjectService` instance
    - Must import `ProjectService` from `taskflow.services`
  - `create_project(name: str, owner_id: str) -> dict`
    - Must reference `Project` from `taskflow.models`

---

## Import Rules

1. `utils` imports nothing from taskflow (leaf module)
2. `models` imports only from `utils`
3. `services` imports from `models` and `utils` (never from `api`)
4. `api` imports from `services` and `models` (never from `utils` directly)
5. No circular imports allowed

---

## Project Metadata (pyproject.toml)

```toml
[project]
name = "taskflow"
version = "0.1.0"
description = "A multi-module task management library"
requires-python = ">=3.9"
```
