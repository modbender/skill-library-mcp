# Skill: tdd-helper (forcing function for agents)

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

If tests fail or missing -> stops. If tests pass -> runs the command.

## Config
- `--tests` path (default: tests/)
- `--run` command to execute after tests are green
- `WARN_AS_ERROR=1` to block on pylint/ruff warnings (optional hook)

## Why
For agents whose output varies, TDD is the forcing function to keep quality deterministic: red → green → refactor. This helper makes “no tests, no run” the default.
