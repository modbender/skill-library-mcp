# Dependency Update Checker

A command-line tool to check for outdated dependencies across multiple package managers (npm, pip, poetry).

## Installation

This skill requires:
- Python 3.x
- **npm**: For checking Node.js dependencies (`npm outdated`)
- **pip**: For checking Python dependencies (`pip list --outdated`)
- **poetry**: Optional, for Poetry projects (`poetry show --outdated`)

Ensure these tools are installed and available in your PATH.

## Quick Start

```bash
# Check all dependencies in current directory
python3 scripts/main.py check

# Check only npm dependencies
python3 scripts/main.py check --manager npm

# Check only pip dependencies
python3 scripts/main.py check --manager pip

# JSON output format
python3 scripts/main.py check --format json
```

## Command Reference

```
python3 scripts/main.py check [OPTIONS]
```

Options:
- `--manager`: Specify package manager(s) to check. Can be one or more of: `npm`, `pip`, `poetry`. Default: check all detected.
- `--format`: Output format: `table` (human-readable) or `json`. Default: `table`.
- `--path`: Path to project directory. Default: current directory.
- `--ignore-errors`: Continue checking other managers if one fails. Default: false.
- `--timeout`: Timeout in seconds for each package manager check. Default: 30.

## How It Works

1. **Detects package manager files** in the current directory:
   - `package.json` → npm
   - `requirements.txt` or `Pipfile` → pip
   - `pyproject.toml` (with poetry section) → poetry

2. **Runs appropriate commands**:
   - `npm outdated --json` for npm projects
   - `pip list --outdated --format=json` for pip projects
   - `poetry show --outdated --no-ansi` for poetry projects

3. **Parses output** and presents in consistent format

## Examples

### Basic Usage

```bash
cd /path/to/node-project
python3 scripts/main.py check
```

Output:
```
Checking dependencies...
[✓] Found package.json
[✓] Running npm outdated...
┌─────────────────┬─────────┬─────────┬─────────┬──────────────┐
│ Package         │ Current │ Wanted  │ Latest │ Package Type │
├─────────────────┼─────────┼─────────┼─────────┼──────────────┤
│ express         │ 4.17.1  │ 4.18.0  │ 4.18.0  │ dependencies │
│ lodash          │ 4.17.20 │ 4.17.21 │ 4.17.21 │ dependencies │
└─────────────────┴─────────┴─────────┴─────────┴──────────────┘
```

### Multiple Projects

```bash
# Check a Python project
cd /path/to/python-project
python3 scripts/main.py check --manager pip

# Output:
Checking dependencies...
[✓] Found requirements.txt
[✓] Running pip list --outdated...
┌─────────────────┬─────────┬─────────┐
│ Package         │ Current │ Latest  │
├─────────────────┼─────────┼─────────┤
│ requests        │ 2.28.1  │ 2.31.0  │
│ flask           │ 2.2.3   │ 2.3.0   │
└─────────────────┴─────────┴─────────┘
```

### JSON Output for Scripting

```bash
python3 scripts/main.py check --format json
```

Output:
```json
{
  "npm": [
    {
      "package": "express",
      "current": "4.17.1",
      "wanted": "4.18.0",
      "latest": "4.18.0",
      "type": "dependencies"
    }
  ],
  "pip": [
    {
      "package": "requests",
      "current": "2.28.1",
      "latest": "2.31.0"
    }
  ]
}
```

## Error Handling

- If a package manager is not installed, the tool skips it with a warning
- If a package manager command fails, the tool shows the error and continues (with `--ignore-errors`)
- Network timeouts can be configured with `--timeout`
- Missing package manager files are reported but don't cause failure

## Limitations

- **npm**: Requires npm 5+ for JSON output support. Falls back to text parsing for older versions.
- **pip**: Requires pip 20.3+ for JSON output support. Falls back to text parsing for older versions.
- **poetry**: Always uses text parsing (no JSON output available).
- **Performance**: Network-dependent. Checking remote registries can be slow.
- **Private registries**: May not work with private npm/pypi registries without authentication.
- **Monorepos**: Only checks root package.json/requirements.txt by default.
- **Lock files**: Does not check package-lock.json or poetry.lock for exact versions.

## Development

The tool is designed to be extensible. To add support for additional package managers:

1. Add detection logic in `detect_package_managers()`
2. Add check function following the pattern `check_<manager>()`
3. Add parser function to handle command output

## License

MIT