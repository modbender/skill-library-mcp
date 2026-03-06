# API Reference

Complete reference for Task Planner and Validator classes and methods.

## Classes

### TaskPlanner

Main interface for creating, validating, and executing task plans.

```python
TaskPlanner(auto_approve: bool = False)
```

**Parameters:**
- `auto_approve` (bool): If True, automatically approve plans before execution

**Example:**
```python
planner = TaskPlanner(auto_approve=False)
```

#### Methods

##### create_plan

```python
create_plan(
    title: str,
    description: str,
    steps: List[Dict[str, Any]]
) -> TaskPlan
```

Create a new task plan with validation and checksum.

**Parameters:**
- `title`: Task title
- `description`: Task description
- `steps`: List of step dictionaries

**Returns:** `TaskPlan` object

**Step Dictionary Format:**
```python
{
    "description": str,           # Required: Step description
    "action": str,                # Required: Action identifier
    "parameters": Dict,           # Required: Action parameters
    "expected_output": str,       # Required: Expected result
    "safety_check": bool,         # Optional: Enable safety validation (default: True)
    "rollback_possible": bool,    # Optional: Can be rolled back (default: True)
    "max_retries": int           # Optional: Max retry attempts (default: 3)
}
```

##### validate_plan

```python
validate_plan(plan: TaskPlan) -> tuple[bool, List[str]]
```

Validate a task plan for safety and integrity.

**Returns:** `(is_valid, warnings)` tuple

##### approve_plan

```python
approve_plan(plan: TaskPlan, approved_by: str = "user") -> bool
```

Approve a plan for execution after validation.

**Returns:** `True` if approval successful

##### execute_plan

```python
execute_plan(
    plan: TaskPlan,
    executor_func: Callable,
    dry_run: bool = False,
    stop_on_error: bool = True
) -> tuple[bool, List[Dict]]
```

Execute a task plan step by step.

**Parameters:**
- `plan`: TaskPlan to execute
- `executor_func`: Function that executes each step
- `dry_run`: If True, simulate without executing
- `stop_on_error`: If True, stop on first error

**Executor Function Signature:**
```python
def executor(action: str, parameters: dict) -> Any:
    # Execute the action
    return result
```

**Returns:** `(success, results)` tuple

##### save_plan

```python
save_plan(plan: TaskPlan, filepath: str)
```

Save plan to JSON file.

##### load_plan

```python
load_plan(filepath: str) -> TaskPlan
```

Load plan from JSON file.

**Returns:** Loaded `TaskPlan` object

##### get_execution_summary

```python
get_execution_summary(plan: TaskPlan) -> Dict
```

Get execution summary with progress statistics.

**Returns:**
```python
{
    'task_id': str,
    'title': str,
    'status': str,
    'total_steps': int,
    'completed': int,
    'failed': int,
    'pending': int,
    'progress_percentage': float,
    'created_at': str,
    'completed_at': str
}
```

---

### TaskPlan

Represents a complete task with multiple steps.

**Attributes:**
- `task_id` (str): Unique identifier
- `title` (str): Task title
- `description` (str): Task description
- `steps` (List[Step]): Ordered list of steps
- `created_at` (str): ISO timestamp
- `status` (TaskStatus): Current status
- `approved_by` (str): Approver identifier
- `approved_at` (str): Approval timestamp
- `completed_at` (str): Completion timestamp
- `metadata` (Dict): Additional metadata
- `checksum` (str): SHA-256 integrity hash

#### Methods

##### to_dict

```python
to_dict() -> Dict
```

Convert plan to dictionary for serialization.

##### calculate_checksum

```python
calculate_checksum() -> str
```

Calculate SHA-256 checksum for integrity verification.

##### verify_integrity

```python
verify_integrity() -> bool
```

Verify plan hasn't been tampered with.

---

### Step

Represents a single execution step.

**Attributes:**
- `step_id` (str): Unique identifier
- `order` (int): Execution order
- `description` (str): Human-readable description
- `action` (str): Action identifier
- `parameters` (Dict): Action parameters
- `expected_output` (str): Expected result
- `safety_check` (bool): Enable safety validation
- `rollback_possible` (bool): Can be rolled back
- `status` (StepStatus): Current status
- `result` (Any): Execution result
- `error` (str): Error message if failed
- `started_at` (str): Start timestamp
- `completed_at` (str): Completion timestamp
- `retry_count` (int): Number of retries
- `max_retries` (int): Maximum retries allowed

#### Methods

##### mark_running

```python
mark_running()
```

Mark step as currently running.

##### mark_completed

```python
mark_completed(result: Any)
```

Mark step as successfully completed.

##### mark_failed

```python
mark_failed(error: str)
```

Mark step as failed with error message.

---

### SafetyValidator

Security validation layer for dangerous operations.

#### Methods

##### validate_step

```python
validate_step(step: Step) -> tuple[bool, List[str]]
```

Validate single step for safety.

**Returns:** `(is_safe, warnings)` tuple

##### validate_plan

```python
validate_plan(plan: TaskPlan) -> tuple[bool, List[str]]
```

Validate entire plan for safety and integrity.

**Returns:** `(is_safe, warnings)` tuple

---

### TaskExecutor

Execution engine with rollback support.

#### Methods

##### execute_step

```python
execute_step(
    step: Step,
    executor_func: Callable,
    dry_run: bool = False
) -> tuple[bool, Any, Optional[str]]
```

Execute a single step.

**Returns:** `(success, result, error)` tuple

##### create_checkpoint

```python
create_checkpoint(step: Step)
```

Create rollback checkpoint before step execution.

##### rollback_to_checkpoint

```python
rollback_to_checkpoint(checkpoint_index: int = -1) -> bool
```

Rollback to a specific checkpoint.

---

## Enums

### TaskStatus

Task execution states:
- `PENDING`: Created but not approved
- `APPROVED`: Validated and approved
- `RUNNING`: Currently executing
- `COMPLETED`: Successfully finished
- `FAILED`: Execution failed
- `CANCELLED`: User cancelled
- `NEEDS_REVIEW`: Requires manual review

### StepStatus

Step execution states:
- `PENDING`: Not started
- `RUNNING`: Currently executing
- `COMPLETED`: Successfully finished
- `FAILED`: Execution failed
- `SKIPPED`: Intentionally skipped

---

## Usage Examples

### Basic Plan Creation

```python
from task_planner import TaskPlanner

planner = TaskPlanner()

steps = [{
    "description": "Fetch data",
    "action": "api_call",
    "parameters": {"endpoint": "/users"},
    "expected_output": "User list"
}]

plan = planner.create_plan("Data Fetch", "Get users", steps)
```

### Custom Executor

```python
def my_executor(action: str, parameters: dict):
    if action == "api_call":
        # Make API call
        return call_api(parameters["endpoint"])
    elif action == "process":
        # Process data
        return process_data(parameters["data"])
    else:
        raise ValueError(f"Unknown action: {action}")

success, results = planner.execute_plan(plan, my_executor)
```

### Error Handling

```python
success, results = planner.execute_plan(
    plan,
    my_executor,
    stop_on_error=False
)

for result in results:
    if not result['success']:
        print(f"Step {result['order']} failed: {result['error']}")
```

### Safety Validation

```python
is_valid, warnings = planner.validate_plan(plan)

if not is_valid:
    print("Plan validation failed!")
    for warning in warnings:
        print(f"  - {warning}")
else:
    planner.approve_plan(plan)
```

---

## Type Hints

The library uses Python type hints throughout:

```python
from typing import List, Dict, Optional, Any, Callable

def execute_plan(
    self,
    plan: TaskPlan,
    executor_func: Callable[[str, Dict[str, Any]], Any],
    dry_run: bool = False,
    stop_on_error: bool = True
) -> tuple[bool, List[Dict[str, Any]]]:
    ...
```

---

## Exceptions

The library uses standard Python exceptions:

- `ValueError`: Invalid parameters
- `KeyError`: Missing required fields
- `FileNotFoundError`: Plan file not found
- `json.JSONDecodeError`: Invalid JSON format

Handle them appropriately:

```python
try:
    plan = planner.load_plan("missing.json")
except FileNotFoundError:
    print("Plan file not found")
except json.JSONDecodeError:
    print("Invalid JSON format")
```
