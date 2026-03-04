---
name: py-memory-optimizer
description: Automatically analyzes Python code and suggests memory usage optimizations for improved performance
---

# py-memory-optimizer Skill

## Overview

This skill provides static analysis of Python code to identify memory-intensive patterns, potential memory leaks, and optimization opportunities. It generates actionable suggestions with estimated memory savings and best practice recommendations.

## Core Capabilities

- **Static Code Analysis**: Parses Python source files using the AST module to analyze code structure without execution
- **Pattern Detection**: Identifies common memory-intensive patterns (large list comprehensions, unnecessary object creation, improper generator usage)
- **Leak Detection**: Finds potential memory leaks from circular references, unclosed resources, and global variable accumulation
- **Optimization Suggestions**: Provides specific, actionable recommendations with estimated memory impact
- **Framework Support**: Handles Python 3.8+ and common frameworks (Django, Flask, FastAPI patterns)
- **CLI Interface**: Command-line tool for integration into development workflows
- **Report Generation**: Creates detailed analysis reports in multiple formats (JSON, markdown, plain text)

## Dependencies

### System Requirements
- Python 3.8+
- pip package manager

### Python Packages (installed automatically via package.json)
- astroid (optional, for enhanced AST analysis)
- tabulate (for formatted output)
- rich (for colored terminal output)
- click (for CLI interface)
- pydantic (for data validation)
- python-slugify (for report naming)

## Installation

```bash
npm install --global openclaw-skill-py-memory-optimizer
```

The skill will automatically install Python dependencies on first run.

## Usage

### CLI Interface

```bash
# Analyze a single file
py-memory-optimizer analyze path/to/script.py

# Analyze entire directory
py-memory-optimizer analyze ./my_project --recursive

# Generate detailed report
py-memory-optimizer analyze script.py --format json --output report.json

# Show optimization suggestions with memory estimates
py-memory-optimizer analyze script.py --show-suggestions --estimate-savings

# Exclude specific patterns
py-memory-optimizer analyze . --exclude "*.test.py" "*/migrations/*"

# Version info
py-memory-optimizer --version
```

### Integration with OpenClaw Agents

The skill can be called directly by OpenClaw agents:

```
Analyze this Python code for memory optimizations: <code>
```

The agent will invoke the analyzer and return structured suggestions.

## Output Format

The analyzer produces:

1. **Memory Issue Summary**: Count of issues by severity (critical, high, medium, low)
2. **Detailed Findings**: For each issue:
   - File and line number
   - Issue type and description
   - Memory impact estimate
   - Specific optimization suggestion with code example
3. **Overall Statistics**: Total memory potentially saved, number of objects analyzed
4. **Best Practices Checklist**: Compliance with Python memory optimization guidelines

## Examples

### Example 1: Large List Comprehension

**Input:**
```python
# Bad: Creates entire list in memory
result = [process(item) for item in huge_dataset]
```

**Output:**
```
Line 15: Medium memory issue
  Pattern: Large list comprehension
  Current memory: ~O(N) for full list
  Suggestion: Use generator expression
  Optimized: (process(item) for item in huge_dataset)
  Estimated savings: 70-90% for large datasets
```

### Example 2: Unclosed File Handles

**Input:**
```python
f = open('data.txt', 'r')
data = f.read()
# Missing f.close()
```

**Output:**
```
Line 8: High memory/resource issue
  Pattern: Unclosed file handle
  Risk: File descriptor leak, memory not freed
  Suggestion: Use context manager
  Optimized: with open('data.txt', 'r') as f:
                 data = f.read()
  Estimated savings: Prevents descriptor accumulation
```

## Out of Scope

- Runtime profiling (use memory_profiler for that)
- C extension analysis
- Database or external service optimization
- Automatic code modification (this skill only suggests)
- Mixed-language project optimization

## Files

This skill provides:

- `SKILL.md`: This documentation
- `package.json`: NPM package definition
- `README.md`: Quick start guide
- `scripts/main.py`: CLI entry point
- `scripts/analyzer.py`: Core analysis engine
- `scripts/optimizer.py`: Suggestion generator
- `scripts/utils.py`: AST utilities and helpers
- `references/memory_patterns.md`: Pattern reference
- `references/best_practices.md`: Best practices guide
- `assets/sample_code/`: Example files for testing

## License

MIT

## Support

For issues and feature requests, visit: https://github.com/openclaw/skills/issues
