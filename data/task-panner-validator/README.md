# Task Planner and Validator

A secure, step-by-step task management system designed for AI Agents to safely plan, validate, and execute complex multi-step tasks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Features

- **✅ Step-by-Step Planning**: Break down complex tasks into manageable, ordered steps
- **🔒 Safety Validation**: Built-in security checks for dangerous operations
- **🔄 Rollback Support**: Checkpoint system for reverting failed operations
- **📝 Plan Persistence**: Save and load plans in JSON format
- **🎨 Integrity Verification**: SHA-256 checksums to prevent tampering
- **⚡ Execution Control**: Dry-run mode, auto-approve, and stop-on-error options
- **📊 Progress Tracking**: Real-time status updates and execution summaries
- **🔍 Detailed Logging**: Comprehensive logging for debugging and auditing

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/cerbug45/task-planner-validator.git
cd task-planner-validator

# No additional dependencies required - uses only Python standard library!
```

### Basic Usage

```python
from task_planner import TaskPlanner

# Create a planner
planner = TaskPlanner(auto_approve=False)

# Define your steps
steps = [
    {
        "description": "Fetch user data from API",
        "action": "fetch_data",
        "parameters": {"endpoint": "/api/users", "method": "GET"},
        "expected_output": "List of user objects",
        "safety_check": True,
        "rollback_possible": True
    },
    {
        "description": "Process and validate data",
        "action": "process_data",
        "parameters": {"validation_rules": ["email", "age"]},
        "expected_output": "Validated user data",
        "safety_check": True,
        "rollback_possible": True
    }
]

# Create a plan
plan = planner.create_plan(
    title="User Data Processing Pipeline",
    description="Fetch, validate, and save user data",
    steps=steps
)

# Validate the plan
is_valid, warnings = planner.validate_plan(plan)
if warnings:
    print("Warnings:", warnings)

# Approve the plan
planner.approve_plan(plan, approved_by="admin")

# Execute the plan
def my_executor(action, parameters):
    # Your execution logic here
    print(f"Executing {action} with {parameters}")
    return {"status": "success"}

success, results = planner.execute_plan(plan, my_executor)
```

## 📚 Core Concepts

### Task Plan
A **TaskPlan** represents a complete workflow with:
- Unique task ID
- Title and description
- Ordered list of steps
- Status tracking (pending, approved, running, completed, failed)
- Integrity checksum

### Step
Each **Step** contains:
- Unique step ID and order
- Description and action name
- Parameters dictionary
- Expected output
- Safety and rollback flags
- Status tracking
- Execution results and errors

### Safety Validation
The **SafetyValidator** checks for:
- Dangerous operations (delete, remove, format, etc.)
- Sensitive system paths (/etc, /sys, C:\Windows, etc.)
- Missing parameters
- Step ordering issues
- Plan integrity violations

## 🔧 Advanced Features

### Dry Run Mode

Test your plan without actually executing steps:

```python
success, results = planner.execute_plan(plan, my_executor, dry_run=True)
```

### Auto-Approve Mode

Skip manual approval for automated workflows:

```python
planner = TaskPlanner(auto_approve=True)
```

### Stop-on-Error Control

Continue execution even if steps fail:

```python
success, results = planner.execute_plan(
    plan, 
    my_executor, 
    stop_on_error=False
)
```

### Save and Load Plans

Persist plans to disk:

```python
# Save
planner.save_plan(plan, "my_plan.json")

# Load
loaded_plan = planner.load_plan("my_plan.json")

# Verify integrity
is_valid = loaded_plan.verify_integrity()
```

### Execution Summary

Get a detailed summary of plan execution:

```python
summary = planner.get_execution_summary(plan)
print(f"Progress: {summary['progress_percentage']}%")
print(f"Completed: {summary['completed']}/{summary['total_steps']}")
```

## 🛡️ Safety Features

### Built-in Dangerous Operation Detection

The system automatically detects and warns about:
- File deletion operations
- System shutdown/reboot commands
- Database drop/truncate operations
- Access to sensitive system paths

### Checksum Verification

Every plan gets a SHA-256 checksum to detect tampering:

```python
# Checksum is automatically calculated
plan.checksum = plan.calculate_checksum()

# Verify before execution
if plan.verify_integrity():
    # Safe to execute
    pass
```

### Rollback Support

Steps can be marked as rollback-capable:

```python
step = {
    "description": "Create user account",
    "action": "create_user",
    "parameters": {"username": "john"},
    "rollback_possible": True  # Can be reverted if needed
}
```

## 📖 Examples

Check out the `examples.py` file for comprehensive examples:

1. **Basic Usage** - Simple task planning and execution
2. **Dangerous Operations** - Handling risky operations safely
3. **Save and Load** - Persisting plans to disk
4. **Auto-Approve Mode** - Automated execution
5. **Error Handling** - Dealing with failures gracefully

Run the examples:

```bash
python examples.py
```

## 🏗️ Architecture

```
TaskPlanner (Main Interface)
    ├── SafetyValidator (Security Layer)
    │   ├── Dangerous operation detection
    │   ├── Sensitive path checking
    │   └── Parameter validation
    │
    └── TaskExecutor (Execution Engine)
        ├── Step execution
        ├── Checkpoint management
        ├── Rollback support
        └── Execution history
```

## 🎯 Use Cases

- **AI Agent Task Management**: Let AI agents safely plan and execute multi-step workflows
- **DevOps Automation**: Orchestrate deployment and maintenance tasks
- **Data Pipelines**: Build complex ETL workflows with safety checks
- **System Administration**: Automate system tasks with validation
- **API Orchestration**: Chain multiple API calls with error handling

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Designed for AI agents that need safe, validated task execution
- Inspired by workflow orchestration systems and DevOps best practices
- Built with security and reliability as top priorities

## 📞 Contact

**Author**: cerbug45

**GitHub**: [@cerbug45](https://github.com/cerbug45)

---

⭐ If you find this project useful, please consider giving it a star on GitHub!
