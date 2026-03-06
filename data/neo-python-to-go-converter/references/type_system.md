# Type System Reference

## Overview

This document describes how Python types are mapped to Go types during automatic conversion. The converter uses a combination of direct mappings and type inference to produce idiomatic Go code.

## Direct Type Mappings

The `python_to_go_mappings.json` file defines the base type mapping table for known Python type names:

| Python Type | Go Type      | Notes                                     |
|-------------|--------------|-------------------------------------------|
| `int`       | `int`        | Python ints are arbitrary precision; Go int is platform-dependent (32 or 64-bit). For large numbers, consider `int64`. |
| `float`     | `float64`    | Python float is double precision; matches Go `float64`. |
| `str`       | `string`     | Unicode strings in Python correspond to Go strings. |
| `bool`      | `bool`       | Boolean values map directly. |
| `list`      | `[]interface{}` | Heterogeneous lists default to empty interface. If element types can be inferred, a more specific slice type (e.g., `[]int`) is used. |
| `dict`      | `map[string]interface{}` | Dictionary keys are assumed to be strings; values are empty interface unless inferred. |
| `None`      | `nil`        | Used as zero value for pointers, interfaces, maps, slices, etc. |
| `bytes`     | `[]byte`     | Byte sequences map directly. |

These mappings are applied when the converter encounters a type annotation (e.g., `def foo(x: int) -> str:`) or when inferring types from constant values.

## Type Inference

When type annotations are absent, the converter attempts to infer Go types from the AST node structure and constant values. The inference algorithm is implemented in `type_mapper.py`.

### Inference from Constants

- `None` → `interface{}` (or nil context)
- `True` / `False` → `bool`
- Integer literals → `int`
- Floating-point literals → `float64`
- String literals → `string`
- Bytes literals → `[]byte`

### Inference from Collections

- **Lists**: If all elements have the same inferred type `T`, the list type becomes `[]T`. Otherwise, `[]interface{}`.
- **Dicts**: If first key-value pair yields key type `K` and value type `V`, and subsequent pairs match, the dict type becomes `map[K]V`. Otherwise, `map[string]interface{}`.
- **Tuples**: Tuples are not directly representable as a single Go type (except as multiple return values). The converter currently renders them as `/* tuple */(a, b, c)` in expressions. In return statements or assignments, they may be converted to multiple values if the context is a multi-assignment.

### Inference from Operations

- **Binary operations** (`+`, `-`, `*`, `/`, `%`): If both operands share the same numeric type, the result retains that type. For `+` with strings, result is `string`.
- **Comparisons** (`==`, `!=`, `<`, `<=`, `>`, `>=`): Result is always `bool`.
- **Boolean operations** (`and`, `or`): Result is `bool`.
- **Unary operations** (`not`, `-`, `+`): `not` yields `bool`; numeric unaries retain operand type.

### Inference from Variables

When a variable first appears in a `:=` short declaration, its type is inferred from the right-hand side expression. Subsequent reassignments must be type-compatible. If a variable's type cannot be determined, it defaults to `interface{}`.

### Inference from Function Calls

- Built-in functions like `len` return `int`.
- `range` used in `for` loops yields integer values.
- Other function calls default to `interface{}` unless the function is known to return a specific type (e.g., `os.Exit` returns `void`, but Go has no void; actually it's a function that doesn't return a value, so Go uses no return).

## Limitations of Type Inference

- **Dynamic Python features** (e.g., reassigning a variable to a different type) cause the inferred type to become `interface{}`.
- **Complex expressions** involving heterogeneous operations fall back to `interface{}`.
- **Lambda expressions** are translated to Go function literals with parameter types inferred from context. Return types are not inferred and default to `interface{}`.
- **Class attributes** (instance variables) are derived from assignments to `self.xxx`. The type is inferred from the assigned value. Subsequent assignments to the same attribute with a different type will result in inconsistent Go field type.

## Overriding Inference

Currently, there is no mechanism to manually override inferred types. The converter relies on Python type annotations when available. Adding explicit type hints in Python code improves conversion accuracy.

## Examples

```python
# Python: explicit annotation
def add(x: int, y: int) -> int:
    return x + y
```

```go
// Go: types directly mapped
func add(x int, y int) int {
    return x + y
}
```

```python
# Python: inferred types
nums = [1, 2, 3]            # list of ints
m = {"a": 1, "b": 2}        # dict with string keys and int values
```

```go
// Go: inferred slice and map
nums := []int{1, 2, 3}
m := map[string]int{"a": 1, "b": 2}
```

## Future Improvements

- Support for Go generics when converting list/dict operations.
- Better handling of numeric type precision (e.g., distinguishing `int` vs `int64`).
- Propagation of type constraints from function signatures.
