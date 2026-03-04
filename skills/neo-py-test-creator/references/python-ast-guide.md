# Python AST Guide

This guide covers the Python Abstract Syntax Tree (AST) module and how to use it to analyze Python source code, as used by py-test-creator for function introspection.

## Table of Contents

- [Introduction to AST](#introduction-to-ast)
- [Basic AST Usage](#basic-ast-usage)
- [AST Node Types](#ast-node-types)
- [Walking the AST](#walking-the-ast)
- [Extracting Functions](#extracting-functions)
- [Handling Parameters](#handling-parameters)
- [Type Annotations](#type-annotations)
- [Best Practices](#best-practices)

---

## Introduction to AST

The `ast` module provides a way to parse Python source code into a tree of nodes, each representing a language construct. This allows programmatic analysis of code structure, including:

- Function definitions and signatures
- Class definitions and methods
- Variable assignments
- Control flow (if/for/while)
- Expressions and operators

**Key functions:**
- `ast.parse(source, filename)`: Parse source code into an AST tree
- `ast.walk(node)`: Iterate over all nodes in the tree
- `ast.iter_child_nodes(node)`: Get direct children of a node
- `ast.get_docstring(node)`: Extract docstring from a node

---

## Basic AST Usage

### Parsing Source Code

```python
import ast

source = """
def add(a: int, b: int) -> int:
    return a + b
"""

tree = ast.parse(source)
print(ast.dump(tree, indent=2))
```

Output (simplified):
```
Module(
  body=[
    FunctionDef(
      name='add',
      args=arguments(
        args=[
          arg(arg='a', annotation=Name(id='int')),
          arg(arg='b', annotation=Name(id='int'))
        ],
        returns=Name(id='int')
      ),
      body=[Return(...)],
      decorator_list=[]
    )
  ]
)
```

### Checking Node Types

```python
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        print(f"Function: {node.name}")
        print(f"  Line: {node.lineno}")
        docstring = ast.get_docstring(node)
        if docstring:
            print(f"  Docstring: {docstring}")
```

---

## AST Node Types

### Function and Async Functions

- `ast.FunctionDef`: Regular function definition
- `ast.AsyncFunctionDef`: Async function (with `async def`)

Key attributes:
- `name`: Function name (str)
- `args`: `arguments` node containing parameters
- `body`: List of statement nodes (the function body)
- `decorator_list`: List of decorator expressions
- `returns`: Return type annotation (AST node or None)
- `lineno`: Line number where function is defined
- `docstring`: Access via `ast.get_docstring(node)`

### Arguments

The `arguments` node contains parameter information:

- `args`: List of `arg` nodes (positional or keyword parameters)
- `posonlyargs`: Positional-only parameters (Python 3.8+)
- `vararg`: `*args` parameter (or None)
- `kwonlyargs`: Keyword-only parameters
- `kwarg`: `**kwargs` parameter (or None)
- `defaults`: List of default values for the last n positional/keyword args
- `kw_defaults`: List of defaults for keyword-only args

### Parameter (arg) Node

- `arg`: Represents a single parameter
  - `arg`: Parameter name (str)
  - `annotation`: Type hint AST node (or None)

---

## Walking the AST

### Depth-First Traversal

```python
def process_node(node, parent=None):
    # Process current node
    handle_node(node, parent)

    # Recursively process children
    for child in ast.iter_child_nodes(node):
        process_node(child, node)
```

### Filtering Nodes

```python
# Get all function definitions at top level
module = ast.parse(source)
functions = [node for node in module.body if isinstance(node, ast.FunctionDef)]

# Get all classes
classes = [node for node in module.body if isinstance(node, ast.ClassDef)]
```

---

## Extracting Functions

### Minimal Example

```python
import ast

def extract_functions(source: str):
    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func = {
                "name": node.name,
                "line": node.lineno,
                "docstring": ast.get_docstring(node),
                "parameters": [arg.arg for arg in node.args.args],
            }
            functions.append(func)

    return functions
```

### Full-Featured Example

See `parser.py` in the skill code for a complete implementation that:

- Handles both `FunctionDef` and `AsyncFunctionDef`
- Distinguishes standalone functions from class methods
- Extracts parameter types, defaults, and kinds
- Preserves decorators
- Handles complex type annotations
- Supports Python 3.8+ features like positional-only parameters

---

## Handling Parameters

### Parameter Kinds

Parameters have a `kind` attribute indicating how they're passed:

- `POSITIONAL_ONLY`: `/` marker (Python 3.8+)
- `POSITIONAL_OR_KEYWORD`: Standard parameter
- `VAR_POSITIONAL`: `*args`
- `KEYWORD_ONLY`: After `*` or `*args`
- `VAR_KEYWORD`: `**kwargs`

Access via `arg.kind` (value is the string constant above).

### Default Values

Defaults are stored in `arguments.defaults` and `arguments.kw_defaults`:

```python
def foo(a, b=1, *, c=2):
    pass

# args.args = [arg('a'), arg('b'), arg('c')]
# defaults = [1]           # Default for 'b' (aligned to last n positional/keyword)
# kw_defaults = [None, 2]  # Defaults for keyword-only: first is None (c before * was not keyword-only?), second is 2
```

The alignment works as: defaults apply to the last N positional/keyword parameters.

---

## Type Annotations

### Getting Annotations

Each `arg` node has an `annotation` attribute (AST node or None):

```python
def process_param(arg: ast.arg):
    if arg.annotation:
        type_hint = ast.unparse(arg.annotation)  # Python 3.9+
    else:
        type_hint = "Any"
```

### Common Annotation Nodes

- `ast.Name`: Simple type like `int`, `str`, `MyClass`
  - Access identifier via `.id`
- `ast.Subscript`: Generic types like `List[int]`, `Dict[str, Any]`
  - `.value`: The base type (e.g., `List`)
  - `.slice`: The type parameter(s)
- `ast.Tuple`: Tuple types like `(int, str)`
  - `.elts`: List of element type nodes
- `ast.Constant`: Literals like `None`, `True`, `False`, or string/numeric constants

### Fallback for Older Python

If `ast.unparse` is not available (Python < 3.9), you can implement a simple formatter:

```python
def simple_unparse(node):
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Subscript):
        value = simple_unparse(node.value)
        slice = simple_unparse(node.slice)
        return f"{value}[{slice}]"
    elif isinstance(node, ast.Constant):
        return repr(node.value)
    else:
        return "Any"  # Fallback
```

---

## Best Practices

1. **Use `ast.unparse` when available** (Python 3.9+). It provides accurate string representations of AST nodes.

2. **Handle syntax errors gracefully**. Wrap `ast.parse()` in try/except:

   ```python
   try:
       tree = ast.parse(source)
   except SyntaxError as e:
       raise ValueError(f"Invalid syntax: {e}")
   ```

3. **Preserve line numbers**. Node `lineno` attributes are crucial for error reporting and debugging.

4. **Be careful with nested scopes**. Functions can be defined inside other functions (closures). Consider if you want to include nested functions.

5. **Consider `type_comments`**. Python 3.6-3.8 may have type comments instead of annotations. Check `node.type_comment`.

6. **Support both functions and methods**. When walking classes, track the enclosing class name.

7. **Handle async functions**. `ast.AsyncFunctionDef` has the same structure as `FunctionDef`.

8. **Avoid executing code**. AST analysis is static; do not evaluate expressions or call functions.

9. **Use `dataclasses` for structured data**. Represent functions, parameters as dataclasses for clarity.

10. **Write comprehensive tests** for your parser itself.

---

## Example: Complete Function Extractor

```python
import ast
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class FunctionInfo:
    name: str
    line: int
    docstring: Optional[str]
    parameters: List[dict]
    is_method: bool = False
    class_name: Optional[str] = None

def extract_all_functions(source: str) -> List[FunctionInfo]:
    tree = ast.parse(source)
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Get parameters
            params = []
            all_args = (
                node.args.posonlyargs +
                node.args.args +
                [node.args.vararg] if node.args.vararg else [] +
                node.args.kwonlyargs +
                [node.args.kwarg] if node.args.kwarg else []
            )
            for arg in all_args:
                if arg is None:
                    continue
                param = {
                    "name": arg.arg,
                    "annotation": ast.unparse(arg.annotation) if arg.annotation else None,
                }
                params.append(param)

            func_info = FunctionInfo(
                name=node.name,
                line=node.lineno,
                docstring=ast.get_docstring(node),
                parameters=params,
            )
            functions.append(func_info)

    return functions
```

---

## Resources

- [Python ast documentation](https://docs.python.org/3/library/ast.html)
- [Green Tree Snakes - AST visual guide](https://greentreesnakes.readthedocs.io/)
- [Python AST playground](https://astexplorer.net/)
