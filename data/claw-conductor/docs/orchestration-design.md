# Claw Conductor Orchestration System - Architecture Design

**Version:** 2.1.0
**Date:** 2026-02-01
**Status:** Production Ready

---

## Overview

Extends Claw Conductor from single-task routing to full autonomous orchestration with:
- Task decomposition
- Dependency analysis
- Parallel execution
- Multi-project support
- Result consolidation

---

## System Architecture

```
Discord Request
    ↓
┌─────────────────────────────────────────────────────────┐
│              Orchestrator (Main Controller)              │
├─────────────────────────────────────────────────────────┤
│  1. Request Analysis                                     │
│  2. Project Initialization                               │
│  3. Task Decomposition                                   │
│  4. Dependency Graph                                     │
│  5. Task Scheduling                                      │
│  6. Worker Pool Management                               │
│  7. Result Consolidation                                 │
│  8. Discord Reporting                                    │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│           Task Decomposition Engine                      │
├─────────────────────────────────────────────────────────┤
│  • Uses Perplexity or primary model                      │
│  • Analyzes request complexity                           │
│  • Breaks into independent subtasks                      │
│  • Assigns complexity (1-5) and category                 │
│  • Identifies dependencies                               │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│                Router (Existing)                         │
├─────────────────────────────────────────────────────────┤
│  • Scores models for each task                           │
│  • Routes to best match                                  │
│  • Handles fallback                                      │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│              Worker Pool (New)                           │
├─────────────────────────────────────────────────────────┤
│  • Max 5 concurrent tasks globally                       │
│  • Spawns OpenClaw Task tool calls                       │
│  • Tracks task state (pending/running/completed/failed)  │
│  • Respects file conflicts                               │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│           Project Manager (New)                          │
├─────────────────────────────────────────────────────────┤
│  • Creates /root/projects/{name}/                        │
│  • Initializes git repo                                  │
│  • Creates GitHub repo                                   │
│  • Registers OpenClaw agent                              │
│  • Tracks project state                                  │
└─────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────┐
│         Result Consolidator (New)                        │
├─────────────────────────────────────────────────────────┤
│  • Merges task outputs                                   │
│  • Resolves file conflicts                               │
│  • Runs tests                                            │
│  • Commits to git                                        │
│  • Pushes to GitHub                                      │
└─────────────────────────────────────────────────────────┘
    ↓
Discord Completion Report
```

---

## Data Structures

### Project State

```python
{
    "project_id": "my-project-20260201",
    "name": "my-project",
    "workspace": "/root/projects/my-project",
    "github_repo": "{user}/my-project",
    "status": "in_progress",  # pending, in_progress, completed, failed
    "created_at": "2026-02-01T03:00:00Z",
    "tasks": [...],  # List of Task objects
    "dependencies": {...},  # Dependency graph
    "progress": {
        "total_tasks": 7,
        "completed": 3,
        "failed": 0,
        "in_progress": 2,
        "pending": 2
    }
}
```

### Task Object

```python
{
    "task_id": "task-001",
    "description": "Design and implement database schema",
    "category": "database-operations",
    "complexity": 4,
    "assigned_model": "mistral-devstral-2512",
    "status": "completed",  # pending, running, completed, failed
    "dependencies": [],  # List of task_ids that must complete first
    "file_targets": ["src/db/schema.sql", "src/models/*"],
    "result": {
        "success": true,
        "files_modified": ["src/db/schema.sql", "src/models/user.py"],
        "execution_time": 240,  # seconds
        "error": null
    },
    "started_at": "2026-02-01T03:05:00Z",
    "completed_at": "2026-02-01T03:09:00Z"
}
```

### Worker State

```python
{
    "worker_id": "worker-1",
    "status": "busy",  # idle, busy
    "current_task": "task-001",
    "current_project": "my-project",
    "started_at": "2026-02-01T03:05:00Z"
}
```

---

## Component Details

### 1. Task Decomposition Engine

**Purpose:** Break complex request into actionable subtasks

**Input:** User request string
**Output:** List of Task objects with dependencies

**Algorithm:**
1. Use Perplexity (if available) or primary model to analyze request
2. Prompt template:
   ```
   Analyze this software development request and break it into independent subtasks.

   Request: "{user_request}"

   For each subtask, provide:
   - Description (what needs to be done)
   - Category (from: {list of 23 categories})
   - Complexity (1-5 scale)
   - Dependencies (which other subtasks must complete first)
   - File targets (which files/directories will be created/modified)

   Output as JSON array.
   ```
3. Parse JSON response
4. Validate task structure
5. Build dependency graph

**Example Output:**
```json
[
  {
    "description": "Design database schema for users, jobs, and locations",
    "category": "database-operations",
    "complexity": 4,
    "dependencies": [],
    "file_targets": ["src/db/schema.sql", "src/models/*"]
  },
  {
    "description": "Implement JWT authentication system",
    "category": "security-fixes",
    "complexity": 4,
    "dependencies": ["task-001"],  # Needs database first
    "file_targets": ["src/auth/*", "src/middleware/auth.js"]
  }
]
```

### 2. Project Manager

**Purpose:** Create and initialize project workspace

**Functions:**

```python
def create_project(project_name: str, description: str):
    """
    1. Create /root/projects/{project_name}/
    2. Initialize git repo
    3. Create GitHub repo via gh CLI
    4. Push initial commit
    5. Register OpenClaw agent in openclaw.json
    6. Return project_id and workspace path
    """

def get_project_state(project_id: str):
    """Load project state from disk"""

def update_project_state(project_id: str, state: dict):
    """Save project state to disk"""
```

**State Storage:**
```
/root/projects/{project_name}/
├── .claw-conductor/
│   ├── project-state.json      # Project metadata
│   ├── task-queue.json         # Current task queue
│   └── execution-log.json      # Execution history
├── .git/
└── ...
```

### 3. Worker Pool

**Purpose:** Execute tasks in parallel with global limit

**Key Features:**
- Global max 5 workers across ALL projects
- File conflict detection (tasks touching same files run sequentially)
- Dependency-aware scheduling
- Automatic retry with fallback

**Algorithm:**
```python
class WorkerPool:
    def __init__(self, max_workers=5):
        self.max_workers = max_workers
        self.workers = []  # Active workers
        self.task_queue = []  # Pending tasks

    def schedule_task(self, task, project):
        """Add task to queue, start if workers available"""
        self.task_queue.append((task, project))
        self._try_start_next()

    def _try_start_next(self):
        """Start next task if worker available and no conflicts"""
        if len(self.workers) >= self.max_workers:
            return

        for task, project in self.task_queue:
            if self._can_execute(task, project):
                self._execute_task(task, project)
                self.task_queue.remove((task, project))
                break

    def _can_execute(self, task, project):
        """Check if task can run (dependencies met, no file conflicts)"""
        # Check dependencies
        for dep_id in task['dependencies']:
            if not self._is_task_complete(dep_id, project):
                return False

        # Check file conflicts
        for worker in self.workers:
            if worker['project'] == project['project_id']:
                if self._files_overlap(task['file_targets'],
                                      worker['task']['file_targets']):
                    return False
        return True

    def _execute_task(self, task, project):
        """Spawn OpenClaw Task tool with assigned model"""
        # Use router to get model
        model_id, details = router.route_task_with_fallback(task)

        # Create worker
        worker = {
            'worker_id': generate_id(),
            'task': task,
            'project': project['project_id'],
            'model': model_id,
            'started_at': now()
        }
        self.workers.append(worker)

        # Execute via OpenClaw Task tool (async)
        result = spawn_openclaw_task(
            model=model_id,
            workspace=project['workspace'],
            prompt=task['description'],
            callback=lambda r: self._on_task_complete(worker, r)
        )
```

### 4. Result Consolidation

**Purpose:** Merge parallel task outputs into coherent project

**Steps:**
1. Wait for all tasks to complete
2. Check for merge conflicts
3. Run tests (if test files exist)
4. Commit all changes with conventional commit message
5. Push to GitHub
6. Update project state to "completed"

**Conflict Resolution:**
```python
def consolidate_results(project):
    """
    1. Get all completed task results
    2. Check git status for conflicts
    3. If conflicts, use primary model to resolve
    4. Run tests: pytest, npm test, etc.
    5. If tests fail, mark project as needs_review
    6. Commit with message: "feat: {project_name} - {task_count} tasks completed"
    7. Push to GitHub
    """
```

### 5. Discord Integration

**Purpose:** Real-time progress updates

**Events to Report:**
- Project started
- Task completed (with progress: 3/7 tasks)
- Task failed (with error summary)
- File conflict detected
- Project completed (with GitHub link)
- Project failed (with debugging suggestions)

**Message Format:**
```
🚀 Project Started: my-project
📋 Decomposed into 7 tasks
⚡ Executing in parallel (max 5 concurrent)

✅ Task 1/7: Database schema (Mistral) - Completed in 4m
🔄 Task 2/7: Authentication (Mistral) - In progress
🔄 Task 3/7: Customer UI (Devstral) - In progress
⏳ Task 4/7: Driver dashboard (Devstral) - Queued
...

✅ All tasks completed!
📦 Committed and pushed to GitHub
🔗 https://github.com/{user}/dispatch-suite
```

---

## File Structure

```
claw-conductor/
├── scripts/
│   ├── router.py                    # Existing routing logic
│   ├── orchestrator.py              # NEW: Main orchestration controller
│   ├── decomposer.py                # NEW: Task decomposition
│   ├── project_manager.py           # NEW: Project initialization
│   ├── worker_pool.py               # NEW: Parallel execution
│   ├── consolidator.py              # NEW: Result merging
│   └── utils/
│       ├── dependency_graph.py      # NEW: Dependency analysis
│       ├── file_conflict.py         # NEW: File conflict detection
│       └── discord_reporter.py      # NEW: Discord integration
├── config/
│   └── agent-registry.json          # Existing model config
└── SKILL.md                         # Updated entry point
```

---

## Integration with OpenClaw

Claw Conductor will be invoked as an OpenClaw skill:

```
User in Discord: @OpenClaw use claw-conductor to build a dispatch system

OpenClaw loads skill → calls orchestrator.py → returns when complete
```

The orchestrator will use OpenClaw's Task tool to spawn work:

```python
from openclaw import Task

# Spawn subtask execution
Task(
    description=f"Execute: {task['description']}",
    prompt=f"""
    You are working on project: {project['name']}
    Workspace: {project['workspace']}

    Task: {task['description']}
    Category: {task['category']}
    Complexity: {task['complexity']}

    Files to create/modify: {task['file_targets']}

    Complete this task and commit your changes.
    """,
    subagent_type="general-purpose",
    model=task['assigned_model']
)
```

---

## Implementation Phases

### Phase 2a: Core Components (Week 1)
- [ ] orchestrator.py - Main controller
- [ ] decomposer.py - Task decomposition with AI
- [ ] project_manager.py - Project initialization
- [ ] dependency_graph.py - Dependency analysis

### Phase 2b: Execution (Week 1)
- [ ] worker_pool.py - Parallel execution
- [ ] file_conflict.py - Conflict detection
- [ ] Integration with existing router.py

### Phase 2c: Consolidation (Week 2)
- [ ] consolidator.py - Result merging
- [ ] Git operations and conflict resolution
- [ ] Test execution

### Phase 2d: Communication (Week 2)
- [ ] discord_reporter.py - Progress updates
- [ ] Error handling and debugging
- [ ] Update SKILL.md with usage examples

### Phase 2e: Testing (Week 2)
- [ ] Simple test: "Build calculator"
- [ ] Complex test: "Build dispatch system"
- [ ] Concurrent test: Two projects
- [ ] Performance optimization

---

## Success Metrics

- [ ] Can decompose complex request into 5+ subtasks
- [ ] Executes tasks in parallel (verify max 5 concurrent)
- [ ] Handles dependencies correctly (database before auth)
- [ ] Detects and avoids file conflicts
- [ ] Consolidates results without merge conflicts
- [ ] Commits to git with meaningful messages
- [ ] Creates GitHub repo and pushes
- [ ] Reports progress to Discord
- [ ] Handles 2+ concurrent projects
- [ ] Falls back gracefully on errors

---

*Next: Begin implementation of orchestrator.py*
