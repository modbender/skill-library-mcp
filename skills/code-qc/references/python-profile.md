# Python QC Profile

## Project Detection

Python project if any of these exist:
- `pyproject.toml`
- `setup.py` or `setup.cfg`
- `requirements.txt`
- `Pipfile`
- Top-level `*.py` files

## Virtual Environment Detection

Check for active/available virtual environment in order:

```bash
# 1. Already active
echo $VIRTUAL_ENV

# 2. Common venv directories
for dir in .venv venv env .env; do
    if [ -f "$dir/bin/activate" ] || [ -f "$dir/Scripts/activate" ]; then
        echo "Found: $dir"
    fi
done

# 3. Poetry
if [ -f "poetry.lock" ]; then
    poetry env info --path 2>/dev/null
fi

# 4. Conda
if [ -f "environment.yml" ] || [ -f "environment.yaml" ]; then
    echo "Conda environment file found"
    # Check if conda env exists
    conda env list | grep -q "$(basename $PWD)"
fi

# 5. PDM
if [ -f "pdm.lock" ]; then
    pdm info --env 2>/dev/null
fi

# 6. Hatch
if [ -f "hatch.toml" ] || grep -q "[tool.hatch]" pyproject.toml 2>/dev/null; then
    hatch env find 2>/dev/null
fi

# 7. Project-specific activate script
if [ -f "activate.sh" ]; then
    echo "Found: activate.sh"
fi
```

**Activation for QC:**
```bash
# Auto-activate if found
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "poetry.lock" ]; then
    poetry shell || poetry run pytest
fi
```

## Test Runner Detection

Check in order:
1. `pyproject.toml` → `[tool.pytest.ini_options]` → `pytest`
2. `pytest.ini` → `pytest`
3. `setup.cfg` → `[tool:pytest]` → `pytest`
4. `tox.ini` → `tox`
5. `noxfile.py` → `nox`
6. Fallback: `python -m pytest tests/`

## Phase 1: Test Suite with Coverage

### Basic Run
```bash
pytest -v --tb=short
```

### With Coverage
```bash
# Coverage for the main package
pytest --cov=<package_name> --cov-report=term-missing --cov-report=json --cov-fail-under=0

# Parse coverage JSON for reporting
python -c "import json; d=json.load(open('coverage.json')); print(f\"Coverage: {d['totals']['percent_covered']:.1f}%\")"
```

### Scientific Computing Projects

Large test suites with GPU/slow tests often use markers:

```bash
# Skip slow tests for quick QC
pytest -m "not slow"

# Skip GPU tests on CPU-only machines
pytest -m "not gpu"

# Run only unit tests (skip integration)
pytest -m "not integration"

# Common marker combinations
pytest -m "not (slow or gpu or integration)"
```

**Detect available markers:**
```bash
pytest --markers | grep -E "^@pytest.mark\.(slow|gpu|integration|e2e)"
```

### No Tests Handling

If no tests found:
- Check for `tests/`, `test/`, `*_test.py`, `test_*.py`
- If directory exists but empty: **SKIP** with note "Test directory exists but no tests"
- If no test directory: **SKIP** with note "No test suite configured"
- Do NOT fail for missing tests (project may be library without tests)

## Phase 3: Static Analysis with ruff

Install if needed: `pip install ruff`

### Standard Check
```bash
ruff check --select E722,T201,B006,F401,F841,UP,I --statistics <project>
```

### Fix Mode
```bash
# Safe auto-fixes only
ruff check --fix --select E,F,I,UP <project>

# Also format
ruff format <project>
```

### Recommended Rule Set

| Rule | What it catches |
|------|----------------|
| `E722` | Bare `except:` without exception type |
| `T201` | `print()` statement found (should use logging) |
| `B006` | Mutable default argument (`def f(x=[])`) |
| `F401` | Unused import |
| `F841` | Unused local variable |
| `UP` | Pyupgrade: outdated syntax for target Python version |
| `I` | isort: import ordering |

### Severity Mapping

- `E722`, `B006` → WARNING (potential bugs)
- `T201` → WARNING (code hygiene)
- `F401`, `F841` → INFO (cleanup)
- Anything ruff calls ERROR → ERROR

### Strict Mode (Optional)

For stricter QC, add security and complexity checks:
```bash
ruff check --select E722,T201,B006,F401,F841,UP,I,S,C90,PT,RUF --statistics .
```

## Phase 3.5: Type Checking

### mypy
```bash
# Basic check
mypy <package> --ignore-missing-imports

# Strict mode
mypy <package> --strict --ignore-missing-imports

# With config from pyproject.toml
mypy <package>
```

### pyright (if configured)
```bash
# Check if pyright is configured
grep -q "tool.pyright" pyproject.toml && pyright <package>
```

### Type Coverage Estimate
```bash
# Count typed vs untyped function signatures
grep -rn "def " --include="*.py" | wc -l  # total
grep -rn "def .*(.*:.*) ->" --include="*.py" | wc -l  # typed
```

## Import Check

Use `scripts/import_check.py`:

```bash
python scripts/import_check.py <package> --exclude vendor1,vendor2 --json
```

Common exclusions:
- Vendored dependencies: `aot`, `sam`, `dinov2`
- Test fixtures: `fixtures`, `mocks`
- Migration scripts: `migrations`, `alembic`
- Generated code: `generated`, `proto`

## Smoke Test Patterns

### Service Layer
```python
import tempfile
from package.service import create_thing, get_thing

def smoke_test_thing_service():
    with tempfile.TemporaryDirectory() as tmp:
        result = create_thing(tmp, "test")
        assert result is not None
        fetched = get_thing(tmp, "test")
        assert fetched is not None
    return "PASS"
```

### CLI (typer/click)
```python
from typer.testing import CliRunner
from package.cli import app

def smoke_test_cli():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    return "PASS"
```

### Config Round-trip
```python
from package.config import Config

def smoke_test_config():
    cfg = Config()
    d = cfg.to_dict()
    cfg2 = Config.from_dict(d)
    assert cfg.field == cfg2.field
    return "PASS"
```

### FastAPI/Flask Endpoints
```python
from fastapi.testclient import TestClient
from package.app import app

def smoke_test_api():
    client = TestClient(app)
    # Health check
    r = client.get("/health")
    assert r.status_code == 200
    # API version
    r = client.get("/api/v1/version")
    assert r.status_code == 200
    return "PASS"
```

### Numerical/ML Backward Compatibility
```python
import numpy as np

def smoke_test_model_backward_compat():
    """Verify model produces same output as baseline."""
    from package.model import predict
    
    # Fixed input for reproducibility
    np.random.seed(42)
    test_input = np.random.randn(1, 10)
    
    result = predict(test_input)
    
    # Compare to saved baseline (update when intentionally changing)
    baseline = np.load("tests/baselines/model_output.npy")
    np.testing.assert_allclose(result, baseline, rtol=1e-5)
    return "PASS"
```

### Database/ORM
```python
import tempfile
from package.db import init_db, Session
from package.models import User

def smoke_test_database():
    with tempfile.NamedTemporaryFile(suffix=".db") as f:
        init_db(f"sqlite:///{f.name}")
        with Session() as session:
            user = User(name="test")
            session.add(user)
            session.commit()
            assert session.query(User).count() == 1
    return "PASS"
```

## UI Verification

### Gradio
```python
def smoke_test_gradio_ui():
    import os
    os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
    from package.ui import create_ui
    
    demo = create_ui()
    assert demo is not None
    # Don't call launch()
    return "PASS"
```

### Streamlit
```bash
# Run in headless mode, should exit cleanly
timeout 10 streamlit run app.py --headless --server.headless true 2>&1 | grep -q "error" && echo "FAIL" || echo "PASS"
```

### PyQt/PySide
```python
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"

def smoke_test_qt_ui():
    from package.ui.main_window import MainWindow
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    window = MainWindow()
    assert window is not None
    # Don't show() or exec()
    return "PASS"
```

## Dependency Security

```bash
# pip-audit (recommended)
pip-audit --json

# safety (alternative)
safety check --json

# Check for known vulnerabilities
pip-audit --strict --desc on
```
