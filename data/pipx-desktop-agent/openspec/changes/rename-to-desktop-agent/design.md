# Design: Desktop-Agent Package Structure and UVX Distribution

## Overview
This change transforms the project from a local script-based tool to a properly packaged Python application that can be executed via `uvx` without installation.

## Architecture Decisions

### 1. Package Structure

**Current:**
```
desktop-skill/
├── main.py
├── commands/
│   ├── mouse.py
│   ├── keyboard.py
│   └── ...
└── pyproject.toml
```

**Proposed:**
```
desktop-agent/
├── desktop_agent/          # New package directory
│   ├── __init__.py        # Exports CLI app
│   ├── __main__.py        # Entry point for python -m
│   └── commands/          # Moved inside package
│       ├── __init__.py
│       ├── mouse.py
│       └── ...
├── pyproject.toml         # Updated config
└── scripts/
    └── install.py
```

**Rationale:**
- Standard Python package structure enables proper distribution
- `__main__.py` allows `python -m desktop_agent` execution
- Package name uses underscores (Python convention), CLI uses hyphens (CLI convention)

### 2. Entry Points Configuration

```toml
[project.scripts]
desktop-agent = "desktop_agent:app"
```

**How it works:**
- `uvx desktop-agent` → uvx downloads/installs package → runs `desktop_agent:app`
- `desktop-agent` → runs installed CLI (if installed locally)
- `python -m desktop_agent` → runs package as module

### 3. UVX Compatibility

**Requirements:**
- Valid `pyproject.toml` with build system
- Proper entry points defined
- Package name matches PyPI-compatible naming (even if not published yet)

**Benefits:**
- Zero-install execution: `uvx desktop-agent <command>` works immediately
- Version pinning: `uvx desktop-agent@0.1.0 <command>`
- Isolated environments: uvx creates temporary venv per execution
- Dependency management: uvx handles all dependencies automatically

### 4. Import Path Migration

**Before:**
```python
from commands import mouse, keyboard
```

**After:**
```python
from desktop_agent.commands import mouse, keyboard
```

**Strategy:**
- Update all imports systematically
- Ensure relative imports work within package
- Test each module independently

### 5. Backwards Compatibility

**Development:**
- Keep supporting `python main.py` during development
- `main.py` can be a thin wrapper that imports from package

**Production:**
- Users should migrate to `uvx desktop-agent` or `desktop-agent`
- Add deprecation notice in README for old invocation method

## Implementation Strategy

### Phase 1: Structure (Non-breaking)
1. Create `desktop_agent/` directory
2. Move code without changing imports yet
3. Setup can coexist with current structure

### Phase 2: Entry Points
1. Update `pyproject.toml`
2. Configure entry points
3. Test local installation

### Phase 3: Migration
1. Update all imports
2. Remove old structure
3. Update documentation

### Phase 4: Verification
1. Test uvx execution
2. Verify all commands work
3. Test edge cases

## Technical Considerations

### Python Package Naming
- **Package name**: `desktop_agent` (underscore)
- **Distribution name**: `desktop-agent` (hyphen)
- **CLI command**: `desktop-agent` (hyphen)

This follows PEP 8 and PyPA conventions.

### UVX Execution Model
```bash
uvx desktop-agent mouse move 100 200
```

UVX will:
1. Create isolated environment
2. Install desktop-agent and dependencies
3. Execute: `desktop_agent:app` with args `['mouse', 'move', '100', '200']`
4. Clean up environment (optional caching)

### Module Entry Point (`__main__.py`)
```python
from desktop_agent import app

if __name__ == "__main__":
    app()
```

Enables: `python -m desktop_agent <commands>`

## Testing Plan

### Manual Tests
```bash
# Test uvx execution (no install)
uvx --from . desktop-agent --help
uvx --from . desktop-agent mouse position

# Test local installation
uv pip install -e .
desktop-agent --help

# Test as module
python -m desktop_agent --help
```

### Verification Points
- [ ] All command categories accessible
- [ ] Help system works
- [ ] Arguments parse correctly
- [ ] Typer sub-apps load properly
- [ ] PyAutoGUI commands execute

## Risk Mitigation

**Risk**: Breaking imports during migration
- **Mitigation**: Phase-based approach, one module at a time

**Risk**: UVX not finding package
- **Mitigation**: Test with `uvx --from .` first (local testing)

**Risk**: Users confused by new invocation
- **Mitigation**: Clear migration guide, keep examples updated

## Future Enhancements (Out of Scope)
- Publish to PyPI for `uvx desktop-agent` without `--from`
- Add shell completions for better UX
- Multi-platform testing (macOS, Linux)
