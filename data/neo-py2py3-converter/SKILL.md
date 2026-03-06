---
name: py2py3-converter
description: Automatically converts legacy Python 2 code to Python 3 with compatibility checks and test generation.
version: 1.0.0
triggers:
  - "Convert this Python 2 code to Python 3"
  - "Upgrade this legacy script to Python 3"
  - "Fix Python 2 to 3 compatibility issues"
  - "Automate Python 2 to 3 migration"
  - "Generate tests for Python 3 converted code"
  - "Transform this script using 2to3"
---

# py2py3-converter

## 1. Introduction

**py2py3-converter** is an OpenClaw skill that automatically converts legacy Python 2 code to modern Python 3 syntax. It handles the most common migration patterns, generates compatibility reports, and creates unit tests for the converted code.

Python 2 reached end-of-life on January 1, 2020, yet many codebases still contain Python 2 code. This skill automates the tedious work of manual migration, reducing human error and accelerating the upgrade process.

## 2. Core Capabilities

### Conversion Logic
The converter handles these Python 2 → 3 transformations:
- `print` statements → `print()` function calls
- `raw_input()` → `input()`
- `xrange()` → `range()`
- `unicode()` → `str()`
- `basestring` → `str`
- `long` type → `int`
- `dict.has_key(k)` → `k in dict`
- `except Exception, e` → `except Exception as e`
- `raise ValueError, "msg"` → `raise ValueError("msg")`
- Integer division `/` awareness
- `__future__` import removal
- `iteritems()` / `itervalues()` / `iterkeys()` → `items()` / `values()` / `keys()`
- `reduce()` → `functools.reduce()`

### Compatibility Checking
After conversion, a compatibility report is generated listing:
- Warnings for patterns that may need manual review
- Errors for constructs that could not be safely converted
- Informational notes about behavior changes

### Test Generation
For each converted file, a companion pytest test file is generated that:
- Validates syntax correctness of converted code
- Tests key functions for expected behavior
- Covers detected edge cases

## 3. Edge Cases Handling

### Print Statements
- `print "hello"` → `print("hello")`
- `print "a", "b"` → `print("a", "b")`
- `print >> sys.stderr, "err"` → `print("err", file=sys.stderr)`
- `print()` already valid → left unchanged

### String/Bytes Compatibility
- `u"string"` prefix → `"string"` (default in Python 3)
- Warns about `b"bytes"` patterns that may need review
- `basestring` references → `str`

### Import Resolution
- `from __future__ import print_function` → removed (default in Python 3)
- `import urllib2` → `import urllib.request`
- `import ConfigParser` → `import configparser`
- `reduce` → adds `from functools import reduce`

## 4. CLI Interface

### Command Syntax
```bash
# Convert a file
node scripts/cli.js convert --input path/to/py2file.py --output path/to/py3file.py

# Convert from stdin
cat py2file.py | node scripts/cli.js convert

# Convert and generate tests
node scripts/cli.js convert --input file.py --output converted.py --generate-tests

# Show compatibility report only
node scripts/cli.js check --input file.py
```

### Exit Codes
- `0` - Conversion successful, no errors
- `1` - Conversion completed with warnings
- `2` - Conversion failed due to errors

## 5. Integration

### OpenClaw Agent Workflow
Agents invoke the skill via the CLI interface. The standard workflow:
1. Agent receives Python 2 code from user
2. Agent calls `node scripts/cli.js convert --input <file>`
3. Skill returns converted code + compatibility report
4. Agent presents results to user

### API Contract
**Input:**
```json
{
  "code": "print 'hello world'",
  "options": {
    "generateTests": false,
    "keepWarnings": true
  }
}
```

**Output:**
```json
{
  "convertedCode": "print('hello world')",
  "issues": [
    {
      "type": "info",
      "line": 1,
      "message": "Converted print statement to function call"
    }
  ]
}
```
