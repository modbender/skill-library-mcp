# Conversion Rules

This reference describes the transformation rules applied by the Python-to-Go converter. It details how each Python AST node type is translated into Go code.

## General Principles

- The generated Go code always begins with `package main` unless overridden (future work).
- Imports are automatically added based on Python imports and the mapping table.
- Top-level statements become top-level declarations in Go (functions, variables, etc.).
- Indentation uses tabs.
- Comments originating from the Python source are preserved where possible; the converter adds its own comments for unsupported features.

## Statements

### Function Definition (`def`)

**Python:**

```python
def name(arg1: type1, arg2: type2 = default) -> return_type:
    body
```

**Go:**

```go
func name(arg1 type1, arg2 type2) return_type {
    body
}
```

**Rules:**
- Python function becomes a Go function.
- Arguments with type annotations use the mapped Go types.
- Arguments without annotations default to `interface{}`.
- Default argument values are **not** currently handled; they should be provided manually in Go.
- Return type annotation is mapped; if absent, the function returns no value (or `interface{}` if return statements have mixed types).
- Decorators are ignored (converter does not apply them).
- The function body is translated statement by statement.

**Example:**

```python
def greet(name: str) -> str:
    return "Hello, " + name
```

```go
func greet(name string) string {
    return "Hello, " + name
}
```

---

### Class Definition (`class`)

**Python:**

```python
class ClassName(Base):
    def __init__(self, x: int):
        self.x = x
    def method(self, y: int) -> int:
        return self.x + y
```

**Go:**

```go
type ClassName struct {
    x int
}
func (c *ClassName) Init(x int) {
    c.x = x
}
func (c *ClassName) Method(y int) int {
    return c.x + y
}
```

**Rules:**
- A Python class becomes a Go `struct`.
- Instance fields are discovered by scanning the class body for assignments to `self.attr`. The type is inferred from the assigned value.
- Methods (`def` inside a class) become Go methods with a receiver. The first parameter named `self` (or conventionally `self`) is omitted and replaced by a receiver `(c *ClassName)`.
- `__init__` is renamed to `Init` (capitalized for exportability). It is treated as a regular method; the constructor pattern in Go is manual (usually a `NewClassName` function, not automatically generated yet).
- Inheritance (`class ClassName(Base):`) is **not** supported directly. Go uses composition. The converter does not generate struct embedding for base classes. It will output a comment and ignore bases.

**Limitations:**
- Only simple attributes assigned directly to `self` are recognized. Properties, class variables, and dynamic attributes are not.
- Method resolution order and overriding are not translated; Go interfaces handle behavior differently.
- `super()` calls are not converted.

---

### Assignment (`=`)

**Python:**

```python
x = 42
name = "Alice"
nums = [1, 2, 3]
m = {"a": 1, "b": 2}
```

**Go:**

```go
x := 42
name := "Alice"
nums := []interface{}{1, 2, 3} // or []int if elements homogeneous
m := map[string]interface{}{"a": 1, "b": 2}
```

**Rules:**
- Simple target assignments use short variable declaration (`:=`) when the variable is first encountered in the scope. If the variable already exists in `known_vars`, a regular assignment (`=`) is used.
- Multiple targets (tuple unpacking) are not fully supported; the converter will emit a comment.
- Assignment to attributes (`self.x = value`) becomes `receiver.Attr = value`.
- Assignment to subscripts (`a[0] = x`) becomes `a[0] = x`.

---

### Augmented Assignment (`+=`, `-=`, etc.)

**Python:** `x += 1`

**Go:** `x += 1`

**Rules:** Direct mapping using operator translation. Supported for `+=`, `-=`, `*=`, `/=`, `%=`.

---

### If Statement

**Python:**

```python
if condition:
    body
elif other:
    body2
else:
    body3
```

**Go:**

```go
if condition {
    body
} else if other {
    body2
} else {
    body3
}
```

**Rules:** Straightforward structural translation. The condition expression is translated according to expression rules.

---

### For Loop

**Python:**

```python
# Iteration over a sequence
for item in seq:
    body

# Range-based numeric loop
for i in range(10):
    body

# Range with start/stop
for i in range(2, 10):
    body

# Range with step
for i in range(0, 10, 2):
    body

# Unpacking (limited)
for idx, val in enumerate(seq):
    body
```

**Go:**

```go
// Iteration over a sequence (slice, array, map, channel)
for _, item := range seq {
    body
}

// Numeric range: range(10) -> i from 0 to 9
for i := 0; i < 10; i++ {
    body
}

// range(2, 10)
for i := 2; i < 10; i++ {
    body
}

// range(0, 10, 2)
for i := 0; i < 10; i += 2 {
    body
}

// enumerate(seq) -> currently mapped to internal/enumerate (not implemented); avoid.
```

**Rules:**
- For loops over iterables use Go's `range` construct. The loop variable takes the place of the Python target.
- If the Python for-loop uses `range()` with up to three arguments, the converter expands it into a C-style `for` initialization; condition; post statement.
- Unpacking the tuple returned by `enumerate` is not supported in Go translation; `enumerate` currently maps to an undefined internal package. Use a manual counter if needed.

---

### While Loop

**Python:**

```python
while condition:
    body
```

**Go:**

```go
for condition {
    body
}
```

**Rules:** The converter currently emits `while` loops as `while { ... }` which is invalid Go; this is a known limitation. The expected correct translation should be `for condition { ... }`. As a workaround, avoid `while` loops or manually rewrite them as `for` loops in the Python code (e.g., `while True` -> `for { ... }` with break). The development version may have this bug.

---

### Return Statement

**Python:**

```python
return expression
# or
return
```

**Go:**

```go
return expression
// or
return
```

**Rules:** Direct translation. The expression's type must match the function's return type.

---

### Expression Statement

Any expression used as a statement (e.g., a function call, a binary operation) is emitted as a standalone statement in Go. For `print(...)`, it becomes `fmt.Println(...)`.

---

### Pass

**Python:** `pass`

**Go:** `// pass`

**Rules:** Replaced with an empty comment to maintain line numbering.

---

### Break and Continue

**Python:** `break` / `continue`

**Go:** `break` / `continue`

**Rules:** Direct mapping. They affect the innermost `for` loop.

---

### Delete

**Python:** `del x`

**Go:** `// delete not supported`

**Rules:** Go has no equivalent. The statement is replaced with a comment and ignored.

---

### Raise

**Python:**

```python
raise Exception("msg")
```

**Go:**

```go
panic("msg")
```

**Rules:** All exceptions become panics. This is a drastic but simple translation. Go's `panic` unwinds the stack similar to uncaught exceptions.

---

### Try/Except

**Python:**

```python
try:
    body
except SomeError as e:
    handler
except OtherError:
    handler2
else:
    else_body
finally:
    finally_body
```

**Go:**

```go
// try/except block not automatically converted; manual error handling needed
body
```

**Rules:** The converter currently does not translate structured exception handling to Go's `if err != nil` pattern. The entire `try` statement is replaced with a comment and the body is executed as normal statements. Any `raise` inside will panic. Proper conversion requires manual intervention.

---

### Assert

**Python:**

```python
assert condition, "message"
```

**Go:**

```go
if !condition {
    panic("message")
}
```

**Rules:** Direct translation; if no message is provided, the panic uses `"assertion failed"`.

---

### Unsupported Statements

If a statement type is not recognized, the converter emits a comment indicating the unknown type.

## Expressions

### Constants

| Python Value | Go Literal |
|--------------|------------|
| `None`       | `nil` (or `interface{}`) |
| `True`       | `true` |
| `False`      | `false` |
| `42`         | `42` |
| `3.14`       | `3.14` |
| `"hello"`    | `"hello"` (with escapes) |
| `b"abc"`     | `[]byte("abc")` |

### Names (Variables)

A variable name is emitted as its identifier. If the variable is not known in the current scope, it is assumed to be of type `interface{}`.

### Function Calls

**General:** `func(arg1, arg2, kw=val)` → `func(arg1, arg2, val)` *(note: keyword arguments are not supported in Go; they are passed as regular arguments)*.

**Built-in Functions:**

| Python      | Go                         | Notes |
|-------------|----------------------------|-------|
| `print(...)` | `fmt.Println(...)`        | Variadic |
| `len(x)`    | `len(x)`                  | Works for slices, arrays, maps, strings |
| `range(...)` | `range(...)`              | Used only in for loops; the form `range(a, b, c)` is not valid Go, so the converter rewrites the loop itself, not the expression. |
| `enumerate(seq)` | `internal/enumerate` | Not implemented; avoid. |

**Other calls:** The function expression is translated, and arguments are translated recursively. If the function is an attribute access (e.g., `obj.method()`), the receiver is translated accordingly.

### Attribute Access

**Python:** `obj.attr`

**Go:** `obj.attr`

The base object and attribute name are translated. No property getter/setter logic is added.

### Binary Operations

Operators are mapped according to `python_to_go_mappings.json`:

| Python Operator | Go Operator |
|-----------------|-------------|
| `+`             | `+` |
| `-`             | `-` |
| `*`             | `*` |
| `/`             | `/` (float division; Python `/` is float division even for ints) |
| `%`             | `%` |
| `==`            | `==` |
| `!=`            | `!=` |
| `<`             | `<` |
| `<=`            | `<=` |
| `>`             | `>` |
| `>=`            | `>=` |
| `and`           | `&&` |
| `or`            | `||` |
| `not`           | `!` |

Notes:
- Python's integer division (`//`) is not supported.
- Bitwise operators (`&`, `|`, `^`, `~`, `<<`, `>>`) are not mapped (would need to be added if encountered).

### Unary Operations

| Python | Go |
|--------|----|
| `not x`| `!x` |
| `+x`   | `+x` |
| `-x`   | `-x` |

### Comparisons

Chained comparisons (e.g., `a < b < c`) are translated to logical AND: `a < b && b < c`.

### Boolean Operations

`a and b` → `a && b`<br>
`a or b` → `a || b`

### List Literals

**Python:** `[1, 2, 3]` or `[]`

**Go:** `[]interface{}{1, 2, 3}` or `[]interface{}{}`

If all elements are of the same type, a more specific slice type may be emitted: `[]int{1, 2, 3}`.

### Tuple Literals

**Python:** `(a, b, c)`

**Go:** `/* tuple */ (a, b, c)`

Tuples are not directly represented in Go as a single value. They may appear in multiple assignment contexts (e.g., return multiple values) but in expression contexts the converter produces a placeholder.

### Dictionary Literals

**Python:** `{"key": value}`

**Go:** `map[string]interface{}{"key": value}` or `map[K]V` if key/value types are uniform.

### Subscript (Indexing)

**Python:** `obj[key]`

**Go:** `obj[key]`

Same syntax. For dicts, slices, arrays, strings.

### Lambda Expressions

**Python:** `lambda x: x + 1`

**Go:** `func(x) { return x + 1 }`

**Rules:** The lambda body is a single expression. Parameters are taken from the lambda's argument list. The return type is inferred as `interface{}` (or from lambda usage if known). This is a simplistic translation; real-world lambdas may need manual adjustment.

### List Comprehensions, Generator Expressions, etc.

These are marked as `unsupported` and will be skipped with a warning.

## Scoping and Variable Lifetime

- The converter maintains a simple scope stack. Variables declared with `:=` are added to the current scope's `known_vars`. They persist through the function or top-level scope.
- No block-level scoping (like in Go) is enforced; the converter's `known_vars` dictionary may incorrectly allow a variable declared in an `if` block to be used outside. Go would treat that as an error. Manual cleanup may be needed.

## Comments

- Python comments (`# ...`) are **not** preserved through AST parsing. The converter does not embed them in the output. Consider adding docstrings or explicit comments in code that needs to survive conversion.

## TODOs and FIXMEs

The following areas need improvement:
- Proper `while` translation (use `for`).
- Support for `else` clauses on loops.
- Better conversion of `try/except` to Go `if err != nil`.
- Handling of default argument values.
- Handling of `*args` and `**kwargs`.
- Conversion of `is` and `is not` (identity checks) to pointer comparisons or interface equality.
- Bitwise operators.
- Complex number support.
- `import *` and relative imports.
