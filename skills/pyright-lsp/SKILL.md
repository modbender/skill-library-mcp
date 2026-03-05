---
name: pyright-lsp
description: Python language server (Pyright) providing static type checking, code intelligence, and LSP diagnostics for .py and .pyi files. Use when working with Python code that needs type checking, autocomplete suggestions, error detection, or code navigation.
---

# Pyright LSP

Python language server integration providing static type checking and code intelligence through Microsoft's Pyright.

## Capabilities

- **Type checking**: Static analysis of Python types
- **Code intelligence**: Autocomplete, go-to-definition, find references
- **Error detection**: Real-time diagnostics for type errors and issues
- **Supported extensions**: `.py`, `.pyi`

## Installation Check

Before using, verify Pyright is installed:

```bash
which pyright || npm install -g pyright
```

Alternative installation methods:
```bash
pip install pyright
# or
pipx install pyright  # recommended for CLI tools
```

## Usage

Run type checking on Python files:

```bash
pyright path/to/file.py
```

Run on entire project:

```bash
cd project-root && pyright
```

## Configuration

Create `pyrightconfig.json` in project root for custom settings:

```json
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__"],
  "typeCheckingMode": "basic",
  "pythonVersion": "3.10"
}
```

## Integration Pattern

When editing Python code:
1. Run pyright after significant changes
2. Address type errors before committing
3. Use diagnostics to improve code quality

## More Information

- [Pyright on npm](https://www.npmjs.com/package/pyright)
- [Pyright on PyPI](https://pypi.org/project/pyright/)
- [GitHub Repository](https://github.com/microsoft/pyright)
