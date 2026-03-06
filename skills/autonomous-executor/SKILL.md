---
name: Autonomous Executor
description: Self-healing, error-recovering task execution with full autonomy.
---

# Autonomous Executor

Self-healing, error-recovering task execution with full autonomy.

## Features

- **Automatic Error Recovery**: Categorizes errors and applies targeted recovery strategies
- **Exponential Backoff**: Smart retry timing with configurable limits
- **Self-Healing**: Auto-installs missing dependencies, creates missing resources
- **Checkpoint/Resume**: Save progress for resumable overnight tasks
- **MongoDB Logging**: Persistent execution logs for monitoring
- **Capability Awareness**: Full knowledge of all OpenClaw skills and tools
- **Overnight Batch Processing**: Queue tasks to run while you sleep

## Error Categories & Recovery

| Category | Auto-Recovery |
|----------|---------------|
| Network | Wait and retry with backoff, check connectivity |
| Auth | Refresh credentials, prompt re-auth |
| Rate Limit | Wait with Retry-After header, exponential backoff |
| Resource | Create missing files/directories, clean temp |
| Validation | Auto-fix input, use defaults |
| Dependency | pip install missing modules |
| Browser | Restart Playwright context, reduce concurrency |
| API | Retry with backoff, try alternate endpoints |

## Quick Usage

```python
from autonomous_executor.executor import AutoExec

# Deploy a project autonomously
result = AutoExec.deploy("my-portfolio", "portfolio", "My awesome portfolio")

# Run any function with auto-recovery
result = AutoExec.run(my_function, arg1, arg2, _max_retries=5)

# Check overnight report
report = AutoExec.report()

# List all capabilities
print(AutoExec.caps())
```

## Overnight Batch Execution

```python
from autonomous_executor.overnight import Overnight

# Queue tasks to run overnight
Overnight.deploy("my-portfolio", "portfolio", description="Overnight deploy")
Overnight.deploy("client-site", "landing", description="Client landing page")
Overnight.research("AI trends 2025")

# Queue custom functions
Overnight.run(my_backup_function, "/data", _name="Backup Data")

# Start overnight run
summary = Overnight.start()

# Next morning, check report
print(Overnight.report())
```

## Decorator Usage

```python
from autonomous_executor.executor import autonomous

@autonomous(max_retries=5, task_name="Critical Task")
def my_critical_function():
    # This will auto-recover from errors
    return do_something()
```

## Full API

### AutonomousExecutor

```python
from autonomous_executor.executor import AutonomousExecutor

executor = AutonomousExecutor(user="ishaan")

# Execute any function
result = executor.execute(
    task_fn=my_function,
    args=(arg1, arg2),
    kwargs={"key": "value"},
    task_name="My Task",
    max_retries=5,
    timeout=300  # 5 minutes
)

# Run project pipeline
result = executor.run_project_pipeline({
    "name": "my-app",
    "type": "nextjs",
    "description": "My Next.js app",
    "extra": {"features": ["dark_mode", "auth"]}
})

# Run research
result = executor.run_research_pipeline("quantum computing", depth="deep")

# Get execution history
history = executor.get_execution_history(limit=20)

# Get overnight report
report = executor.get_overnight_report()
```

## Example Output

```
[14:23:45] 🚀 Starting task: Deploy Portfolio
[14:23:45]    Max retries: 5, Timeout: 0s
[14:23:45]    Available capabilities: 15 skills
[14:23:45] ⚡ Attempt 1/5...
[14:23:47] ❌ Attempt 1 failed: ConnectionError: Network timeout
[14:23:47]    Error category: network
[14:23:47] 🔧 Trying recovery: wait_and_retry
[14:23:47] ⏳ Waiting 4.0s before retry...
[14:23:51] ⚡ Attempt 2/5...
[14:24:03] ✅ Task completed successfully in 12.1s
```

## MongoDB Collections

- `task_records`: Complete task execution records
- `task_checkpoints`: Checkpoint data for resumable tasks
- `execution_logs`: Real-time execution logs
