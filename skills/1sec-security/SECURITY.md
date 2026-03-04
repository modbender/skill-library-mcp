# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in 1-SEC, please report it responsibly:

- **Email**: security@1-sec.dev
- **PGP Key**: [Available at https://1-sec.dev/pgp.asc]
- **Response Time**: We aim to respond within 48 hours

Please do not open public GitHub issues for security vulnerabilities.

## Supply Chain Security

1-SEC follows industry best practices for supply chain security:

- **Build Process**: All releases are built via GitHub Actions with reproducible builds
- **Checksums**: SHA256 checksums are generated during the build and published alongside every release binary in `checksums.txt`
- **Artifact Signing**: GPG signing of release artifacts is planned for a future release
- **SBOMs**: Software Bill of Materials generated for each release
- **Dependencies**: All dependencies are pinned and verified with checksums
- **Source Code**: Fully open source under AGPL-3.0 license

## Verification

### Verify Release Integrity

```bash
# Download release and checksums
VERSION="0.4.11"
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/1sec-linux-amd64
wget https://github.com/1sec-security/1sec/releases/download/v${VERSION}/checksums.txt

# Verify SHA256 checksum
sha256sum -c checksums.txt 2>&1 | grep 1sec-linux-amd64
```

### Installer Script Source

The installer script source code is publicly available for review at:
https://github.com/1sec-security/1sec/blob/main/get.sh

The script downloads the same versioned binary from GitHub Releases used in
the manual install path above, and verifies its SHA256 checksum before
installing. **We recommend the manual install path** (download binary +
verify checksum) over any script-based method for production systems.

## Data Handling & Privacy

### Local Processing
- All log analysis and threat detection happens locally by default
- No data is sent externally unless explicitly configured
- Module detection logic runs entirely on-host

### Optional External Connections

1. **Webhook Notifications** (opt-in)
   - User configures webhook URLs in config
   - Only alert metadata is sent (severity, module, timestamp, source IP)
   - No log content or sensitive data included in webhooks
   - Supports Slack, Discord, Telegram, PagerDuty, Microsoft Teams

2. **Cloud API** (opt-in)
   - Disabled by default
   - Enable via `cloud.enabled: true` in config
   - Used for centralized management of multiple 1-SEC instances
   - Sends alert metadata and enforcement statistics
   - API key required (user-generated)

3. **AI Analysis** (opt-in)
   - Requires `GEMINI_API_KEY` environment variable
   - Only used for cross-module correlation (module 16)
   - Sends alert metadata to Gemini API for pattern analysis
   - No raw log content sent to AI service
   - All 15 rule-based modules work without any API key

### What We Don't Collect
- No telemetry or usage statistics by default
- No personally identifiable information (PII)
- No log file contents sent externally
- No automatic crash reports or error reporting

## Self-Update Mechanism

1-SEC includes a self-update feature that checks for new releases daily:

```bash
# Check for updates
1sec selfupdate --check

# Update to latest version
1sec selfupdate

# Disable auto-update checks
1sec config set auto_update false
```

The self-update mechanism:
- Downloads from GitHub releases (same source as manual install)
- Verifies checksums before applying updates
- Creates backup of current binary before updating
- Can be disabled entirely via config

## Enforcement Actions & Permissions

1-SEC enforcement actions require specific system permissions:

| Action | Required Permission | Risk Level |
|--------|-------------------|------------|
| `log_only` | None (read-only) | None |
| `webhook` | Network access | Low |
| `block_ip` | iptables/nftables (root) | Medium |
| `drop_connection` | Network control (root) | Medium |
| `kill_process` | Process management (root) | High |
| `quarantine_file` | File system access (root) | High |
| `disable_user` | User management (root) | High |

**Recommendation**: Run 1-SEC with root/sudo for full enforcement capabilities. For read-only monitoring, run as unprivileged user (only `log_only` and `webhook` actions will work).

## Uninstall

Complete removal of 1-SEC:

```bash
# 1. Stop the engine
1sec stop

# 2. Remove enforcement rules (iptables, blocked IPs, etc.)
1sec enforce cleanup

# 3. Remove binary
sudo rm /usr/local/bin/1sec

# 4. Remove data directory
rm -rf ~/.1sec

# 5. Remove config (if using system-wide config)
sudo rm -rf /etc/1sec
```

## Security Audit History

- **2026-02**: Initial security review by internal team
- **2026-01**: ClawHub.ai skill audit (transparency improvements implemented)

## Responsible Disclosure

We follow a 90-day coordinated disclosure policy:

1. Researcher reports vulnerability privately
2. We confirm and develop a fix
3. We release patched version
4. After 90 days (or earlier if agreed), public disclosure

## Security Best Practices

When deploying 1-SEC:

1. **Start with dry-run mode** to validate behavior before enforcement
2. **Use the `safe` preset** initially, then progress to more aggressive presets
3. **Configure webhook notifications** to monitor enforcement actions
4. **Review enforcement history** regularly: `1sec enforce history`
5. **Keep 1-SEC updated** to receive security patches
6. **Use manual install with checksum verification** for production deployments
7. **Test in isolated environment** before deploying to production
8. **Document your enforcement policies** and review them quarterly

## Contact

- **General inquiries**: hello@1-sec.dev
- **Security issues**: security@1-sec.dev
- **GitHub**: https://github.com/1sec-security/1sec
- **Documentation**: https://1-sec.dev/docs
