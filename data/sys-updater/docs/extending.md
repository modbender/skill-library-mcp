# Extending sys-updater

sys-updater is designed for apt on Ubuntu, but the architecture can be extended to other package managers.

## Adding a New Provider

### 1. Create a new script

```
scripts/
├── apt_maint.py      # existing
├── brew_maint.py     # new: Homebrew
├── npm_maint.py      # new: npm global packages
└── ...
```

### 2. Follow the same pattern

Each provider should implement:

```python
def run_6am() -> ProviderResult:
    """Execute maintenance, save state."""
    pass

def render_report() -> str:
    """Generate human-readable report."""
    pass
```

### 3. State file convention

```
state/
├── apt/
│   ├── last_run.json
│   └── tracked.json
├── brew/
│   ├── last_run.json
│   └── tracked.json
├── npm/
│   ├── last_run.json
│   └── tracked.json
└── logs/
    └── *.log
```

## Example: Homebrew Provider

```python
# scripts/brew_maint.py

def run_6am() -> RunResult:
    # 1. brew update
    sh(["brew", "update"])

    # 2. brew upgrade (dry-run)
    cp = sh(["brew", "upgrade", "--dry-run"], check=False)

    # 3. List outdated
    outdated = sh(["brew", "outdated", "--json"])

    # 4. Save state
    save_json(STATE_DIR / "brew" / "last_run.json", result.__dict__)

    return result
```

## Example: npm Global Packages

```python
# scripts/npm_maint.py

def run_6am() -> RunResult:
    # 1. Check outdated
    cp = sh(["npm", "outdated", "-g", "--json"], check=False)

    # 2. Parse and track
    outdated = json.loads(cp.stdout) if cp.stdout else {}

    # 3. Save state
    save_json(STATE_DIR / "npm" / "last_run.json", result.__dict__)

    return result
```

## Future Providers

Potential providers to add:

| Provider | Use case |
|----------|----------|
| `brew` | macOS Homebrew packages |
| `npm` | Node.js global packages |
| `pip` | Python system packages |
| `snap` | Ubuntu Snap packages |
| `flatpak` | Flatpak applications |
| `docker` | Docker image updates |
| `openclaw` | OpenClaw model updates |
| `claude` | Claude Code updates |

## Unified Report

A future `report_all.py` could aggregate all providers:

```python
def render_unified_report():
    providers = ["apt", "brew", "npm"]
    sections = []

    for p in providers:
        state = load_json(STATE_DIR / p / "last_run.json", None)
        if state:
            sections.append(render_provider_section(p, state))

    return "\n\n".join(sections)
```

## Contributing

When adding a provider:

1. Keep it conservative (no auto-apply for non-security)
2. Use the same state file schema where possible
3. Add logging following the same pattern
4. Update CLAUDE.md with new commands
5. Add documentation in docs/
