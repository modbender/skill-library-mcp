---
name: release-prep
description: Deep code audit + documentation sync + release preparation for Python packages. Use when preparing a release, checking code quality before publishing, auditing code vs docs, fixing pre-release issues, generating changelogs, bumping versions, or publishing to PyPI. Triggers on "release", "prepare release", "audit code", "check docs", "ready to release?", "publish", "pre-release check", "code review before release".
---

# release-prep — Release Preparation & Code Audit

Deep automated analysis of code quality, documentation completeness, and release readiness for Python packages. Can auto-fix issues found.

## Modes

- **`audit`** (default) — analyze and report only
- **`fix`** — analyze, then auto-fix issues via coding agent
- **`release`** — full pipeline: audit → fix → changelog → version bump → tag → publish

Parse mode from user request. Default to `audit` if unclear.

## Phase 1: Deep Code Audit

Run all checks, collect results into a structured report.

### 1.1 Test Suite

```bash
# Run full test suite with coverage
python -m pytest tests/ -q --tb=short --co -q 2>/dev/null | tail -1  # count tests
python -m pytest tests/ -q --tb=short 2>&1 | tail -5                  # run tests
```

Report: total tests, passed, failed, skipped, coverage % (if pytest-cov available).

**BLOCKER if any test fails.**

### 1.2 Static Analysis

```bash
# Ruff (if available)
ruff check src/ --statistics 2>&1 | tail -20

# Mypy (if available)
mypy src/ --no-error-summary 2>&1 | grep "error:" | wc -l
```

Report: error count by category. **BLOCKER if errors > 0** (warnings are OK).

### 1.3 Dead Code Detection

```bash
# Find unused imports
ruff check src/ --select F401 2>&1

# Find functions with no callers (heuristic)
grep -rn "^def \|^async def " src/ --include="*.py" | while read line; do
  func=$(echo "$line" | sed 's/.*def \([a-zA-Z_]*\).*/\1/')
  if [ "$func" != "__init__" ] && [ "$func" != "__" ]; then
    count=$(grep -rn "$func" src/ --include="*.py" | grep -v "^def \|^async def " | wc -l)
    if [ "$count" -lt 2 ]; then
      echo "POSSIBLY UNUSED: $line"
    fi
  fi
done
```

Report: list of potentially dead code. **WARNING** level.

### 1.4 API Completeness

```bash
# Public API (__all__ exports) vs actual public functions
python3 -c "
import ast, sys, pathlib
for f in pathlib.Path('src/').rglob('*.py'):
    tree = ast.parse(f.read_text())
    all_list = [n.value.s for n in ast.walk(tree) 
                if isinstance(n, ast.Assign) 
                for t in n.targets if isinstance(t, ast.Name) and t.id == '__all__'
                for elt in n.value.elts if isinstance(elt, ast.Constant)]
    if all_list:
        funcs = [n.name for n in ast.walk(tree) 
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) 
                 and not n.name.startswith('_')]
        missing = [f for f in funcs if f not in all_list]
        if missing:
            print(f'{f}: public but not in __all__: {missing}')
"
```

Report: functions missing from `__all__`. **WARNING** level.

### 1.5 Dependency Check

```bash
# Check for pinned vs unpinned deps
grep -E "dependencies|requires" pyproject.toml | head -20

# Check for unused dependencies (heuristic)
for dep in $(python3 -c "
import tomllib; 
d=tomllib.load(open('pyproject.toml','rb')); 
print(' '.join(d.get('project',{}).get('dependencies',[])))
"); do
  pkg=$(echo "$dep" | sed 's/[>=<].*//')
  count=$(grep -rn "import $pkg\|from $pkg" src/ --include="*.py" | wc -l)
  if [ "$count" -eq 0 ]; then
    echo "POSSIBLY UNUSED DEP: $dep"
  fi
done
```

Report: dependency issues. **WARNING** level.

## Phase 2: Documentation Audit

### 2.1 Docstring Coverage

```bash
python3 -c "
import ast, pathlib
total = missing = 0
for f in pathlib.Path('src/').rglob('*.py'):
    tree = ast.parse(f.read_text())
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith('_') or node.name == '__init__':
                total += 1
                if not ast.get_docstring(node):
                    missing += 1
                    print(f'  MISSING: {f}:{node.lineno} {node.name}')
print(f'\nDocstring coverage: {(total-missing)/total*100:.0f}% ({total-missing}/{total})')
"
```

**WARNING if coverage < 80%. BLOCKER if < 50%.**

### 2.2 README vs Reality

Check that README.md mentions:
- All CLI entry points from pyproject.toml `[project.scripts]`
- Installation instructions
- Basic usage example
- All major features (compare against module-level docstrings)

```bash
# Extract entry points
python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); [print(k) for k in d.get('project',{}).get('scripts',{}).keys()]"

# Check README mentions them
for ep in $(python3 -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); [print(k) for k in d.get('project',{}).get('scripts',{}).keys()]"); do
  grep -q "$ep" README.md && echo "✅ $ep in README" || echo "❌ $ep NOT in README"
done
```

**WARNING if entry points missing from README.**

### 2.3 Changelog Check

```bash
# Check CHANGELOG.md exists and has recent entries
if [ -f CHANGELOG.md ]; then
  head -20 CHANGELOG.md
  echo "Last entry date:"
  grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' CHANGELOG.md | head -1
else
  echo "❌ No CHANGELOG.md"
fi
```

### 2.4 Version Consistency

```bash
# Check version in pyproject.toml matches __version__
PYPROJECT_VER=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
CODE_VER=$(grep -r "__version__" src/ --include="*.py" | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
echo "pyproject.toml: $PYPROJECT_VER"
echo "Code __version__: $CODE_VER"
if [ "$PYPROJECT_VER" != "$CODE_VER" ]; then
  echo "❌ VERSION MISMATCH"
fi
```

**BLOCKER if version mismatch.**

## Phase 3: Report

Generate structured report:

```
╔══════════════════════════════════════╗
║     RELEASE READINESS REPORT        ║
╠══════════════════════════════════════╣
║ Package: {name} v{version}          ║
║ Branch:  {branch}                   ║
║ Commit:  {short_sha}                ║
╠══════════════════════════════════════╣
║ 🔴 BLOCKERS: {count}               ║
║ 🟡 WARNINGS: {count}               ║
║ 🟢 PASSED:   {count}               ║
╠══════════════════════════════════════╣
║ Tests:      {pass}/{total} ✅/❌    ║
║ Lint:       {errors} errors         ║
║ Docstrings: {pct}% coverage         ║
║ README:     {status}                ║
║ Version:    {status}                ║
║ Changelog:  {status}                ║
╚══════════════════════════════════════╝

BLOCKERS:
  1. {description}
  2. {description}

WARNINGS:
  1. {description}
  2. {description}

VERDICT: 🟢 READY / 🟡 READY WITH WARNINGS / 🔴 NOT READY
```

If mode is `audit` — stop here, present report to user.

## Phase 4: Auto-Fix (mode=fix or mode=release)

For each issue found, categorize fix approach:

| Issue Type | Fix Method |
|-----------|------------|
| Missing docstrings | Coding agent — generate from code |
| Lint errors | `ruff check --fix` or coding agent |
| Dead imports | `ruff check --fix --select F401` |
| README gaps | Generate missing sections from code analysis |
| Changelog missing | Generate from `git log` (conventional commits) |
| Version mismatch | Update code `__version__` to match pyproject.toml |
| Test failures | Coding agent — investigate and fix |

**Rules:**
- Show user what will be fixed before doing it
- Delegate complex fixes (test failures, missing features) to coding agent
- Simple fixes (lint, imports, version sync) — do directly
- After fixes — re-run Phase 1+2 to verify

## Phase 5: Changelog Generation (mode=release)

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LAST_TAG" ]; then
  RANGE="${LAST_TAG}..HEAD"
else
  RANGE="HEAD~50..HEAD"
fi

git log $RANGE --pretty=format:"%s" | sort
```

Group by conventional commit type (feat/fix/refactor/docs/test/chore). Generate markdown. Prepend to CHANGELOG.md.

Show draft to user before writing.

## Phase 6: Version & Publish (mode=release)

1. Determine version bump (major/minor/patch) from changelog:
   - `feat` → minor, `fix` → patch, `BREAKING CHANGE` → major
2. Update version in `pyproject.toml` and `__version__`
3. Commit: `chore: release v{version}`
4. Tag: `v{version}`
5. Build: `uv build` or `python -m build`
6. **Ask user before publish**: show summary + ask confirmation
7. Publish: `uv publish` or `twine upload dist/*`
8. Push tag: `git push origin v{version}`

## Project Detection

Auto-detect project type from files present:
- `pyproject.toml` → Python package (primary)
- `package.json` → Node.js (future)
- `Cargo.toml` → Rust (future)

Read `pyproject.toml` for: name, version, entry points, dependencies, build system.

## Error Handling

| Error | Action |
|-------|--------|
| No pyproject.toml | Stop — "Not a Python package. Looking for pyproject.toml" |
| No tests dir | WARNING — "No tests found. Consider adding tests before release" |
| No git repo | Stop — "Not a git repository" |
| Dirty working tree | WARNING — "Uncommitted changes detected" |
| ruff/mypy not found | Skip that check, note in report |
