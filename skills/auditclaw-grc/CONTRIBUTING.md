# Contributing to AuditClaw GRC

Thank you for your interest in contributing! This document explains how to get started.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/auditclaw-grc.git`
3. Create a feature branch: `git checkout -b feature/your-feature`

## Development Setup

```bash
cd skills/auditclaw-grc
pip install -r scripts/requirements.txt
pip install -r requirements-dev.txt
python3 -m pytest tests/ -v
```

All 431 tests should pass before submitting changes.

## Project Structure

- `skills/auditclaw-grc/` -- The main skill (installable via ClawHub)
- `companion-skills/` -- Companion skills for cloud integrations
- `docs/` -- Documentation

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

### Suggesting Features

Open an issue with the "enhancement" label describing the use case and proposed solution.

### Code Contributions

1. Make changes in your feature branch
2. Write tests for new functionality (see `skills/auditclaw-grc/tests/`)
3. Ensure all tests pass: `cd skills/auditclaw-grc && python3 -m pytest tests/ -v`
4. Submit a pull request with a clear description

### Adding a New Database Action

1. Add the action function in `skills/auditclaw-grc/scripts/db_query.py` following the `action_<name>(conn, args)` pattern
2. Add argparse arguments in the argument parser section
3. Add the action name to the `ACTIONS` dispatch dictionary
4. Write tests in a new or existing test file
5. Update `skills/auditclaw-grc/references/db-actions.md` with the action reference
6. Add the command to the Quick Command Reference in `skills/auditclaw-grc/SKILL.md`

### Adding a New Framework

1. Create the JSON definition at `skills/auditclaw-grc/assets/frameworks/<slug>.json`
2. Follow the schema: `{id, name, version, description, domains: [{id, name, controls: [{id, title, description, category, priority, typical_evidence, mappings}]}]}`
3. Optionally add a reference guide at `skills/auditclaw-grc/references/frameworks/<slug>.md`
4. Add tests in `skills/auditclaw-grc/tests/`
5. Update the framework table in SKILL.md and the root README.md

### Building a Companion Skill

See [docs/DEVELOPING.md](docs/DEVELOPING.md) for the companion skill architecture and integration pattern.

## Code Style

- Python 3.8+ compatible
- All `db_query.py` actions return JSON to stdout
- Tests use subprocess to invoke scripts (black-box testing pattern)
- No external runtime dependencies beyond `requests` (for header scanning)
- Keep SKILL.md body comprehensive -- it serves as the AI agent's instruction manual

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
