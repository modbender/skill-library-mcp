# Best Practices for Python-to-Go Conversion

This guide provides recommendations for writing Python code that converts cleanly to Go, and for refining the generated output. Following these practices will improve conversion success rates and reduce manual post-processing.

## Writing Python Code for Conversion

### 1. Use Explicit Type Annotations

Strongly-typed code yields more accurate Go types.

**Good:**
```python
def process(name: str, age: int) -> str:
    return f"{name} is {age} years old"
```

**Bad:**
```python
def process(name, age):
    return name + " is " + str(age) + " years old"
```

### 2. Avoid Dynamic Features

Stick to static constructs. Avoid `eval`, `exec`, `getattr`, `setattr`, `hasattr`, and `import *`.

### 3. Prefer Simple Loops Over Comprehensions

List comprehensions are not supported. Use explicit `for` loops.

**Good:**
```python
result = []
for x in items:
    result.append(x * 2)
```

**Bad:**
```python
result = [x * 2 for x in items]
```

### 4. Use `for` Loops Instead of `while`

`while` loops currently generate invalid Go code. Use `for` with a condition or `range`.

**Good:**
```python
while True:  # still problematic; better:
for { ; condition;  } not directly, but you can break
def process_until(limit):
    i = 0
    while i < limit:  # problematic
        i += 1
# Better: use for with break if needed
def process_until(limit):
    for i := 0; i < limit; i++ { ... } # not Python
# In Python, you can still use while but will need to edit output
```
Actually, avoid loops that rely on while; prefer for loops over iterables or explicit counters with break.

**Better Python for conversion:**
```python
def process_up_to(n):
    for i in range(n):
        # do work
        if some_condition:
            break
```

### 5. Stick to Supported Built-in Functions

Only `print`, `len`, and `range` (in `for`) are reliably translated. Avoid `enumerate`, `zip`, `map`, `filter`, etc.

**Manual counter example:**
```python
i = 0
for item in items:
    # use i and item
    i += 1
```

### 6. Use `try/except` Sparingly

`try/except` blocks are not converted. If exception handling is critical, you may need to rewrite using explicit error checks after conversion.

Consider structuring code to avoid exceptions in the first place (check preconditions). Or accept that `try` bodies will be inserted without handling, and panics will propagate.

### 7. Use `assert` for Preconditions

`assert` converts nicely to `if !cond { panic(...) }`. This is a good way to embed sanity checks.

### 8. Favor Simple Data Structures

`list` and `dict` with homogeneous types yield better Go types (`[]int`, `map[string]string`). Heterogeneous collections default to `interface{}`.

**Good:**
```python
nums = [1, 2, 3]  # -> []int
ages = {"alice": 30, "bob": 25}  # -> map[string]int
```

**Mixed:**
```python
mixed = [1, "two", 3.0]  # -> []interface{}
```

### 9. Avoid Mutable Default Arguments

Python's `def f(x=[])` is a trap; the default is shared. In Go, default arguments are not supported at all, so such patterns will require manual handling anyway. Avoid defaults, or use `None` and set inside.

### 10. Keep Classes Simple

Classes should mainly contain data attributes assigned in `__init__` and simple methods. Avoid complex inheritance, descriptors, properties, and magic methods beyond `__init__`.

**Good:**
```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def distance(self) -> float:
        return (self.x**2 + self.y**2)**0.5
```

### 11. Use `os` and `fmt` Packages

When interacting with the file system or formatting, Python's `os` and `fmt` (print) are supported at the import level. However, specific function calls may need manual adjustment.

### 12. Limit Return Types to Simple Types

Returning tuples (multiple values) is supported in the sense that Go can return multiple values. The converter may handle `return a, b` as `return a, b`. However, tuple literals in other contexts are problematic.

```python
def min_max(nums):
    return min(nums), max(nums)  # This might work if min/max are defined elsewhere.
```

## After Conversion: Manual Refinement

Even with perfect input, the generated Go may need adjustments:

1. **Run `gofmt`** to format the code.
2. **Fix `while` loops** if present: replace `while condition {` with `for condition {`.
3. **Replace stub imports**: If you used unsupported stdlib modules, replace calls with proper Go equivalents.
4. **Add error handling**: Convert any Python exceptions to Go error returns. For `panic` calls from `raise`, consider whether they should be `return err`.
5. **Strengthen types**: Replace `interface{}` with concrete types where possible.
6. **Add missing imports**: The converter adds imports based on Python imports, but if you introduced new Go functions (e.g., `strconv.Atoi`), you must add `import "strconv"`.
7. **Check for variable scoping issues**: Ensure variables declared inside blocks are not incorrectly used outside.
8. **Review method receivers**: The converter uses pointer receivers `(c *ClassName)`. If methods do not modify the receiver, consider using value receivers for efficiency.
9. **Rename methods**: Python's `snake_case` is preserved (e.g., `my_method`). Go prefers `CamelCase` for exported methods. Adjust as needed.
10. **Add tests**: Write Go tests to verify behavior matches the original Python code.

## Example Workflow

1. Write clean Python code with type hints.
2. Run converter: `python-to-go-converter convert input.py --output output.go --verbose`
3. Inspect `output.go` for comments indicating unsupported features.
4. Fix any `while` loops.
5. Replace any placeholder or stub functions (e.g., `internal/enumerate`).
6. Add proper error handling where `panic` appears (unless panic is intended).
7. Run `go build output.go` to compile; address errors.
8. Add missing imports based on compiler errors.
9. Run `go test` if you have a test suite.
10. Refactor to improve idiomatic Go (use `go vet`, `golint`).

## Conclusion

Treat the converter as a **boilerplate generator**, not a fully automated migration tool. Its value is in producing a first draft that captures the control flow and data structure layout. Human refinement is essential for robust, production-ready Go code.
