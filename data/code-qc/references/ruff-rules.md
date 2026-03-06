# Ruff Rule Reference for QC

## Rule Selection Decision Tree

Use this flowchart to select the appropriate rule set for your project:

```
Is this a QC audit or development linting?
├── QC Audit (one-time check)
│   └── Use: STANDARD SET (catch issues without blocking)
│
└── Development/CI (ongoing)
    │
    ├── Is this a library/SDK?
    │   └── Use: STRICT SET (quality is paramount)
    │
    ├── Is this a CLI/script?
    │   ├── Allow print()? → Remove T201 from rules
    │   └── Use: STANDARD SET minus T201
    │
    ├── Is this a web application?
    │   └── Use: STANDARD + SECURITY (add S)
    │
    ├── Is this a data science/ML project?
    │   ├── Allow long lines? → Add --line-length 120
    │   └── Use: STANDARD SET (flexible)
    │
    └── Is this a legacy codebase?
        └── Use: MINIMAL SET (fix critical only)
```

## Rule Sets

### MINIMAL SET (Legacy/Quick Fix)
```bash
ruff check --select E722,B006 .
```
Only catches:
- Bare `except:` (potential bug masking)
- Mutable default arguments (actual bugs)

### STANDARD SET (QC Audit)
```bash
ruff check --select E722,T201,B006,F401,F841,UP,I --statistics .
```
Recommended for most projects. Catches common issues without being noisy.

### STRICT SET (Libraries/SDKs)
```bash
ruff check --select E722,T201,B006,F401,F841,UP,I,S,C90,PT,RUF,D --statistics .
```
Full strictness for public libraries.

### SECURITY SET (Web Applications)
```bash
ruff check --select E722,B006,F401,F841,UP,I,S --statistics .
```
Focus on security-relevant issues.

## Rule Explanations

### E722 — Bare except
```python
# Bad — catches KeyboardInterrupt, SystemExit, and hides bugs
try:
    risky()
except:
    pass

# Good — specific exceptions
try:
    risky()
except (ValueError, KeyError) as e:
    logger.error(f"Failed: {e}")

# Also Good — Exception base class (still allows KeyboardInterrupt)
try:
    risky()
except Exception as e:
    logger.exception("Unexpected error")
```

**Why it matters:** Bare `except:` catches `KeyboardInterrupt` (Ctrl+C), `SystemExit` (sys.exit()), and other system signals. This makes debugging impossible and can prevent graceful shutdown.

### T201 — print() found
```python
# Bad — goes to stdout, no timestamps, no levels
print(f"Processing {item}")

# Good — proper logging
logger.info(f"Processing {item}")

# Also Good — explicit CLI output
import sys
sys.stderr.write(f"Processing {item}\n")
```

**When to ignore:** CLIs, scripts, notebooks. Add `# noqa: T201` or exclude T201 from rule set.

### B006 — Mutable default argument
```python
# Bad — shared mutable state across all calls
def process(items=[]):  # Same list for every call!
    items.append("new")
    return items

process()  # ['new']
process()  # ['new', 'new'] — Bug!

# Good — None sentinel
def process(items=None):
    if items is None:
        items = []
    items.append("new")
    return items
```

**Why it matters:** This is a genuine bug, not style. Default arguments are evaluated once at function definition, not each call.

### F401 — Unused import
```python
# Bad — clutters namespace, slows startup
import os  # never used

# Good — remove or use
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import os  # Only for type hints
```

**When to ignore:** `__init__.py` re-exports, plugins that need imports for side effects.

### F841 — Unused variable
```python
# Bad — confusing, may indicate forgotten logic
result = expensive_call()  # result never used

# Good — explicit discard
_ = expensive_call()

# Or just
expensive_call()
```

### UP — Pyupgrade
Catches outdated syntax for your target Python version:
```python
# Python 3.9+: old
from typing import Dict, List
# Python 3.9+: new
dict, list  # Use built-in generics

# Python 3.10+: old
Union[int, str]
# Python 3.10+: new
int | str
```

### I — isort
Consistent import ordering:
```python
# Bad — inconsistent grouping
from myproject.utils import helper
import os
from typing import Optional
import sys

# Good — grouped and sorted
import os
import sys
from typing import Optional

from myproject.utils import helper
```

## Extended Rules (Optional)

### S — Bandit Security
```bash
ruff check --select S .
```
- `S101` — assert used (disabled in production)
- `S105` — hardcoded password
- `S106` — hardcoded password in function arg
- `S107` — hardcoded password default
- `S108` — insecure temp file
- `S301` — pickle usage (insecure deserialization)
- `S608` — SQL injection

### C90 — McCabe Complexity
```bash
ruff check --select C90 --max-complexity 10 .
```
- `C901` — function too complex (cyclomatic complexity)

### D — Docstrings (pydocstyle)
```bash
ruff check --select D .
```
- `D100` — missing module docstring
- `D101` — missing class docstring
- `D102` — missing method docstring
- `D103` — missing function docstring

### PT — pytest
```bash
ruff check --select PT .
```
- `PT001` — use @pytest.fixture
- `PT006` — wrong type for parametrize args
- `PT009` — use pytest.raises instead of unittest

### RUF — Ruff-specific
```bash
ruff check --select RUF .
```
Ruff's own rules for common Python issues.

## Configuration

### pyproject.toml
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E722", "T201", "B006", "F401", "F841", "UP", "I"]
ignore = ["T201"]  # Allow print in this project

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
"scripts/*" = ["T201"]  # Allow print in scripts
```

### CLI Override
```bash
# Ignore specific rules for this run
ruff check --ignore T201,F841 .

# Add extra rules
ruff check --select E722,T201,B006 --extend-select S .
```

## Fix Mode

### Safe Fixes Only
```bash
ruff check --fix .
```
Applies only fixes that are guaranteed safe (won't change behavior).

### Unsafe Fixes
```bash
ruff check --fix --unsafe-fixes .
```
Applies all fixes including potentially behavior-changing ones. Review diff carefully.

### Format
```bash
ruff format .
```
Black-compatible formatting. Run after `--fix`.

## Interpreting Output

```
$ ruff check --statistics .
Found 47 errors.
F401  [ ] 23  `...` imported but unused
T201  [ ] 15  `print` found
F841  [*]  5  Local variable `...` is assigned but never used
E722  [ ]  3  Do not use bare `except`
B006  [ ]  1  Do not use mutable data structures for argument defaults

[*] 5 fixable with `--fix`
```

- **Count by rule** — prioritize high-count rules
- **[*] Fixable** — can be auto-fixed
- **Statistics** — use `--statistics` for summary view

## CI Integration

```yaml
# GitHub Actions
- name: Lint with ruff
  run: |
    pip install ruff
    ruff check --output-format=github .
```

```yaml
# GitLab CI
lint:
  script:
    - pip install ruff
    - ruff check --output-format=gitlab .
```
