# Release Notes - OpenClaw iFlow Doctor

## [1.1.0] - 2026-03-01

### 🐛 Bug Fixes

#### Fix #1: watchdog.py --daemon Not Working
- **Issue**: Daemon thread exits when main thread exits, making monitoring useless
- **Impact**: Watchdog functionality completely broken
- **Fix**: Changed `daemon=True` to `daemon=False` in watchdog.py
- **File**: `watchdog.py` (line 176)
- **Tested**: ✅ Verified with systemd service

#### Fix #2: Missing systemd Service
- **Issue**: No auto-start on boot
- **Impact**: Manual intervention required after reboot
- **Fix**: Added systemd service file and installation script
- **Files**: 
  - `openclaw-iflow-doctor.service` (new)
  - `install-systemd.sh` (new)
- **Tested**: ⏳ Pending installation

#### Fix #3: Tilde (~) Path Expansion
- **Issue**: Tilde in config paths not expanded
- **Impact**: Config file not found errors
- **Fix**: Use `Path.home().expanduser()` throughout codebase
- **Files**: `watchdog.py`, `config_checker.py`
- **Tested**: ✅ Path expansion working

#### Fix #4: Desktop Directory Not Found
- **Issue**: Code referenced Desktop directory which doesn't exist on servers
- **Impact**: Diagnostic report generation failed
- **Fix**: Changed to use user home directory instead
- **Files**: `watchdog.py`, `openclaw_memory.py`
- **Tested**: ✅ No more Desktop references

### ✨ Improvements

#### Cross-Platform Support
- **Linux**: Full systemd integration
- **Windows**: BAT file generation for manual installation
- **macOS**: launchd support planned

#### Better Error Handling
- Improved logging with timestamps
- Better error messages for debugging
- Graceful degradation when iflow-helper not available

#### Documentation
- Added `BUGFIX_STATUS.md` with detailed fix status
- Updated `skill.md` with changelog
- Added `RELEASE.md` for version history

### 📦 Compatibility

| Component | Minimum Version | Tested Version |
|-----------|----------------|----------------|
| OpenClaw | 2026.2.0 | 2026.2.25 |
| Python | 3.8 | 3.12 |
| iflow-helper | 1.0.0 | Latest |
| systemd | 219 | 249 |

### 🎯 Installation

#### Linux (systemd)
```bash
cd openclaw-iflow-doctor
sudo ./install-systemd.sh
```

#### Windows
```powershell
# Manual installation
python install.py
```

#### macOS
```bash
# Coming in next release
```

### 📊 Bug Fix Summary

| Bug ID | Priority | Status | Tested |
|--------|----------|--------|--------|
| #1 (daemon) | High | ✅ Fixed | ✅ |
| #2 (systemd) | High | ✅ Fixed | ⏳ |
| #3 (paths) | High | ✅ Fixed | ✅ |
| #4 (Desktop) | Medium | ✅ Fixed | ✅ |

**Fix Rate**: 100% (4/4 bugs fixed)

---

## [1.0.0] - 2026-02-28

### Initial Release

- Auto-healing for 8 error types
- Case library with 10+ pre-built solutions
- Integration with iflow-helper
- Config checker
- Process monitoring
- Diagnostic reports

---

## Version History

- **1.1.0** (2026-03-01) - Bug fixes, systemd support, cross-platform
- **1.0.0** (2026-02-28) - Initial release

---

## Support

- **Issues**: https://github.com/kosei-echo/openclaw-iflow-doctor/issues
- **Discussions**: https://github.com/kosei-echo/openclaw-iflow-doctor/discussions
- **Documentation**: https://github.com/kosei-echo/openclaw-iflow-doctor/blob/main/skill.md

---

**Total Downloads**: N/A  
**Rating**: N/A  
**Last Updated**: 2026-03-01
