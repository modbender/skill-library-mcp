# Supported Features

This document enumerates the Python language features and standard library modules that are currently supported by the converter. For each feature, a brief description and a simple example are provided.

## Language Features

### Variables and Assignment

- **Simple assignment**: `x = value`
- **Multiple assignment**: `a = b = 0` (only simple chain; not true tuple unpacking)
- **Augmented assignment**: `x += 1`, `x -= 1`, `x *= 2`, `x /= 2`, `x %= 3`
- **Type-annotated variables** (PEP 484 style in function args only; top-level variable annotations are not yet parsed)

### Data Types

- `int` integers
- `float` floating-point numbers
- `str` strings (Unicode)
- `bool` booleans (`True`, `False`)
- `list` mutable sequences (converted to slices)
- `dict` mappings (converted to maps)
- `None` null value
- `bytes` byte strings
- `tuple` as expression (limited; not as assignment target)

### Operators

- Arithmetic: `+`, `-`, `*`, `/`, `%`
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Boolean: `and` (`&&`), `or` (`||`), `not` (`!`)
- Unary: `+`, `-`, `not`
- String concatenation: `+` (strings)
- Membership: `in` (not yet translated; **unsupported**)
- Identity: `is`, `is not` (**unsupported**)
- Bitwise: `&`, `|`, `^`, `~`, `<<`, `>>` (**unsupported**)
- Floor division: `//` (**unsupported**)

### Control Flow

- `if` / `elif` / `else`
- `for` loops over iterables and `range()`
- `while` loops (see note: **currently emits invalid Go `while` keyword; avoid or rewrite**)
- `break` and `continue`
- `pass` (converted to comment)

### Functions

- Definition with `def`
- Positional arguments
- Type annotations for parameters and return type
- Return statements (including early returns)
- Default return `None` (converted to no return or `interface{}`)
- **Not supported**: default argument values, `*args`, `**kwargs`, keyword-only arguments, positional-only parameters, lambda parameters with annotations (not needed)

### Classes

- Class definition with `class Name:`
- Instance methods with `self` as first parameter
- Constructor method `__init__` (treated as a regular method named `Init`)
- Instance attributes discovered from `self.attr = value` assignments inside methods
- **Not supported**: inheritance, class methods, static methods, properties, `__str__`, `__repr__`, multiple inheritance, metaclasses, `super()`

### Exceptions

- `raise` statements (`raise Exception(...)`, `raise`, `raise from`)
- `try` / `except` / `else` / `finally` blocks (see note: currently **not converted**; body runs without catching; `raise` becomes `panic`)
- `assert` statements (converted to `if !cond { panic(...) }`)

### Expressions

- **Constant literals**: numbers, strings, bytes, booleans, `None`
- **Variable references**
- **Function calls** (including methods)
- **Attribute access**: `obj.attr`
- **Binary operations**: as listed under Operators
- **Unary operations**: `not`, `+`, `-`
- **Comparisons**: including chained comparisons
- **Boolean operations**: `and`, `or`
- **List literals**: `[1, 2, 3]`
- **Tuple literals**: `(a, b, c)` (expression only)
- **Dictionary literals**: `{"a": 1}`
- **Subscripting**: `obj[key]`
- **Lambda expressions**: `lambda args: body`
- **List comprehensions**: **unsupported**
- **Generator expressions**: **unsupported**
- **Set/dict comprehensions**: **unsupported**
- **Yield**: **unsupported**
- **Await/Async**: **unsupported**

### Built-in Functions

The following Python built-in functions have direct mappings:

| Python   | Go Equivalent    | Notes |
|----------|-------------------|-------|
| `print`  | `fmt.Println`     | Variadic |
| `len`    | `len`             | Works on slices, arrays, maps, strings |
| `range`  | (special)         | In `for` loops, expands to C-style numeric loop |

`enumerate` is listed in `python_to_go_mappings.json` as mapping to `internal/enumerate` but no implementation exists; treat as unsupported.

## Standard Library Imports

The following modules can be imported and will be automatically translated to the corresponding Go import path:

| Python Module | Go Package      |
|---------------|-----------------|
| `os`          | `os`            |
| `sys`         | `sys`           |
| `json`        | `encoding/json` |
| `math`        | `math`          |
| `strings`     | `strings`       |
| `fmt`         | `fmt`           |
| `time`        | `time`          |
| `io`          | `io`            |
| `os.path`     | `path/filepath` |

**Important:** Import translation does **not** automatically convert calls to these libraries. For example, `json.dumps(obj)` is not rewritten to `json.Marshal`. You will need to manually write the Go equivalents.

## Examples of Supported Constructs

### Simple Function

```python
def square(x: int) -> int:
    return x * x
```

### Conditional Logic

```python
def abs(x: int) -> int:
    if x < 0:
        return -x
    else:
        return x
```

### Loops and Lists

```python
def sum_list(nums: list) -> int:
    total = 0
    for n in nums:
        total += n
    return total
```

### Range Loop

```python
def print_numbers():
    for i in range(5):
        print(i)
```

### Class with Method

```python
class Counter:
    def __init__(self):
        self.count = 0
    def inc(self):
        self.count += 1
```

### Dictionary Operations

```python
def get_value(m: dict, key: str) -> str:
    return m[key]
```

### Lambda (Limited)

```python
def apply(f, x):
    return f(x)
```

### Assert

```python
def check_positive(x: int):
    assert x > 0, "must be positive"
```

### Raise

```python
def fail(msg):
    raise RuntimeError(msg)
```

## Feature Detection

The converter will emit warnings for unsupported features but will continue to generate code, skipping those statements. The exit code will be non-zero (`E001` or `E003`) if critical errors occur.

## Future Support

Planned enhancements include:
- `while` loops correctly mapped to `for`
- `try/except` to `if err != nil`
- Default argument values
- `*args` and `**kwargs`
- `is` / `is not` for `None` and primitive identity
- Bitwise operators
- List comprehensions to explicit loops
- `enumerate` helper
- `super()` in single inheritance

## Reporting Missing Features

If you need a feature that is listed as unsupported, please file an issue with a code example. The converter will be improved incrementally.
