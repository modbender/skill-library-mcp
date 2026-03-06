---
name: tdd-helper
description: Lightweight helper to enforce TDD-style loops for non-deterministic agents.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["python3", "pytest"] },
      "category": "development"
    }
  }
---

# tdd-helper

Lightweight helper to enforce TDD-style loops for non-deterministic agents.

## Features
- `tdd.py` wraps a task: fails if tests are absent or failing, refuses to run "prod" code first.
- Watches for lint/warnings (optional) and blocks on warnings-as-errors.
- Simple config via env or JSON.

## Usage
```bash
# Define tests in tests/ or specify via --tests
python tdd.py --tests tests/ --run "python your_script.py"
```
