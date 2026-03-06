# Quick Start Guide

Get started with Task Planner and Validator in 5 minutes!

## Installation

```bash
git clone https://github.com/cerbug45/task-planner-validator.git
cd task-planner-validator
```

No dependencies needed! Pure Python standard library.

## Your First Task Plan

Create a file `my_first_plan.py`:

```python
from task_planner import TaskPlanner

# 1. Create a planner
planner = TaskPlanner(auto_approve=False)

# 2. Define your executor function
def my_executor(action: str, parameters: dict):
    """
    This function executes each step.
    Replace this with your actual logic.
    """
    print(f"Executing: {action}")
    print(f"Parameters: {parameters}")
    
    # Your execution logic here
    if action == "fetch_users":
        # Simulate API call
        return {"users": ["Alice", "Bob", "Charlie"]}
    elif action == "process_users":
        # Simulate data processing
        return {"processed": True, "count": 3}
    else:
        return {"status": "completed"}

# 3. Define steps
steps = [
    {
        "description": "Fetch users from database",
        "action": "fetch_users",
        "parameters": {"limit": 100},
        "expected_output": "List of users"
    },
    {
        "description": "Process user data",
        "action": "process_users",
        "parameters": {"validation": True},
        "expected_output": "Processed users"
    },
    {
        "description": "Send notification",
        "action": "send_notification",
        "parameters": {"message": "Processing complete"},
        "expected_output": "Notification sent"
    }
]

# 4. Create the plan
plan = planner.create_plan(
    title="User Data Processing",
    description="Fetch and process user data",
    steps=steps
)

print(f"Created plan: {plan.task_id}")

# 5. Validate the plan
is_valid, warnings = planner.validate_plan(plan)
print(f"Valid: {is_valid}")
if warnings:
    print("Warnings:", warnings)

# 6. Approve the plan
if planner.approve_plan(plan, approved_by="admin"):
    print("Plan approved!")

# 7. Execute the plan
success, results = planner.execute_plan(plan, my_executor)

print(f"\nExecution {'succeeded' if success else 'failed'}!")

# 8. Get summary
summary = planner.get_execution_summary(plan)
print(f"\nProgress: {summary['progress_percentage']:.1f}%")
print(f"Completed: {summary['completed']}/{summary['total_steps']} steps")
```

Run it:
```bash
python my_first_plan.py
```

## Common Patterns

### Pattern 1: Safe File Operations

```python
steps = [
    {
        "description": "Backup important files",
        "action": "backup_files",
        "parameters": {"source": "/data", "dest": "/backup"},
        "expected_output": "Backup created",
        "rollback_possible": True  # Can be undone
    },
    {
        "description": "Clean temporary files",
        "action": "delete_temp",
        "parameters": {"path": "/tmp/*.temp"},
        "expected_output": "Temp files removed",
        "rollback_possible": False,  # Cannot be undone
        "safety_check": True  # Will trigger warning
    }
]
```

### Pattern 2: API Orchestration

```python
steps = [
    {
        "description": "Authenticate with API",
        "action": "api_auth",
        "parameters": {"service": "github"},
        "expected_output": "Auth token"
    },
    {
        "description": "Fetch repositories",
        "action": "api_fetch",
        "parameters": {"endpoint": "/repos", "token": "${step1.result}"},
        "expected_output": "Repository list"
    },
    {
        "description": "Process each repo",
        "action": "process_repos",
        "parameters": {"repos": "${step2.result}"},
        "expected_output": "Processed data"
    }
]
```

### Pattern 3: Error Handling

```python
# Continue on errors
success, results = planner.execute_plan(
    plan, 
    my_executor,
    stop_on_error=False  # Keep going even if steps fail
)

# Check which steps failed
for result in results:
    if not result['success']:
        print(f"Step {result['order']} failed: {result['error']}")
```

### Pattern 4: Dry Run Testing

```python
# Test without executing
success, results = planner.execute_plan(
    plan,
    my_executor,
    dry_run=True  # Simulate execution
)

print("Dry run completed - no changes made")
```

### Pattern 5: Save and Reuse Plans

```python
# Save plan
planner.save_plan(plan, "my_plan.json")

# Load later
loaded_plan = planner.load_plan("my_plan.json")

# Verify integrity
if loaded_plan.verify_integrity():
    planner.execute_plan(loaded_plan, my_executor)
```

## Best Practices

### 1. Always Define Expected Output
```python
{
    "description": "Fetch data",
    "action": "fetch",
    "parameters": {"url": "https://api.example.com/data"},
    "expected_output": "JSON array of user objects"  # Be specific!
}
```

### 2. Use Safety Checks for Dangerous Operations
```python
{
    "description": "Delete old logs",
    "action": "delete_logs",
    "parameters": {"older_than": "30days"},
    "safety_check": True,  # System will warn
    "rollback_possible": False  # Cannot undo!
}
```

### 3. Handle Step Dependencies
```python
def my_executor(action, parameters):
    if action == "step2" and "step1_result" in parameters:
        # Use result from step 1
        step1_data = parameters["step1_result"]
        # Process it...
```

### 4. Use Descriptive Names
```python
# Good
{
    "description": "Fetch active users from PostgreSQL database",
    "action": "fetch_active_users_postgres",
    ...
}

# Bad
{
    "description": "Get data",
    "action": "get",
    ...
}
```

### 5. Log Everything
```python
import logging

def my_executor(action, parameters):
    logging.info(f"Starting {action}")
    try:
        result = perform_action(action, parameters)
        logging.info(f"Completed {action}: {result}")
        return result
    except Exception as e:
        logging.error(f"Failed {action}: {e}")
        raise
```

## Troubleshooting

### Problem: "Plan must be approved before execution"
**Solution**: Call `planner.approve_plan(plan)` before executing, or use `auto_approve=True`

### Problem: Safety validation fails
**Solution**: Review warnings, ensure `safety_check=True` only for safe operations

### Problem: Steps not executing in order
**Solution**: Check that step `order` values are sequential (1, 2, 3...)

### Problem: Can't load saved plan
**Solution**: Verify JSON file exists and is valid, check file permissions

## Next Steps

- Read the [full README](README.md) for advanced features
- Check [examples.py](examples.py) for more use cases
- Run tests with `python test_basic.py`
- Customize `SafetyValidator` for your needs

## Need Help?

- 📖 Read the documentation in [README.md](README.md)
- 💻 Check [examples.py](examples.py) for code samples
- 🐛 Report issues on GitHub
- ⭐ Star the repo if you find it useful!
