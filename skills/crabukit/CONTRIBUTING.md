# Contributing to Crabukit

Thank you for your interest in contributing to Crabukit! This document provides guidelines and instructions for contributing.

## 🐛 Reporting Issues

### Bug Reports

Please include:
- Crabukit version (`crabukit --version`)
- Python version (`python --version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Sample skill that triggers the issue (if applicable)

### Security Vulnerabilities

**Do not open public issues for security vulnerabilities.**

Instead, use GitHub's private vulnerability reporting:
https://github.com/tnbradley/crabukit/security/advisories

Or open a private discussion with the maintainer.

## 💡 Feature Requests

We welcome feature requests! Please open an issue with:
- Clear description of the feature
- Use case / why it's needed
- Proposed implementation (if you have ideas)

## 🔧 Development Setup

```bash
# Clone the repo
git clone https://github.com/tnbradley/crabukit.git
cd crabukit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check .
black --check .
```

## 📝 Code Style

- **Formatter**: [Black](https://github.com/psf/black) (line length 100)
- **Linter**: [Ruff](https://github.com/astral-sh/ruff)
- **Type hints**: Required for new code
- **Docstrings**: Google style

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=crabukit --cov-report=html

# Run specific test file
pytest tests/test_python_analyzer.py
```

## 🏗️ Adding New Detection Rules

To add a new security check:

1. **Add the pattern** to `crabukit/rules/patterns.py`:
```python
"my_new_pattern": {
    "pattern": r"regex_here",
    "severity": Severity.HIGH,
    "title": "Descriptive title",
    "description": "What this detects and why it's dangerous",
    "remediation": "How to fix it",
    "cwe": "CWE-XXX",  # Optional
}
```

2. **Implement the check** in the appropriate analyzer
3. **Add a test case** in `tests/fixtures/`
4. **Update documentation** in `docs/rules.md`

## 📋 Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

### PR Checklist

- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] New rules have test cases
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

## 🎯 Priority Areas

We especially welcome contributions in:

- **New detection rules** for emerging AI threats
- **Performance improvements** for large skills
- **Better false positive reduction**
- **Additional output formats** (SARIF, JUnit XML)
- **Documentation improvements**
- **CI/CD integrations**

## 💬 Community

- GitHub Discussions: [github.com/tnbradley/crabukit/discussions](https://github.com/tnbradley/crabukit/discussions)
- Issues: [github.com/tnbradley/crabukit/issues](https://github.com/tnbradley/crabukit/issues)

## 📜 Code of Conduct

Be respectful, constructive, and inclusive. We're all here to make AI safer.

---

Thank you for contributing to safer AI! 🦀🔒
