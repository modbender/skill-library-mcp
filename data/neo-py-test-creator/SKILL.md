---
name: py-test-creator
description: Automatically generates pytest-compatible unit test templates from Python function signatures and docstrings
---

# py-test-creator — Skill Documentation

## Overview

`py-test-creator` is an OpenClaw skill that automatically generates comprehensive pytest unit test templates from Python code. It parses function signatures, type hints, and docstrings to create actionable test scaffolding that covers edge cases and parameter combinations.

**Key features:**
- Parse Python functions with complex signatures (defaults, type hints, variadic args)
- Generate pytest-compatible test methods with proper assertions
- Handle both standalone functions and class methods
- Convert docstrings into test method documentation
- Create ready-to-use test files with correct imports and structure

## Installation

Dependencies are managed via `package.json`. Install with:

```bash
npm install
```

This will install the required Python packages (pytest, ast-parser utilities) and Node.js dependencies for the skill runner.

## Usage

Trigger the skill with natural language:

- "Create unit tests for this Python function"
- "Generate test templates from these function signatures"
- "Write pytest tests for my Python methods"
- "Create unit test scaffolding from docstrings"

The skill expects a Python file or code snippet as input and produces a corresponding test file.

## Input/Output

**Input:**  
A Python file path or raw code containing one or more functions/methods.

**Output:**  
A test file (e.g., `test_<original>.py`) containing pytest test functions with:
- `import pytest` statements
- Test fixtures for common parameter types
- Edge case coverage (None values, boundaries, invalid types)
- Parametrized tests where appropriate
- Docstrings explaining test purpose

**Example:**

Input (`utils.py`):
```python
def add(a: int, b: int) -> int:
    """Add two integers and return the result."""
    return a + b
```

Output (`test_utils.py`):
```python
import pytest
from utils import add

def test_add_basic_integers():
    """Test add function with basic positive integers."""
    assert add(1, 2) == 3

def test_add_negative_numbers():
    """Test add function with negative integers."""
    assert add(-1, -2) == -3

def test_add_zero():
    """Test add function with zero."""
    assert add(0, 5) == 5
    assert add(5, 0) == 5

def test_add_large_numbers():
    """Test add function with large integers."""
    assert add(1000000, 2000000) == 3000000
```

## Configuration

No configuration required. The skill uses default pytest conventions.

**Optional environment variables:**
- `PYTEST_STRICT`: Set to `true` to enable strict mark handling
- `TEST_COVERAGE`: Set to `true` to include coverage hints in generated tests

## Error Handling

The skill exits with non-zero status on:
- Invalid Python syntax
- Missing input file/code
- Permission errors writing output
- AST parsing failures

Error messages are logged to stderr.

## Limitations

Out of scope:
- Running or validating generated tests
- Integration/end-to-end testing
- Multi-language support (Python only)
- CI/CD integration
- Performance optimization of tests

## Files

The skill package includes:

```
skill/
├── SKILL.md           # This documentation
├── package.json       # NPM package definition
├── README.md          # Quick start guide
└── scripts/
    ├── main.py        # CLI entry point
    ├── parser.py      # Python AST parser
    ├── generator.py   # Test template generator
    └── cli.py         # Command-line interface
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [OpenClaw Skill System](https://docs.openclaw.ai)

## Support

For issues, feature requests, or contributions, visit:
- Repository: `openclaw/openclaw`
- Discord: https://discord.com/invite/clawd

## License

MIT © OpenClaw Contributors
