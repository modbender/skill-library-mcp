# Security Policy

## 🔒 Security Features

iCalendar Sync v2.2.0 implements enterprise-grade security measures:

### Credential Protection

- **System Keyring Integration**: Credentials stored in OS-native secure storage
  - macOS: Keychain
  - Windows: Credential Manager
  - Linux: Secret Service (GNOME Keyring, KWallet)
- **Fallback Encryption**: .env files with 0600 permissions
- **Log Filtering**: Automatic redaction of passwords and emails from logs

### Input Validation

- **Calendar Names**: Regex validation (`^[a-zA-Z0-9\s_-]+$`)
- **Text Fields**: Sanitization and length limits
  - Summary: 500 characters
  - Description: 5000 characters
  - Location: 500 characters
- **File Size**: 1MB limit for JSON inputs
- **Email Validation**: RFC-compliant regex
- **Path Validation**: Protection against directory traversal

### Attack Prevention

- **Rate Limiting**: 10 API calls per 60-second window
- **SSL Verification**: Enforced certificate validation
- **Injection Protection**: All inputs sanitized
- **DoS Protection**: Size limits, timeouts, rate limiting
- **Thread Safety**: Locks on shared resources

### Code Security

- **Memory Safety**: Traceback cleanup in exception handlers
- **Atomic Operations**: File writes use tempfile + move
- **Timeout Protection**: 30-second timeout on interactive inputs
- **Type Validation**: Strict type checking on all inputs

## 🚨 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 2.2.x   | :white_check_mark: |
| 2.1.x   | :x: (upgrade)      |
| 2.0.x   | :x: (upgrade)      |
| < 2.0   | :x:                |

## 📝 Reporting a Vulnerability

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: security@clawhub.ai (or create private security advisory)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Triage**: Within 5 business days
- **Fix & Release**: Depends on severity
  - Critical: 1-3 days
  - High: 5-7 days
  - Medium: 2-4 weeks
  - Low: Next minor release

## 🛡️ Security Audit Results (v2.2.0)

### Vulnerability Summary

- **Critical**: 0 ✅
- **High**: 0 ✅
- **Medium**: 0 ✅
- **Low**: 4 ⚠️ (non-security impacting)

### Overall Rating: **A** (Excellent)

### Known Low-Risk Items

1. **HMAC for .env**: Not implemented (mitigated by keyring primary storage)
2. **ReDoS in SensitiveDataFilter**: Theoretical on extremely long strings
3. **Windows timeout fallback**: No timeout on Windows (acceptable tradeoff)
4. **RRULE validation**: Missing FREQ enum validation (minor UX issue)

## 🔐 Best Practices for Users

### Credential Management

1. **Use App-Specific Passwords**: Never use your main Apple ID password
2. **Generate at**: https://appleid.apple.com → Sign-In & Security → App-Specific Passwords
3. **Rotate Regularly**: Create new passwords every 6-12 months
4. **Revoke Old Passwords**: Remove unused app-specific passwords

### System Hardening

1. **Update Dependencies**: `pip install --upgrade openclaw-icalendar-sync`
2. **File Permissions**: Ensure ~/.openclaw/.env is 0600 (if used)
3. **Log Rotation**: Configure log rotation for /var/log if running as service
4. **Network Security**: Use firewall rules if exposed

### Multi-Agent Isolation

- Each agent gets separate credentials
- Use different calendar names per agent
- Rate limiting applies per CalendarManager instance
- Thread-safe for concurrent access

## 📊 Security Testing

### Automated Tests

```bash
# Run security tests
pytest tests/test_security.py -v

# Check for known vulnerabilities
pip-audit

# Static analysis
bandit -r src/
```

### Manual Testing

- Injection attacks (SQL, Command, Path Traversal)
- Authentication bypass attempts
- Rate limit testing
- Memory leak detection
- Concurrent access testing

## 📝 Compliance

- **OWASP Top 10**: Addressed all applicable items
- **CWE Coverage**: Protected against common weaknesses
- **PCI DSS**: Not applicable (no payment card data)
- **GDPR**: User data stored locally, full control

## 🔗 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [CalDAV Security](https://datatracker.ietf.org/doc/html/rfc4791#section-8)
- [Apple ID Security](https://support.apple.com/en-us/HT204915)

---

**Last Updated**: February 9, 2026  
**Security Version**: 2.2.0  
**Audit Date**: February 9, 2026
