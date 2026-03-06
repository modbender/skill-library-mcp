---
name: uv-priority
description: Prioritize uv over pip for all Python package management and execution. When running ANY Python command or CLI tool (python, dbt, pytest, etc.), MUST wrap with uv run.
license: MIT
metadata:
  always: true
  emoji: "⚡"
  homepage: https://github.com/marcoracer/uv-priority
  os: [darwin, linux, windows]
  tags: [python, uv, pip, package-management, dbt]
  requires:
    anyBins: [uv]
---

# UV Priority

## CRITICAL: Always Wrap Python Commands with uv or uvx

This is a **mandatory skill** for all Python-related tasks. When the user mentions Python, dbt, or ANY Python package, you **MUST**:

1. **NEVER** run Python commands directly (python, python3, dbt, pytest, etc.)
2. **ALWAYS** wrap them with `uv run` or `uvx`
3. **NEVER** install packages with `pip install`
4. **ALWAYS** use `uv add` or `uv pip install`

## uv run vs uvx: When to Use Each

| Command | When to Use | Example |
|---------|-------------|---------|
| `uv run <tool>` | **Ferramenta do projeto** - precisa importar seus módulos, usada regularmente | `uv run pytest tests/` |
| `uvx <tool>` | **Utilitário externo** - usa Python como runtime, mas não é parte do seu app | `uvx ruff check .` |

### Quick Decision Guide

```
Preciso rodar uma ferramenta Python?
├─ A ferramenta precisa importar meus módulos do projeto?
│  └─ SIM → uv run <comando>
└─ A ferramenta só analisa/transforma código externo?
   └─ SIM → uvx <comando>
```

### Use `uvx` for External Tools

`uvx` creates a temporary, isolated environment. Use it for tools that:

- Analyze code without importing project modules (linters, formatters, type checkers)
- Are one-off utilities not tied to your project
- Shouldn't pollute your project's dependencies

```bash
uvx ruff check .          # Linter - analisa sintaxe, não importa seus módulos
uvx black .               # Formatter - manipula texto, não importa seus módulos
uvx mypy .                # Type checker - analisa tipos, não precisa rodar seu código
uvx isort .               # Organizador de imports - só lê arquivos
uvx ruff@latest check .   # Use specific version
```

### Use `uv run` for Project Tools

`uv run` uses your project's existing virtual environment. Use it for tools that:

- Need to import your project modules
- Are part of your development workflow with project dependencies
- Run tests or your application

```bash
uv run pytest tests/      # Test runner - precisa importar seus módulos
uv run python main.py     # Sua aplicação
uv run python -m myapp.cli  # CLI do seu app
uv run dbt run            # dbt com suas transformações do projeto
```

### Rule of Consistency

> **If the project already uses `uv run` for a specific tool, continue using it.**

- If you see `uv run ruff check .` in the project, don't change to `uvx`
- If the user specified `uv run pytest`, maintain the pattern
- **Project consistency takes precedence** over the "ideal rule"

Why? Changing from `uv run` to `uvx` (or vice-versa) mid-project can:
- Break scripts/CI that expect the specific command
- Confuse other developers
- Create unnecessary inconsistency

### Command Translation Rules

| NEVER run this | ALWAYS run this instead |
|----------------|------------------------|
| `python script.py` | `uv run python script.py` |
| `python -c "import..."` | `uv run python -c "import..."` |
| `python -m module` | `uv run python -m module` |
| `python3 script.py` | `uv run python3 script.py` |
| `dbt --version` | `uv run dbt --version` |
| `dbt run` | `uv run dbt run` |
| `dbt debug` | `uv run dbt debug` |
| `dbt deps` | `uv run dbt deps` |
| `pytest` | `uv run pytest` (imports project modules) or `uvx pytest` (one-off) |
| `pytest tests/` | `uv run pytest tests/` (imports project modules) or `uvx pytest tests/` (one-off) |
| `black .` | `uvx black .` (preferred - external tool) or `uv run black .` (if already in project) |
| `ruff check .` | `uvx ruff check .` (preferred - external tool) or `uv run ruff check .` (if already in project) |
| `mypy .` | `uvx mypy .` (preferred - external tool) or `uv run mypy .` (if already in project) |
| `pip install <package>` | `uv add <package>` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |

## When to Use

Use when:
- Installing ANY Python package or dependency (for ANY Python app: web apps, scripts, data processing, dbt, ML, etc.)
- Setting up Python projects (web apps like Flask/Django/FastAPI, data science, ML, automation, dbt, etc.)
- Installing dependencies for ANY Python-based application
- Creating virtual environments
- Running Python scripts
- Running tests (pytest, unittest, etc.)
- Using dbt commands (dbt-core, dbt-snowflake, etc.)
- ANY task involving Python packages or dependencies

## Command Substitutions (MANDATORY)

NEVER use these pip commands. ALWAYS use the uv equivalent:

| NEVER use pip | ALWAYS use uv |
|---------------|---------------|
| `pip install <package>` | `uv add <package>` |
| `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| `pip list` | `uv pip list` |
| `pip freeze` | `uv pip freeze` |

### Popular Python Tools with CLI

These are commonly installed Python packages that have CLI commands. When installing or running them, always use `uv`:

| Tool | Install with uv | Run with uv (project) | Run with uvx (external) |
|------|----------------|------------------------|--------------------------|
| **dbt** (dbt-core) | `uv add dbt-snowflake` (or dbt-postgres) | `uv run dbt <command>` | - |
| **pytest** | `uv add pytest` | `uv run pytest` (imports project modules) | `uvx pytest` (one-off) |
| **black** (formatter) | `uv add black` | `uv run black` (if in project) | `uvx black .` (preferred) |
| **ruff** (linter) | `uv add ruff` | `uv run ruff` (if in project) | `uvx ruff check .` (preferred) |
| **mypy** (type checker) | `uv add mypy` | `uv run mypy` (if in project) | `uvx mypy .` (preferred) |
| **flake8** (linter) | `uv add flake8` | `uv run flake8` | `uvx flake8` |
| **pylint** (linter) | `uv add pylint` | `uv run pylint` | `uvx pylint` |
| **isort** (import sorter) | `uv add isort` | `uv run isort` | `uvx isort .` |
| **poetry** (dependency manager) | `uv add poetry` | `uv run poetry` | `uvx poetry` |
| **pipenv** (dependency manager) | `uv add pipenv` | `uv run pipenv` | `uvx pipenv` |
| **cookiecutter** (project templates) | `uv add cookiecutter` | `uv run cookiecutter` | `uvx cookiecutter` |
| **httpie** (HTTP client) | `uv add httpie` | `uv run http` | `uvx http` |
| **mycli** (MySQL CLI) | `uv add mycli` | `uv run mycli` | `uvx mycli` |
| **pgcli** (PostgreSQL CLI) | `uv add pgcli` | `uv run pgcli` | `uvx pgcli` |

**Note**: For linters, formatters, and type checkers, `uvx` is preferred (doesn't pollute project dependencies). For tools that need to import your project modules (like pytest with your app code), use `uv run`.

### Running Any Python Package CLI

For ANY Python package with a CLI command:

```bash
# Option 1: Run as external tool (preferred for linters, formatters, one-off tools)
uvx <cli-command>

# Option 2: Install and run within project environment
uv add <package>
uv run <cli-command>

# Option 3: Run with specific version
uvx <package>@version <cli-command>
```

### Environment and Scripts

| NEVER use pip | ALWAYS use uv |
|---------------|---------------|
| `python -m venv .venv` | `uv venv` |
| `python script.py` | `uv run script.py` |
| `python -m module` | `uv run python -m module` |
| `python -m pip install` | `uv add` |
| `python -m pip list` | `uv pip list` |

## Priority

`uv` (with `uv run` or `uvx`) is the **ONLY** option for Python package management and execution.

**Execution priority**:
1. `uv run <command>` - for tools that need project dependencies
2. `uvx <command>` - for external tools that don't need project modules

Only consider `pip` as a fallback if:
1. The user explicitly requests `pip`
2. `uv` is not available on the system
3. You receive explicit confirmation from the user
