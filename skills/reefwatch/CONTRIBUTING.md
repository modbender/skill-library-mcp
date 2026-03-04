# Contributing to ReefWatch

Thanks for your interest in contributing to ReefWatch!

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/reefwatch.git
   cd reefwatch
   ```
3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```
4. Download detection rules:
   ```bash
   python setup_rules.py
   ```

## Running Tests

```bash
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=reefwatch
```

## Making Changes

1. Create a feature branch: `git checkout -b my-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/ -v`
5. Commit with a clear message
6. Push and open a Pull Request

## Code Style

- Follow existing patterns in the codebase
- Keep functions focused and small
- Add docstrings to public classes and functions
- Use type hints where practical

## Custom Rules

You can contribute detection rules by adding JSON files to `rules/custom/`. See the README for the rule format.

## Reporting Issues

Open an issue on GitHub with:
- Steps to reproduce
- Expected vs actual behavior
- Platform (Linux/macOS) and Python version
