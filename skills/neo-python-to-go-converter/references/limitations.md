# Limitations and Known Issues

This document outlines the current limitations of the Python-to-Go converter, as well as known bugs and missing features. Understanding these constraints is essential before relying on automatic conversion for production code.

## Unsupported Python Features

The following Python constructs are **not** converted and will be either skipped (with a warning comment) or cause an error:

| Feature | Status | Workaround |
|---------|--------|------------|
| Async/await (`async def`, `await`) | Not supported | Remove async, use synchronous code or manual rewrite |
| Context managers (`with` statement) | Not supported | Use explicit `Open`/`Close` or `defer` manually |
| List comprehensions | Not supported | Rewrite as explicit `for` loops |
| Dictionary comprehensions | Not supported | Rewrite with `for` and `map` or `make` |
| Set comprehensions | Not supported | Rewrite using slices and `map` or loops |
| Generator expressions | Not supported | Replace with function that returns slice/channel |
| `yield` and generators | Not supported | Rewrite as function returning slice or channel |
| `eval`, `exec` | Not supported | Remove dynamic code execution |
| `setattr`, `getattr`, `delattr` on arbitrary objects | Not supported | Access fields directly |
| Decorators (`@decorator`) | Ignored | Remove or manually apply equivalent Go patterns |
| Metaclasses | Not supported | Use Go's type system differently |
| `super()` | Not supported | Directly refer to base struct fields or methods |
| `import *` (wildcard imports) | Partially handled | Prefer explicit imports |
| Relative imports (e.g., `from .module import x`) | Not handled | Use absolute imports or adjust GOPATH |
| Default argument values (mutable defaults) | Not translated | Use explicit initialization in function body |
| `*args` and `**kwargs` | Not supported | Define explicit parameters or use `...interface{}` manually |
| Keyword-only arguments | Not supported | Use regular parameters and document |
| Positional-only parameters (PEP 570) | Not supported | Avoid `/` in function signature |
| Multiple inheritance | Not supported | Use composition |
| `is` / `is not` comparisons | Not supported (except `None` may map to `nil`) | Use `==` for value equality, pointer comparison for identity |
| Identity checks on small integers/strings | Not reliable | Avoid identity checks; use equality |
| `iter` and `next` protocol | Partially via `range` | Use `for` loops |
| `enumerate` | Mapped but not implemented | Keep manual counter |
| `zip` | Not supported | Manual loop over indices |
| `map`, `filter`, `reduce` | Not supported | Use `for` loops |
| `slice` object | Not supported | Use explicit indices |
| `bool` subclassing | Not relevant | Go `bool` is primitive |
| Complex numbers (`complex`) | Not supported | Avoid or use manual struct |
| `memoryview` | Not supported | Use slices |
| `property` decorator | Not supported | Use explicit getter/setter methods |
| Class/static methods | Not supported | Define regular functions or methods |
| `__slots__` | Not relevant | Go structs have fixed fields |
| `__dict__`, `__class__`, `__mro__` | Not supported | No reflection equivalent |
| `hasattr`, `setattr` on classes | Not supported | Direct field access |
| `__import__` | Not supported | Avoid dynamic imports |
| `globals()`, `locals()` | Not supported | No direct equivalent |
| `vars()`, `dir()` | Not supported | Use struct field tags or manual serialization |
| `callable()` | Not supported | Use type assertions or interfaces |
| `isinstance`, `issubclass` | Not supported | Use Go's type switches or assertions |
| `@property` setter/deleter | Not supported | Define setter methods |
| `__len__`, `__getitem__`, `__setitem__` | Not directly; mapping to Go methods possible | Implement Go methods manually |
| `__iter__`, `__next__` | Not directly | Use `range`/loops or channels |
| `__enter__`, `__exit__` (context manager protocol) | Not supported | Use `defer` manually |
| `__await__`, `__aiter__`, `__anext__` | Not supported | Avoid async idioms |

### Missing Operators

- Bitwise AND (`&`), OR (`|`), XOR (`^`), NOT (`~`), left shift (`<<`), right shift (`>>`)
- Floor division (`//`)
- Matrix multiplication (`@`) (unlikely)
- In-place operators like `**=` (not in Python either but conceptually)

These operators are omitted from `python_to_go_mappings.json` and will cause an "unsupported operator" fallback.

## API Conversion Gaps

Even if a Python statement is syntactically supported, the conversion of library calls may be incomplete:

- **Standard library function calls** are **not** rewritten. Only the import statements are translated. For example, `os.path.join(a, b)` remains as-is in the output; it must be manually changed to `path.Join(a, b)`.
- **Method calls** on objects are preserved verbatim, which means they will not compile if the method does not exist on the Go type. For instance, a Python list's `.append()` method will appear as `list.append(x)`, but Go slices use `append(list, x)` (a function, not a method). Such mismatches are not handled.
- **String methods** (`str.upper()`, `str.split()`, etc.) are not converted to Go `strings` package functions.
- **JSON** calls (`json.loads`, `json.dumps`) need manual conversion to `json.Unmarshal`/`json.Marshal`.
- **Math** functions (`math.sqrt`) must be changed to `math.Sqrt` (capitalization difference).
- **Printing**: `print()` is converted to `fmt.Println`. However, `print` with multiple arguments works, but `sep` and `end` arguments are ignored.

These gaps mean that after syntax conversion, the semantic layer often requires significant manual rewrite.

## Type System Limitations

- **Dynamic typing**: Python's dynamic nature clashes with Go's static typing. The converter uses `interface{}` as a fallback, which can lead to runtime type assertions in Go.
- **No generics**: The converter does not generate Go generic code (type parameters). Slices and maps use concrete element types when possible but fall back to `interface{}`.
- **Numeric precision**: Python `int` can be arbitrarily large; Go `int` may overflow. For large integers, manual conversion to `int64` or `big.Int` is needed.
- **Float vs int mixing**: Adding an `int` to a `float64` in Go would cause a type mismatch, whereas Python promotes automatically. The converter does not insert explicit conversions; you may need to add `float64(x)` in the Go code.

## Scoping and Name Resolution

- The converter's scope tracking is simplistic. Variables declared in an inner block (e.g., inside an `if` or `for`) may be incorrectly considered available outside the block, leading to Go compilation errors.
- Loop variables in `for` loops are reused across iterations as in Go, but Python semantics (especially with closures) differ; no closure conversion is performed.
- Global variables are treated as package-level variables; cross-module globals are not handled.

## Error Handling

- `try/except` is not converted; any `raise` becomes `panic`. Go's error-return style is not automatically applied. Converting Python exceptions to Go errors requires substantial manual effort.
- `finally` blocks are ignored.

## Code Generation Quality

- **Indentation**: Uses tabs, but may misalign for nested structures.
- **Formatting**: Does not run `gofmt`; generated code should be formatted before committing.
- **Comments**: Python comments are lost. Only converter-generated comments for unsupported features are present.
- **Line numbers**: Not preserved; debugging generated Go against original Python may be difficult.
- **Readability**: The generated Go may not be idiomatic; manual cleanup is expected.

## Performance Considerations

- Conversion time scales linearly with source size. Large codebases (thousands of lines) may take several seconds.
- No incremental or caching mechanism; each run reprocesses the entire file.
- The Python parser (`ast.parse`) is relatively fast, but type inference can become expensive for deeply nested expressions.

## Platform and Dependencies

- Requires Python 3.8+ and the `go` compiler in PATH for `--check`.
- The converter itself is a Python script; no external Python packages are needed (uses only standard library).
- The generated Go code may require additional third-party Go dependencies not accounted for by the import mapping.

## Security Considerations

- The converter does not execute the Python code; it only parses it. However, be cautious when converting untrusted code, as the generated Go may still contain malicious logic.
- The `--check` flag runs `go vet`, which might briefly compile the code; ensure the environment is secure.

## Roadmap

Planned improvements for future versions:

1. **Proper `while` translation**: emit `for condition { ... }`.
2. **Basic `try/except` conversion**: convert `try` block to explicit error checks for known functions (e.g., `os.ReadFile`).
3. **Default arguments**: generate overloads or default values.
4. **`*args` and `**kwargs`**: map to `...interface{}` and proper handling.
5. **`enumerate` helper**: generate a small helper function.
6. **`with` for file operations**: convert to `defer file.Close()`.
7. **List comprehensions**: rewrite as explicit loops.
8. **Type improvements**: detect integer-only slices and use `[]int`.
9. **Better scoping**: respect block boundaries for variable declarations.
10. **Formatting**: pipe output through `gofmt` automatically.
11. **Documentation preservation**: extract docstrings as Go comments.
12. **Configurable output package name** (e.g., `--package`).

## Conclusion

The converter is a useful starting point for migrating simple to moderately complex Python code to Go. It is not a turnkey solution; expect to spend time refining the output, especially for non-trivial codebases. Always review and test the generated Go code thoroughly.
