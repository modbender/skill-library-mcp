# Security Guidelines

## Overview

OpenClaw Janitor requires powerful system permissions to perform its cleanup and session management tasks. This document explains the security implications, risks, and mitigations.

## ⚠️ Security Classification

**Classification:** Powerful System Tool with Inherent Risks

Janitor is classified as a **high-privilege skill** due to:
- Broad file system access (read/write/delete)
- Process execution capabilities
- External network communication
- Automated destructive operations

## Required Permissions

### 1. File System Permissions

**Permission:** `filesystem:read`, `filesystem:write`

**Why Required:**
- Read session files to calculate token usage
- Delete cache files, logs, and old sessions
- Archive sessions to compressed files
- Create backup directories

**Risks:**
- Could delete important files if misconfigured
- Could read sensitive data in session files
- Could write malicious files if compromised

**Mitigations:**
- Protected file list prevents deletion of critical files
- All deletions are logged
- Archive before delete (sessions are backed up)
- Configurable dry-run mode
- User confirmation required for aggressive operations

### 2. Process Execution

**Permission:** `process:execute`

**Why Required:**
- Execute git commands for GitHub backup
- Execute tar/gzip for session archiving
- Execute shell scripts for pre-start cleanup

**Risks:**
- Shell command injection if inputs not sanitized
- Arbitrary code execution if compromised
- Resource exhaustion from runaway processes

**Mitigations:**
- All shell commands use parameterized inputs
- Input validation on all user-provided values
- Timeout limits on all exec operations (10-60 seconds)
- No user input passed directly to shell
- Commands are hard-coded, not dynamic

### 3. Network Communication

**Permission:** Implicit (Node.js https module)

**Why Required:**
- Send notifications to Telegram/Discord
- Push archives to GitHub repository

**Risks:**
- Data exfiltration if compromised
- Credential exposure in environment variables
- Man-in-the-middle attacks

**Mitigations:**
- All network requests use HTTPS
- Credentials stored in environment variables, not code
- User configures endpoints (no hard-coded servers)
- Network calls are optional and user-controlled
- Failed requests are logged but don't stop cleanup

## Security Features

### 1. Protected Files

Janitor **NEVER** deletes these files/directories:

```javascript
// From janitor.js isImportant() method
const protectedPatterns = [
  'package.json',
  'package-lock.json',
  'node_modules',
  '.git',
  '.gitignore',
  'README.md',
  '.env',
  'src/',
  'config',
  '.npmrc',
  '.yarnrc'
];
```

### 2. Input Validation

All external inputs are validated:

```javascript
// File paths are validated
if (filePath.includes('..') || !filePath.startsWith(workingDir)) {
  throw new Error('Invalid file path');
}

// URLs are validated
if (!url.match(/^https:\/\//)) {
  throw new Error('Only HTTPS URLs allowed');
}

// Commands are parameterized
execAsync(`git commit -m "${sanitize(message)}"`, { timeout: 30000 });
```

### 3. Dry-Run Mode

Test operations without actual changes:

```bash
# Preview what will be deleted
node index.js clean --dry-run

# Preview session pruning
node index.js context clean moderate --dry-run
```

### 4. Archive Before Delete

All session deletions create backups first:

```javascript
// From pruner.js
await this.archiver.archiveSessions(sessionsToDelete);
// Only then delete
await this._deleteSessions(sessionsToDelete);
```

### 5. Audit Logging

All operations are logged:

```javascript
// From janitor.js
this.log('INFO', `Deleted ${filesDeleted} files, saved ${spaceSaved}`);
this.log('WARN', `Pruned ${prunedCount} sessions, freed ${tokensFreed} tokens`);
this.log('ERROR', `Emergency cleanup triggered at ${usagePercent}%`);
```

### 6. Rate Limiting

Background monitoring has safe intervals:

```javascript
// Minimum 1 minute between checks (default: 5 minutes)
if (intervalMinutes < 1) {
  throw new Error('Interval too short, minimum 1 minute');
}
```

### 7. Resource Limits

Process execution has timeouts:

```javascript
// All exec calls have max 60 second timeout
execAsync(command, {
  timeout: 60000,        // 60 seconds max
  maxBuffer: 50 * 1024 * 1024  // 50MB max output
});
```

## Threat Model

### Threat 1: Malicious Configuration

**Attack:** User provides malicious GitHub URL or notification webhook

**Impact:** Data exfiltration via network requests

**Mitigation:**
- User explicitly configures all endpoints
- No default external endpoints
- HTTPS required for all requests
- Credentials are user's own (not shared)
- User reviews config before use

### Threat 2: Path Traversal

**Attack:** Attacker provides `../../etc/passwd` as file path

**Impact:** Deletion or reading of system files

**Mitigation:**
- All paths validated against base directory
- `..` sequences rejected
- Symbolic link following disabled
- Protected patterns enforced

### Threat 3: Command Injection

**Attack:** Attacker injects shell commands via git commit message

**Impact:** Arbitrary code execution

**Mitigation:**
- No user input passed directly to shell
- All parameters sanitized
- Heredoc used for multi-line strings
- Command arrays used where possible

### Threat 4: Dependency Compromise

**Attack:** Malicious npm package in dependency chain

**Impact:** Full system compromise

**Mitigation:**
- Zero external dependencies (only Node.js built-ins)
- No `npm install` required
- All code is in the repository

### Threat 5: Accidental Deletion

**Attack:** User misconfigures and deletes important sessions

**Impact:** Data loss

**Mitigation:**
- Archives created before deletion
- 30-day archive retention
- `listArchives()` and `restoreArchive()` available
- Dry-run mode for testing
- Confirmation prompts for aggressive operations

## Safe Usage Guidelines

### 1. Review Configuration

Before first use, review all settings:

```bash
# View current configuration
node index.js config list

# Check what will be deleted
node index.js clean --dry-run
```

### 2. Start Conservative

Use conservative settings initially:

```javascript
const janitor = new Janitor({
  sessionManagement: {
    pruning: {
      maxSessionAge: 14,  // Keep sessions longer
      keepRecentHours: 48  // Protect recent sessions
    },
    monitoring: {
      alertThreshold: 90,  // Alert only at high usage
      emergencyThreshold: 95  // Emergency only at critical
    }
  }
});
```

### 3. Monitor Logs

Check logs regularly:

```bash
# On systemd systems
sudo journalctl -u janitor-monitor@$USER -f

# Or application logs
tail -f ~/.openclaw/logs/janitor.log
```

### 4. Test Notifications

Verify notification channels work correctly:

```bash
node index.js test notifications
```

### 5. Backup Archives

Keep archive backups external:

```bash
# Enable GitHub backup
export GITHUB_BACKUP_REPO="https://github.com/user/backups.git"
node index.js config set sessionManagement.archiving.gitHubBackup true
```

### 6. Use Dry-Run

Always test destructive operations first:

```bash
# Test what emergency cleanup would do
node index.js context emergency --dry-run

# Test moderate cleanup
node index.js context clean moderate --dry-run
```

## Security Checklist

Before deploying Janitor in production:

- [ ] Review all configuration settings
- [ ] Test dry-run mode for all destructive operations
- [ ] Verify protected files list includes your critical files
- [ ] Configure notification channels securely
- [ ] Set up GitHub backup repository (optional)
- [ ] Test archive restoration process
- [ ] Review systemd service permissions
- [ ] Set appropriate pruning thresholds
- [ ] Enable audit logging
- [ ] Monitor initial cleanups manually
- [ ] Document your configuration

## Incident Response

If you suspect Janitor has been compromised:

1. **Stop immediately:**
   ```bash
   node index.js monitor stop
   sudo systemctl stop janitor-monitor@$USER
   ```

2. **Review logs:**
   ```bash
   # Check what was deleted
   grep "Deleted" ~/.openclaw/logs/janitor.log

   # Check network activity
   grep "Notification sent" ~/.openclaw/logs/janitor.log
   ```

3. **Restore from archives:**
   ```bash
   # List available archives
   node index.js archives list

   # Restore specific archive
   node index.js archives restore sessions-2026-02-08.tar.gz
   ```

4. **Review configuration:**
   ```bash
   # Check for malicious settings
   node index.js config list

   # Reset to defaults if needed
   node index.js config reset
   ```

5. **Report issue:**
   - File issue at: https://github.com/openclaw/janitor/issues
   - Include: logs, configuration, what happened

## Responsible Disclosure

If you discover a security vulnerability in Janitor:

1. **Do NOT** open a public GitHub issue
2. Email: security@openclaw.ai (or repository maintainer)
3. Include: description, reproduction steps, impact assessment
4. Allow time for patch before public disclosure

## Permissions Justification

### Why Janitor Needs These Permissions

| Permission | Justification | Can It Be Reduced? |
|------------|---------------|-------------------|
| `filesystem:read` | Must read session files to count tokens | No - core functionality |
| `filesystem:write` | Must delete cache/sessions, create archives | No - core functionality |
| `process:execute` | Git/tar commands for backup/archive | Partially - can disable GitHub backup |
| Network access | Optional notifications and backup | Yes - disable notifications/backup |

### Principle of Least Privilege

To minimize risk while maintaining functionality:

```javascript
// Minimal configuration (no network, no GitHub)
const janitor = new Janitor({
  sessionManagement: {
    archiving: {
      enabled: true,      // Local archives only
      gitHubBackup: false  // Disable network
    },
    notifications: {
      channels: ['log']    // No external notifications
    }
  }
});
```

## Trust Model

**You should trust Janitor if:**
- You've reviewed the source code
- You understand the operations it performs
- You've tested it in dry-run mode
- You control all configuration endpoints
- You monitor its activity

**You should NOT trust Janitor if:**
- You haven't reviewed the code
- Configuration comes from untrusted source
- Running on a shared/multi-tenant system
- Credentials are shared or exposed
- You need zero-risk file operations

## Conclusion

Janitor is a **powerful tool that requires trust**. Its capabilities are necessary for its function (automated cleanup and session management), but inherently carry risk.

**Recommendations:**
1. Only install if you understand and accept the risks
2. Review all code before first use
3. Start with conservative configuration
4. Use dry-run mode extensively
5. Monitor logs during initial deployment
6. Keep archives backed up externally
7. Consider disabling network features if not needed

**Risk vs. Benefit:**
- **High Risk:** File deletion, process execution, network access
- **High Benefit:** Prevents context overflow, automates cleanup, saves storage
- **Acceptable If:** You review code, test thoroughly, monitor actively

For questions or concerns, please review the documentation or contact the maintainers.

---

**Last Updated:** 2026-02-08
**Version:** 1.1.0
