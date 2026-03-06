---
name: Task Planner and Validator - Skill Guide
description: This skill provides a secure, step-by-step task management system
  for AI Agents.
---

# Task Planner and Validator - Skill Guide

This skill provides a secure, step-by-step task management system for AI Agents.

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/cerbug45/task-planner-validator.git
cd task-planner-validator

# That's it! No dependencies needed - pure Python standard library
```

## Verify Installation

```bash
# Run tests
python test_basic.py

# Run examples
python examples.py
```

## Basic Usage

### 1. Import and Initialize

```python
from task_planner import TaskPlanner

# Create planner
planner = TaskPlanner(auto_approve=False)
```

### 2. Define Your Executor

```python
def my_executor(action: str, parameters: dict):
    """Your custom execution logic"""
    if action == "fetch_data":
        # Fetch data from API, database, etc.
        return {"data": [1, 2, 3]}
    elif action == "process_data":
        # Process the data
        return {"processed": True}
    else:
        return {"status": "completed"}
```

### 3. Create a Plan

```python
steps = [
    {
        "description": "Fetch user data",
        "action": "fetch_data",
        "parameters": {"source": "database"},
        "expected_output": "List of users"
    },
    {
        "description": "Process users",
        "action": "process_data",
        "parameters": {"validation": True},
        "expected_output": "Processed data"
    }
]

plan = planner.create_plan(
    title="Data Processing Pipeline",
    description="Fetch and process user data",
    steps=steps
)
```

### 4. Validate and Execute

```python
# Validate
is_valid, warnings = planner.validate_plan(plan)
if warnings:
    print("Warnings:", warnings)

# Approve
planner.approve_plan(plan, approved_by="admin")

# Execute
success, results = planner.execute_plan(plan, my_executor)

# Get summary
summary = planner.get_execution_summary(plan)
print(f"Progress: {summary['progress_percentage']}%")
```

## Key Features

### Safety Validation

Automatically detects dangerous operations:

```python
steps = [
    {
        "description": "Delete old files",
        "action": "delete_files",  # ⚠️ Dangerous!
        "parameters": {"path": "/data/old"},
        "safety_check": True,  # System will warn
        "rollback_possible": False  # Cannot undo
    }
]
```

### Dry Run Mode

Test without executing:

```python
success, results = planner.execute_plan(
    plan, 
    my_executor, 
    dry_run=True  # Simulate only
)
```

### Save and Load Plans

Persist plans for reuse:

```python
# Save
planner.save_plan(plan, "my_plan.json")

# Load later
loaded_plan = planner.load_plan("my_plan.json")

# Verify integrity
if loaded_plan.verify_integrity():
    planner.execute_plan(loaded_plan, my_executor)
```

### Error Handling

Control error behavior:

```python
success, results = planner.execute_plan(
    plan,
    my_executor,
    stop_on_error=False  # Continue on failures
)

# Check results
for result in results:
    if not result['success']:
        print(f"Step {result['order']} failed: {result['error']}")
```

## Step Configuration

Each step supports these parameters:

```python
{
    "description": str,          # Required: Human-readable description
    "action": str,               # Required: Action identifier
    "parameters": dict,          # Required: Action parameters
    "expected_output": str,      # Required: Expected result
    "safety_check": bool,        # Optional: Enable validation (default: True)
    "rollback_possible": bool,   # Optional: Can be rolled back (default: True)
    "max_retries": int          # Optional: Retry attempts (default: 3)
}
```

## Common Use Cases

### API Orchestration

```python
steps = [
    {
        "description": "Authenticate",
        "action": "api_auth",
        "parameters": {"service": "github"},
        "expected_output": "Auth token"
    },
    {
        "description": "Fetch data",
        "action": "api_fetch",
        "parameters": {"endpoint": "/repos"},
        "expected_output": "Repository list"
    }
]
```

### Data Pipeline

```python
steps = [
    {
        "description": "Extract data",
        "action": "extract",
        "parameters": {"source": "database"},
        "expected_output": "Raw data"
    },
    {
        "description": "Transform data",
        "action": "transform",
        "parameters": {"rules": ["normalize", "validate"]},
        "expected_output": "Clean data"
    },
    {
        "description": "Load data",
        "action": "load",
        "parameters": {"destination": "warehouse"},
        "expected_output": "Success confirmation"
    }
]
```

### System Automation

```python
steps = [
    {
        "description": "Backup database",
        "action": "backup",
        "parameters": {"target": "postgres"},
        "expected_output": "Backup file path",
        "rollback_possible": True
    },
    {
        "description": "Update schema",
        "action": "migrate",
        "parameters": {"version": "2.0"},
        "expected_output": "Migration complete",
        "rollback_possible": True
    },
    {
        "description": "Verify integrity",
        "action": "verify",
        "parameters": {"checks": ["all"]},
        "expected_output": "All checks passed"
    }
]
```

## Best Practices

### 1. Always Validate First

```python
is_valid, warnings = planner.validate_plan(plan)
if not is_valid:
    print("Plan validation failed!")
    for warning in warnings:
        print(f"  - {warning}")
    exit(1)
```

### 2. Use Descriptive Names

```python
# Good ✅
{
    "description": "Fetch active users from PostgreSQL production database",
    "action": "fetch_active_users_postgres_prod",
    ...
}

# Bad ❌
{
    "description": "Get data",
    "action": "get",
    ...
}
```

### 3. Mark Dangerous Operations

```python
{
    "description": "Delete temporary files older than 30 days",
    "action": "cleanup_temp_files",
    "parameters": {"age_days": 30, "path": "/tmp"},
    "safety_check": True,      # ⚠️ Will trigger warnings
    "rollback_possible": False  # ⚠️ Cannot undo!
}
```

### 4. Test with Dry Run

```python
# Always test first
success, results = planner.execute_plan(plan, my_executor, dry_run=True)

if success:
    # Now run for real
    success, results = planner.execute_plan(plan, my_executor, dry_run=False)
```

### 5. Handle Errors Gracefully

```python
def safe_executor(action: str, parameters: dict):
    try:
        result = execute_action(action, parameters)
        return result
    except Exception as e:
        logging.error(f"Failed to execute {action}: {e}")
        raise  # Re-raise to let planner handle it
```

## Advanced Features

### Auto-Approve for Automation

```python
# Skip manual approval for automated workflows
planner = TaskPlanner(auto_approve=True)
```

### Checkpoint System

```python
# Checkpoints are automatically created for rollback-capable steps
# Access checkpoint history
checkpoints = planner.executor.checkpoint_stack
```

### Execution History

```python
# View execution history
history = planner.executor.execution_history
for entry in history:
    print(f"{entry['timestamp']}: {entry['step_id']} - {entry['status']}")
```

### Custom Validation Rules

```python
# Add custom validation to SafetyValidator
planner.safety_validator.dangerous_operations.append('my_dangerous_op')
planner.safety_validator.sensitive_paths.append('/my/sensitive/path')
```

## Troubleshooting

### "Plan must be approved before execution"

```python
# Solution: Approve the plan first
planner.approve_plan(plan, approved_by="admin")
# Or use auto-approve mode
planner = TaskPlanner(auto_approve=True)
```

### Safety validation warnings

```python
# Review warnings and ensure operations are intentional
is_valid, warnings = planner.validate_plan(plan)
for warning in warnings:
    print(warning)

# If operations are safe, approve anyway
if is_valid:  # Still valid, just warnings
    planner.approve_plan(plan)
```

### Steps executing out of order

```python
# Ensure order values are sequential
steps[0]['order'] = 1
steps[1]['order'] = 2
steps[2]['order'] = 3
```

## File Structure

```
task-planner-validator/
├── task_planner.py      # Main library
├── examples.py          # Usage examples
├── test_basic.py        # Test suite
├── README.md            # Full documentation
├── QUICKSTART.md        # Quick start guide
├── API.md              # API reference
├── SKILL.md            # This file
└── LICENSE              # MIT License
```

## Requirements

- Python 3.8 or higher
- No external dependencies!

## Testing

```bash
# Run basic tests
python test_basic.py

# Run examples
python examples.py

# Both should show "✅ ALL TESTS PASSED"
```

## Getting Help

- 📖 Read full documentation in [README.md](README.md)
- 🚀 Check [QUICKSTART.md](QUICKSTART.md) for quick examples
- 📚 See [API.md](API.md) for complete API reference
- 💡 Browse [examples.py](examples.py) for real code
- 🐛 Report issues on GitHub

## License

MIT License - see [LICENSE](LICENSE) file

## Author

**cerbug45**
- GitHub: [@cerbug45](https://github.com/cerbug45)

---

⭐ If you find this useful, star the repository on GitHub!
