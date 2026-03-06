# Platform Compatibility

## Supported Platforms

| Platform | Status | Shell Scripts | Notes |
|----------|--------|---------------|-------|
| Linux | ✅ Fully Supported | `.sh` | Primary development target |
| macOS | ✅ Fully Supported | `.sh` | Tested on macOS 12+ |
| Windows (WSL) | ✅ Fully Supported | `.sh` | Run in WSL environment |
| Windows (Native) | ⚠️ Partial | `.ps1`, `.bat` | Requires PowerShell or CMD |

## Requirements (All Platforms)

1. **Python 3.8+**
2. **OpenClaw** installed and running
3. **Google Chrome** with OpenClaw extension attached
4. **Active Kimi account** session in Chrome

## Platform-Specific Setup

### Linux / macOS

```bash
# Use bash scripts
./check_usage.sh
python3 scripts/preflight_check.py intensive
```

### Windows (WSL - Recommended)

```bash
# In WSL terminal
./check_usage.sh
python3 scripts/subagent_guard.py
```

### Windows (Native PowerShell)

```powershell
# In PowerShell
.\check_usage.ps1
python3 scripts\preflight_check.py intensive
```

### Windows (Native CMD)

```cmd
:: In Command Prompt
check_usage.bat --json
python3 scripts\fetch_usage.py
```

## Path Handling

All Python scripts use `pathlib.Path` for cross-platform compatibility:

```python
from pathlib import Path
SKILL_DIR = Path(__file__).parent.parent
script = SKILL_DIR / "scripts" / "fetch_usage.py"
```

This works correctly on:
- Linux/macOS: `/path/to/scripts/fetch_usage.py`
- Windows: `C:\path\to\scripts\fetch_usage.py`

## Known Limitations

### Windows Native (Non-WSL)

1. **OpenClaw CLI Path**: Ensure `openclaw` is in your PATH or use full path
2. **Python Command**: May need `py` or `python` instead of `python3`
3. **Terminal Encoding**: Use UTF-8 capable terminal for emoji display

### Workaround for Missing `openclaw` in PATH (Windows)

```python
# In scripts, modify the subprocess call:
result = subprocess.run(
    ["C:\\Path\\To\\openclaw", "browser", "tabs"],  # Full path
    # ... rest of code
)
```

## Testing Matrix

| Feature | Linux | macOS | Windows (WSL) | Windows (Native) |
|---------|-------|-------|---------------|------------------|
| fetch_usage.py | ✅ | ✅ | ✅ | ✅ |
| usage_logger.py | ✅ | ✅ | ✅ | ✅ |
| preflight_check.py | ✅ | ✅ | ✅ | ✅ |
| subagent_guard.py | ✅ | ✅ | ✅ | ✅ |
| check_usage.sh | ✅ | ✅ | ✅ | ❌ |
| check_usage.ps1 | ❌ | ❌ | ❌ | ✅ |
| check_usage.bat | ❌ | ❌ | ❌ | ✅ |

## Recommendation

**For Windows users**: Use WSL2 if possible — it provides the most consistent experience with Linux/macOS.

**For all platforms**: The Python scripts are the most portable option. Use these directly:

```bash
# Universal command (all platforms)
python3 scripts/fetch_usage.py
```
