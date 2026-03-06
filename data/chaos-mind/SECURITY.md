# Security Policy

## Security Model

CHAOS Memory is designed with security and privacy as core principles:

### 1. Installation Security

**No Automatic Remote Script Execution:**
- Install script (`install.sh`) **requires Dolt pre-installed**
- Does NOT automatically run `curl | bash` for dependencies
- Users must install Dolt via their package manager:
  - macOS: `brew install dolt`
  - Linux: `brew install dolt` or apt/yum
  - Windows: `choco install dolt`

**Binary Distribution:**
- Binaries downloaded from GitHub Releases (signed, reproducible builds)
- Built via GitHub Actions (public workflow)
- SHA256 checksums provided for verification
- Source code available for audit

**No Build-Time Risks:**
- Pre-built binaries (no compilation during install)
- No npm/pip install that could run arbitrary code
- Install script is auditable before running

### 2. Runtime Security

**Local-Only Operation:**
- All data stored locally: `~/.chaos/db`
- No cloud sync or external transmission
- No telemetry or analytics
- No network access during normal operation

**SQL Injection Prevention:**
- `chaos-cli` sanitizes all user input
- Single quotes escaped before SQL execution
- No dynamic SQL string concatenation
- Limited to SELECT queries (read-only CLI)

**Command Injection Prevention:**
- No `eval` or `exec` of user input
- No shell command execution from user strings
- All file paths validated and sanitized

### 3. Data Privacy

**Auto-Capture (Opt-In Only):**
- **Disabled by default**
- Requires explicit configuration in `~/.chaos/config.yaml`
- User explicitly chooses which paths to process
- Only processes files in configured `auto_capture.sources` list

**Session Transcript Access:**
- Only reads paths explicitly configured by user
- No automatic discovery of session files
- User controls: which files, when processed, what's extracted
- All processing happens locally (via Ollama)

**Data Storage:**
- Plain Dolt SQL database (auditable)
- Version-controlled (git-like history)
- No encryption at rest (user can add disk encryption)
- No cloud backup (user controls backups)

### 4. Permissions

**Read Permissions:**
- Session transcripts: Only paths in `auto_capture.sources`
- Database: Local only (`~/.chaos/db`)
- Config: Local only (`~/.chaos/config.yaml`)

**Write Permissions:**
- Database: Local only (`~/.chaos/db`)
- Logs: Local only (`~/.chaos/consolidator.log`)
- State: Local only (`~/.chaos/consolidator-state.json`)

**Network Permissions:**
- None (except initial binary download during install)
- Ollama communication: localhost only (127.0.0.1:11434)
- No external API calls
- No cloud services

### 5. Threat Model

**Protected Against:**
- SQL injection (input sanitization)
- Command injection (no shell eval)
- Remote code execution (no curl|bash after install)
- Data exfiltration (no network access)
- Unauthorized file access (explicit path configuration)

**User Responsibility:**
- Installing Dolt from trusted package manager
- Configuring auto-capture paths responsibly
- Protecting database with filesystem permissions
- Reviewing install script before running

**Not Protected Against:**
- Malicious Dolt binary (user installs via package manager)
- Malicious Ollama (user installs separately)
- Filesystem access by other processes
- Physical access to machine

### 6. Transparency

**Open Source:**
- Full source code: https://github.com/hargabyte/Chaos-mind
- GitHub Actions workflows: public and auditable
- Binary checksums: provided with each release

**Auditable:**
- Install script included in repo (review before running)
- Database is plain SQL (inspect with `dolt sql`)
- No obfuscated or minified code
- Clear logging (what's processed, what's stored)

**Reproducible:**
- GitHub Actions builds are reproducible
- Build from source instructions provided
- Dependencies pinned to versions

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT** open a public GitHub issue
2. Email: security@hargabyte.com
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and provide:
- Acknowledgment of report
- Timeline for fix
- Credit in security advisory (if desired)

## Security Updates

- Security patches released as patch versions (e.g., 1.0.1)
- Critical vulnerabilities disclosed after patch available
- Users notified via GitHub Security Advisories

## Best Practices

**For Users:**
1. Install Dolt from official package managers only
2. Review `install.sh` before running
3. Keep auto-capture disabled unless needed
4. Audit configured session paths regularly
5. Protect `~/.chaos/` with filesystem permissions
6. Regularly update to latest version

**For Developers:**
1. Never execute remote scripts automatically
2. Sanitize all user input before SQL
3. Avoid shell command execution
4. Log all file access for auditability
5. Keep dependencies minimal and pinned
6. Provide reproducible builds

## Version History

**v1.0.0:**
- Initial release
- SQL injection prevention in chaos-cli
- No automatic curl|bash for dependencies
- Auto-capture opt-in with explicit configuration
- Local-only operation (no network access)

---

Last updated: 2026-02-06
