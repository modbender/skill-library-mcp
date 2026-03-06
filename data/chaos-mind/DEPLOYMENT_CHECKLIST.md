# CHAOS Memory - Deployment Checklist

## Pre-Release Validation

### 1. Configuration Files ✅
- [x] `config/consolidator.template.yaml` - Uses port 3307 (local DB)
- [x] `config/chaos-consolidator.service.template` - Systemd service
- [x] Categories are flexible (not strict enum)
- [x] Auto-capture paths use glob patterns

### 2. Installation Script ✅
- [x] Creates `~/.chaos/db` database with VARCHAR categories
- [x] Downloads pre-built binaries or builds from source
- [x] Sets up config directory structure
- [x] Includes setup-service.sh for systemd

### 3. Database Schema ✅
**CRITICAL:** Local database uses flexible VARCHAR for `category` field.

```sql
-- Local development (port 3307)
category VARCHAR(50) DEFAULT 'semantic'

-- NOT the strict enum from SaaS (port 3306):
-- category enum('core','semantic','working','episodic')
```

### 4. Auto-Capture Sources
Default glob patterns:
- `~/.openclaw-*/agents/*/sessions/*.jsonl`
- `~/.clawdbot-*/agents/*/sessions/*.jsonl`
- `~/*/memory/*.md`

Users can customize in `~/.chaos/config/consolidator.yaml`.

### 5. Service Setup
```bash
# Install service
./setup-service.sh

# Start
sudo systemctl start chaos-consolidator

# Monitor
sudo journalctl -u chaos-consolidator -f
```

## Known Issues & Fixes

### Issue 1: Wrong Database Port
**Problem:** Config pointed to SaaS DB (port 3306) instead of local (port 3307)  
**Fix:** Updated template to use port 3307  
**Impact:** Memories now go to local flexible-schema database

### Issue 2: Invalid Category Enum
**Problem:** Qwen extracted categories like "decision", "research" but SaaS DB only accepts enum  
**Fix:** Local DB uses VARCHAR(50) for flexible categories  
**Impact:** All categories are now accepted

### Issue 3: Service Not Restarting
**Problem:** No systemd service, manual restarts required  
**Fix:** Added service template + setup script  
**Impact:** Auto-restart on failure, survives reboot

## Testing Protocol

### Manual Testing
```bash
# 1. Install
./install.sh

# 2. Start database
cd ~/.chaos/db && dolt sql-server --port 3307 &

# 3. Pull model
ollama pull qwen3:1.7b

# 4. Configure paths
nano ~/.chaos/config/consolidator.yaml
# Edit auto_capture.sources to match your OpenClaw location

# 5. Test one-shot
chaos-consolidator --config ~/.chaos/config/consolidator.yaml --auto-capture --once

# 6. Check logs
tail -f ~/.chaos/consolidator.log

# Expected: ✅ Extracted N memories from <file>
# NOT: ⚠️ Failed to store memory: Error 1105
```

### Validation
- [ ] Extracts memories from session files
- [ ] Stores without errors (no enum violations)
- [ ] Database count increases
- [ ] Service restarts on failure
- [ ] Survives system reboot

## Release Artifacts

### Required Files
- [x] `skill/install.sh` - Main installer
- [x] `skill/config/consolidator.template.yaml` - Config template
- [x] `skill/config/chaos-consolidator.service.template` - Service template
- [x] `skill/scripts/setup-service.sh` - Service installer
- [x] `skill/README.md` - User documentation
- [x] `skill/SKILL.md` - Skill metadata

### Binary Releases
Build for all platforms:
```bash
# Linux x86_64
GOOS=linux GOARCH=amd64 go build -o chaos-consolidator-linux ./cmd/consolidator
GOOS=linux GOARCH=amd64 go build -o chaos-mcp-linux ./cmd/chaos

# macOS Intel
GOOS=darwin GOARCH=amd64 go build -o chaos-consolidator-macos ./cmd/consolidator
GOOS=darwin GOARCH=amd64 go build -o chaos-mcp-macos ./cmd/chaos

# macOS ARM (M1/M2)
GOOS=darwin GOARCH=arm64 go build -o chaos-consolidator-macos-arm64 ./cmd/consolidator
GOOS=darwin GOARCH=arm64 go build -o chaos-mcp-macos-arm64 ./cmd/chaos
```

## Post-Release

### Support Resources
- GitHub Issues: https://github.com/hargabyte/chaos-memory/issues
- ClawHub Page: https://clawhub.com/skills/chaos-memory
- Documentation: skill/README.md

### Monitor
- Installation success rate
- Common error patterns
- Feature requests
- Bug reports

## Version History

**v1.0.0** (2026-02-06)
- Fixed database port (3307 for local)
- Flexible category schema (VARCHAR not enum)
- Added systemd service support
- Improved auto-capture source patterns

---

**Deployment approved by:** _____________  
**Date:** 2026-02-06
