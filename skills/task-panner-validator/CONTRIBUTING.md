# Contributing to Task Planner and Validator

First off, thank you for considering contributing to Task Planner and Validator! It's people like you that make this tool better for everyone.

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates.

When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** (code snippets, config files)
- **Describe the behavior you observed** and what you expected
- **Include Python version and OS information**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description** of the suggested enhancement
- **Provide specific examples** to demonstrate the steps
- **Describe the current behavior** and explain the behavior you expected
- **Explain why this enhancement would be useful**

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/task-planner-validator.git
cd task-planner-validator

# Create a branch
git checkout -b feature/your-feature-name
```

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Group standard library, third-party, and local imports
- **Docstrings**: Use Google style docstrings
- **Type hints**: Use type hints for function parameters and returns

### Example Code Style

```python
from typing import List, Dict, Optional

def process_steps(
    steps: List[Step],
    executor: Callable,
    dry_run: bool = False
) -> tuple[bool, List[Dict]]:
    """
    Process a list of steps with the given executor.
    
    Args:
        steps: List of Step objects to process
        executor: Callable that executes each step
        dry_run: If True, simulate execution without running
        
    Returns:
        Tuple of (success, results)
        
    Raises:
        ValidationError: If steps fail validation
    """
    results = []
    
    for step in steps:
        # Process step
        result = executor(step.action, step.parameters)
        results.append(result)
    
    return True, results
```

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

Good commit messages:
```
Add rollback checkpoint functionality

- Implement checkpoint stack for step rollback
- Add checkpoint creation before step execution
- Add rollback_to_checkpoint method
- Update tests for checkpoint functionality

Fixes #123
```

## Testing

### Running Tests

```bash
python test_basic.py
```

### Writing Tests

Add tests for new features in `test_basic.py` or create new test files:

```python
def test_new_feature():
    """Test description of what's being tested"""
    planner = TaskPlanner()
    
    # Setup
    steps = [...]
    plan = planner.create_plan("Test", "Description", steps)
    
    # Execute
    result = planner.some_new_method(plan)
    
    # Assert
    assert result == expected_value
    
    print("✅ New feature test passed")
```

## Documentation

### Docstring Format

Use Google style docstrings:

```python
def create_plan(
    self,
    title: str,
    description: str,
    steps: List[Dict[str, Any]]
) -> TaskPlan:
    """
    Create a new task plan with the given steps.
    
    This method converts step dictionaries into Step objects,
    generates a unique task ID, and calculates an integrity
    checksum for the plan.
    
    Args:
        title: Human-readable title for the task
        description: Detailed description of what the task does
        steps: List of step dictionaries with action details
        
    Returns:
        TaskPlan object with all steps and metadata
        
    Example:
        >>> planner = TaskPlanner()
        >>> steps = [{"description": "Test", "action": "test", ...}]
        >>> plan = planner.create_plan("My Task", "Description", steps)
        >>> print(plan.task_id)
        'abc-123-def-456'
    """
```

### Updating README

If your changes affect how users interact with the library, update:
- README.md
- QUICKSTART.md (if applicable)
- examples.py (add new examples)

## Project Structure

```
task-planner-validator/
├── task_planner.py      # Main library code
├── examples.py          # Usage examples
├── test_basic.py        # Test suite
├── README.md            # Main documentation
├── QUICKSTART.md        # Quick start guide
├── CONTRIBUTING.md      # This file
├── LICENSE              # MIT License
├── requirements.txt     # Dependencies (none!)
└── .gitignore          # Git ignore rules
```

## Feature Requests

We track feature requests as GitHub issues. Before creating a feature request:

1. Check if it's already been requested
2. Consider if it fits the project's goals
3. Think about backward compatibility

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How do you envision this working?

**Alternatives Considered**
What other solutions have you considered?

**Additional Context**
Any other information, mockups, or examples
```

## Areas That Need Help

We especially welcome contributions in these areas:

- 📝 **Documentation**: Improve docs, add tutorials
- 🧪 **Testing**: Add more test cases, improve coverage
- 🐛 **Bug Fixes**: Fix reported issues
- ✨ **Features**: Implement requested features
- 🎨 **Examples**: Add real-world usage examples
- 🌐 **Integrations**: Add integrations with other tools

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Future CHANGELOG entries
- Commit history

## Questions?

Feel free to:
- Open an issue for questions
- Reach out to @cerbug45 on GitHub

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
