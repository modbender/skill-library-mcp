# Standard Library Equivalents

## Introduction

When converting Python code to Go, the `import_handler` module translates Python standard library imports to their corresponding Go packages. This document details the currently supported mappings and highlights any behavioral differences.

## Mapping Table

The mapping is defined in `references/stdlib_equivalents.json`. The following modules are supported:

| Python Module       | Go Import Path        | Description |
|---------------------|-----------------------|-------------|
| `os`                | `os`                  | File system operations, environment variables, process management. |
| `sys`               | `sys`                 | System-specific parameters and functions (limited). |
| `json`              | `encoding/json`       | JSON encoding and decoding. |
| `math`              | `math`                | Basic mathematical functions. |
| `strings`           | `strings`             | String manipulation utilities. |
| `fmt`               | `fmt`                 | Formatted I/O (mostly used by `print`). |
| `time`              | `time`                | Time and date operations. |
| `io`                | `io`                  | Basic I/O interfaces. |
| `os.path`           | `path/filepath`       | Path manipulation (POSIX vs Windows differences). |

## Behavioral Notes

### `os`

- The `os` package in Go provides similar functionality to Python's `os`. However:
  - File operations: `os.Open`, `os.ReadFile`, `os.WriteFile` replace `open`, `read`, `write`.
  - The converter does **not** automatically rewrite `os` method calls; it only translates the import. The actual function calls must be manually adapted or may be unsupported.
  - The current scope of conversion covers only the import translation and simple `print` statements, not deep API rewrites.

### `sys`

- Only a subset of `sys` may be mapped. For example, `sys.argv` is not translated; Go uses `os.Args`. Import mapping only.

### `json`

- Python's `json` module functions (`loads`, `dumps`, `load`, `dump`) map to `encoding/json` functions (`Unmarshal`, `Marshal`, `NewDecoder`, `NewEncoder`). The API is different; conversion of calls is not currently performed automatically. The import is provided for when you manually write Go code.

### `math`

- Most mathematical constants and functions have analogs. Function names are similar but may differ in casing (Go uses `Sin`, `Cos`, etc.). Conversion of `math.sqrt(x)` would require rewriting to `math.Sqrt(x)` — not automatic.

### `strings`

- Functions like `strings.ToUpper`, `strings.Join`, `strings.Split` have similar counterparts in Python's `str` methods. Import mapping only.

### `path/filepath` (from `os.path`)

- `os.path.join` becomes `path.Join`. `os.path.dirname` becomes `path.Dir`. However, automatic rewriting of these calls is not implemented; the import is provided for manual use.

## Unsupported Modules

Modules not listed in the mapping will trigger error `E002` ("Unsupported library") during conversion. The converter will still attempt to generate Go code but will skip those imports. It is recommended to either remove unsupported imports or provide fallback stubs.

## Extending the Mapping

The `stdlib_equivalents.json` file can be extended to include additional mappings. For third-party Python libraries, there is no automatic Go equivalent; manual rewrites are required.

## Example

```python
import os
import json
import math

def read_config(path):
    with open(path) as f:
        return json.load(f)
```

Converted Go (illustrative only; `with` is not supported, so this code would not fully convert):

```go
package main

import (
    "os"
    "encoding/json"
    "math"
)

func readConfig(path string) interface{} {
    // Note: with statement not supported; manual rewrite needed
    // content, err := os.ReadFile(path)
    // ...
    return nil
}
```

In this example, the import statements are automatically derived. However, the body of `read_config` contains unsupported features (`with`, `json.load`) and would be partially translated or flagged.

## Best Practices

- Prefer standard library APIs that have direct Go equivalents.
- Avoid complex or obscure modules if conversion is the goal.
- Use explicit type hints to improve type inference.
- When an import is unsupported, consider refactoring to a supported alternative.
