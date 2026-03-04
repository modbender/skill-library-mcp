# Error Codes

This document provides detailed explanations for all error codes emitted by the Python-to-Go converter. Understanding these codes helps users diagnose conversion failures and adjust their Python code accordingly.

## E001: Unsupported Python syntax

**Message:** `Unsupported Python syntax: {feature}`

**Description:** The converter encountered a Python language feature that is not implemented. The `{feature}` placeholder indicates the name of the unsupported construct (e.g., "async function", "list comprehension", "with statement").

**Common Causes:**
- Use of `async` / `await`
- `with` context managers
- List/dict/set comprehensions
- Generator expressions
- Metaprogramming (`eval`, `exec`, `setattr` on types)
- Decorators (some are supported but may produce warnings)
- Certain complex expressions

**Resolution:** Rewrite the code to avoid unsupported features. Often, an equivalent construct using basic loops and conditionals can be used. For example, replace list comprehensions with explicit `for` loops.

---

## E002: Unsupported library

**Message:** `Unsupported library: {library}`

**Description:** The Python import `{library}` has no known Go equivalent mapping in `stdlib_equivalents.json`.

**Common Causes:**
- Importing third-party libraries (e.g., `numpy`, `pandas`, `requests`)
- Importing standard library modules that have not been mapped (e.g., `re`, `collections`, `itertools`)
- Misspelled module names

**Resolution:** Remove or replace unsupported imports. For missing stdlib modules, consider adding a mapping to `stdlib_equivalents.json` if a suitable Go package exists. For third-party libraries, you may need to write the corresponding Go code manually.

---

## E003: Type inference failed

**Message:** `Type inference failed for expression: {expr}`

**Description:** The type inference engine could not determine a Go type for the given expression. The `{expr}` placeholder shows a snippet of the expression (or its AST node type).

**Common Causes:**
- Expressions with mixed types that cannot be resolved (e.g., adding a string to an int)
- Lambda expressions with no type hints
- Dynamic attribute access (`getattr`, arbitrary attribute on a variable)
- Complex nested structures with inconsistent element types

**Resolution:** Provide explicit type annotations in the Python code. For ambiguous expressions, break them into smaller steps with typed variables.

---

## E004: Invalid output path

**Message:** `Invalid output path: {path}`

**Description:** The specified output file path is not writable. The path may be a directory, lack write permissions, or the filesystem may be full.

**Resolution:** Choose a different output file location, ensure the directory exists and is writable, or output to stdout by omitting `--output`.

---

## E005: Input file not found

**Message:** `Input file not found: {path}`

**Description:** The Python source file specified as input does not exist at the given path.

**Resolution:** Provide a correct path to an existing `.py` file.

---

## E006: Go compilation failed

**Message:** `Go compilation failed: {error}`

**Description:** The generated Go code was written to a file, but when `go vet` or `go build` was attempted (if `--check` flag is used), compilation failed. The `{error}` contains the compiler output.

**Common Causes:**
- Generated code contains syntax errors (unlikely but possible for unsupported features)
- Missing imports for used functions
- Incorrect type conversions
- Use of features that cannot be directly represented in Go

**Resolution:** Examine the generated `.go` file to identify issues. Consider adjusting the Python code to use supported constructs, or report a bug if the generated code is valid but the compiler rejects it incorrectly.

---

## Non-Zero Exit Codes

The converter exits with the numeric part of the error code (e.g., `E001` → exit code 1). A successful conversion exits with code `0`.

## Diagnostics

For more insight, run the converter with the `--verbose` flag. It prints:
- Detected Python imports
- Resolved Go imports
- Warnings about unsupported features that are skipped

## Troubleshooting Checklist

1. **Unsupported syntax?** Look for `E001` and refactor code to avoid the indicated feature.
2. **Library not found?** Check `E002` and remove or replace the import.
3. **Type errors?** Add type hints or break complex expressions.
4. **Compilation fails?** Inspect generated Go file. Ensure you have a recent Go version.
5. **Blank or incomplete output?** Verify the input file contains supported statements; unsupported statements are replaced with comments.

## Reporting Issues

If you encounter an error that you believe is incorrect or the converter should handle, please provide:
- The original Python code
- The full error message and exit code
- The generated Go output (if any)
- The verbose log (`--verbose`)

Submit issues via the skill repository's issue tracker.
