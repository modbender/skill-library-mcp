---
name: critpt-solver
description: Validates and executes Python solutions for CritPt benchmark problems. Use when the user asks to check a generated solution or run a test case.
---

# CritPt Solver

Wraps Python execution for CritPt problems.

## Usage

```javascript
const solver = require('./index');
const code = "..."; // Python code implementing answer(p)
const result = await solver.runPythonCode(code);
console.log(result);
```

## How it works

1.  **Format Prompt**: Creates a structured prompt for the LLM to generate Python code.
2.  **Generate Code**: (Optionally calls LLM, or expects LLM to call it).
3.  **Validate**: Checks syntax and executes `answer(p)` with test values if possible.
