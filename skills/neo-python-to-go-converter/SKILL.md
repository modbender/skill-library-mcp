---
name: python-to-go-converter
description: Automatically converts Python code to optimized Go code for performance-critical applications.
---

# SKILL.md — Python to Go Converter

## Overview

This skill automatically converts Python source code to idiomatic, compilable Go code. It handles type mappings, import translations, and produces clean Go output suitable for performance-critical applications.

## Capabilities

- Convert Python source files to Go with preserved functionality
- Intelligent Python-to-Go type mapping (int, str, list, dict, classes, etc.)
- Translate common Python standard library imports to Go equivalents
- Generate properly formatted Go code with comments
- Provide detailed error diagnostics for unsupported Python features
- CLI interface for batch conversion and agent integration
- Support for functions, classes, control flow, and basic data structures

## Installation

The skill is installed as part of an OpenClaw skill package. Ensure dependencies are met (Python 3.8+, `go` compiler in PATH).

## Usage

### CLI Invocation

```bash
python-to-go-converter convert <input.py> [--output <output.go>]
```

### Agent Integration

The skill exposes a single-turn execution model. Provide Python code as input, receive Go code as output.

### Examples

```bash
# Convert a single file
python-to-go-converter convert examples/basic.py --output output.go

# Convert with diagnostics
python-to-go-converter convert myscript.py --verbose
```

## Error Handling

The converter produces non-zero exit codes on failure and writes diagnostics to stderr. Common errors include:
- Unsupported Python syntax (decorators, metaclasses, async generators)
- Library dependencies without Go equivalents
- Type inference failures

See `error_codes.json` for the full error catalog.

## Files

- `scripts/converter.py` — Main CLI and conversion orchestration
- `scripts/ast_parser.py` — Python AST parsing and analysis
- `scripts/go_generator.py` — Go code emission and formatting
- `scripts/type_mapper.py` — Type system translation rules
- `scripts/import_handler.py` — Import resolution and library mapping
- `references/python_to_go_mappings.json` — Feature mapping table
- `references/stdlib_equivalents.json` — Standard library translations
- `references/error_codes.json` — Error code definitions
- `examples/` — Example conversions and test cases
- `tests/` — Unit tests and validation suite

## Limitations

- Does not convert GUI frameworks (Tkinter, PyQt)
- No support for dynamic metaprogramming (eval, exec, setattr magic)
- Machine learning libraries (NumPy, TensorFlow) require manual rewrite
- Perfect 1:1 runtime behavior is not guaranteed; testing required

## Performance

Typical conversion times: small scripts (<100 LOC) < 1s; medium (500 LOC) ~2-3s; large codebases scale linearly. Conversion is CPU-bound on Python parsing and AST traversal.

## Support

For issues, feature requests, or contributions, refer to the skill repository.
