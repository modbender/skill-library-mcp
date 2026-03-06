# Security Information - Rune v1.1.2

## Package Security

### Installation & Dependencies
- **npm install process**: Installation fetches dependencies from npm registry
- **No git clone required**: Installation works from packaged bundle alone  
- **Transparent dependencies**: All deps visible in package.json for security audit
- **No remote binary downloads**: All code comes from npm registry (auditable)

### Minimal Dependencies
**Required (2):**
- `better-sqlite3` - Native SQLite3 bindings for database
- `commander` - CLI argument parsing library

**Optional (1):**
- `node-fetch` - For cloud API requests (only if you use cloud models)

### Dependency Security Audit
```bash
# Check security of dependencies
npm audit

# View dependency tree
npm ls --all

# Security verification before install
./install.sh --verify
```

## Installation Security

### Automatic Backups
The installer automatically backs up:
- `~/.openclaw/workspace/HEARTBEAT.md` → `HEARTBEAT.md.backup-<timestamp>`
- `~/.openclaw/memory.db` → `memory.db.backup-<timestamp>`

### Verification Modes
```bash
# Preview installation without changes
./install.sh --dry-run

# Verify package integrity only
./install.sh --verify

# Skip safety prompts (automated installs)
./install.sh --force
```

### File System Impact
**Creates:**
- `~/.openclaw/` directory structure
- `~/.openclaw/memory.db` (SQLite database)
- Global `rune` CLI command

**Modifies:**
- `~/.openclaw/workspace/HEARTBEAT.md` (appends integration, with backup)

**Never touches:**
- System files
- Other user directories
- Network configurations
- Browser settings

## Runtime Security

### Session Handler Security (CVE-2026-0001 Fixed)
- **Input sanitization**: All user input sanitized before shell commands
- **Length limits**: Message length capped at 200 characters
- **Character filtering**: Dangerous shell characters removed
- **No direct shell execution**: All commands use safe wrappers

### Data Storage
**Local SQLite database** at `~/.openclaw/memory.db`:
- **No network access** required for core functionality
- **No telemetry** or usage tracking
- **User-controlled** data retention and deletion

### Privacy Modes

**Local-First (Default):**
- Uses Ollama for all AI operations
- No data sent to external services
- Complete privacy and offline operation

**Cloud-Enabled (Optional):**
- Requires explicit API key setup
- User controls which operations use cloud APIs
- Clear documentation of data flow

```bash
# Local-only usage (no API keys needed)
rune add person "John Doe" "Project manager"
rune search "project"

# Cloud-enhanced (requires API keys)
export ANTHROPIC_API_KEY="sk-..."
rune extract "complex document.txt"  # Uses cloud for analysis
```

## Vulnerability Response

### CVE-2026-0001: Shell Injection (FIXED)
- **Issue**: Session hooks allowed shell command injection
- **Fix**: Comprehensive input sanitization in v1.0.2
- **Status**: Verified fixed by ClawHub security review

### Security Updates
- Version 1.0.2: Shell injection fix
- Version 1.0.3: Documentation transparency improvements  
- Version 1.1.0: Complete package + security enhancements

## Verification

### Package Integrity
```bash
# Verify package structure
./install.sh --verify

# Check included source
ls -la bin/ src/ package.json

# Audit dependencies
npm audit
```

### Runtime Verification
```bash
# Verify installation
rune --version
rune stats

# Check file permissions
ls -la ~/.openclaw/
```

## Reporting Security Issues

Found a security vulnerability? Please report responsibly:

1. **Do NOT** open public issues for security vulnerabilities
2. **Contact** via GitHub security advisory system
3. **Include** detailed reproduction steps
4. **Allow** reasonable time for fix before disclosure

We follow responsible disclosure practices and will credit security researchers appropriately.

---

**Security Level**: Production Ready  
**Last Security Review**: 2026-02-25 (ClawHub)  
**Dependencies Audit**: Clean (0 vulnerabilities)  
**Privacy Rating**: Local-first with optional cloud