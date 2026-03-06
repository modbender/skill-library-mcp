# Security Audit Checklist

Comprehensive security checklist for code, files, and agent skills.

## Quick Reference

**Use this checklist when:**
- Auditing new code before deployment
- Reviewing pull requests
- Security assessment of agent skills
- Regular security reviews

**Severity Levels:**
- 🚨 **CRITICAL**: Fixes required immediately
- ⚠️ **HIGH**: Priority fixes, block deployment
- ⚡ **MEDIUM**: Important fixes, track and schedule
- ℹ️ **LOW**: Nice to have, document exceptions

---

## 1. Secrets and Credentials

### 1.1 No Hardcoded Secrets
- [ ] No API keys in code
- [ ] No passwords in code
- [ ] No private keys in code
- [ ] No tokens in code
- [ ] No keys/tokens in environment files committed to repo

**Check:** Search for common patterns:
- `api_key`, `apikey`, `api-key`
- `secret`, `password`, `token`
- `private_key`, `sk_live`, `ghp_`
- `0x[a-fA-F0-9]{64}` (Ethereum keys)

**Severity:** 🚨 CRITICAL

---

## 2. Input Validation

### 2.1 User Input Handling
- [ ] All user input is sanitized
- [ ] Input types are validated
- [ ] Input length limits enforced
- [ ] Input character sets enforced
- [ ] Reject unexpected input types

**Severity:** ⚠️ HIGH

### 2.2 File Operations
- [ ] File paths validated
- [ ] Path traversal prevented (no `..` outside expected)
- [ ] File type whitelist enforced
- [ ] File size limits enforced
- [ ] No user-controlled file operations on system files

**Severity:** 🚨 CRITICAL

### 2.3 Database Operations
- [ ] Parameterized queries used (no concatenation)
- [ ] No SQL injection vulnerabilities
- [ ] Input not concatenated into queries
- [ ] Database permissions least-privilege

**Severity:** 🚨 CRITICAL

---

## 3. Code Execution

### 3.1 Dynamic Code Execution
- [ ] No `eval()` on user input
- [ ] No `exec()` on user input
- [ ] No compiler/code generators on user input
- [ ] No dynamic imports from user input

**Severity:** 🚨 CRITICAL

### 3.2 System Commands
- [ ] No `os.system()` with user input
- [ ] No `subprocess` with `shell=True` and user input
- [ ] No `popen()` with user input
- [ ] All commands use parameterized lists

**Severity:** 🚨 CRITICAL

---

## 4. Cryptography

### 4.1 Algorithm Security
- [ ] No MD5 for cryptographic purposes
- [ ] No SHA1 for cryptographic purposes
- [ ] No DES/RC4 ciphers
- [ ] Using strong algorithms (SHA-256+, AES-256)

**Severity:** ⚠️ HIGH

### 4.2 Key Management
- [ ] No hardcoded keys
- [ ] Keys stored securely (env vars, KMS)
- [ ] Keys rotated periodically
- [ ] Key derivation functions used properly

**Severity:** 🚨 CRITICAL

### 4.3 Random Number Generation
- [ ] No `random` module for crypto operations
- [ ] No `math.random()` for security
- [ ] Using `secrets` module for crypto
- [ ] Using `os.urandom()` for entropy

**Severity:** ⚠️ HIGH

---

## 5. Network Security

### 5.1 HTTP/Network Requests
- [ ] No arbitrary URLs from user input
- [ ] URL validation before requests
- [ ] HTTPS required for external APIs
- [ ] Certificate verification enabled

**Severity:** ⚠️ HIGH

### 5.2 Authentication
- [ ] Strong password policies
- [ ] Multi-factor authentication where appropriate
- [ ] Session tokens are secrets length
- [ ] Secure session handling

**Severity:** ⚡ MEDIUM

### 5.3 Authorization
- [ ] Proper authorization checks
- [ ] No authenticated ID bypass
- [ ] Role-based access control
- [ ] Least privilege principle applied

**Severity:** ⚠️ HIGH

---

## 6. Data Security

### 6.1 Data at Rest
- [ ] Sensitive data encrypted
- [ ] Database credentials secure
- [ ] No plain text passwords
- [ ] Secure key management

**Severity:** ⚠️ HIGH

### 6.2 Data in Transit
- [ ] HTTPS required
- [ ] TLS/SSL properly configured
- [ ] No unencrypted sensitive data in transit
- [ ] Certificate validation

**Severity:** ⚠️ HIGH

### 6.3 Data in Use
- [ ] Sensitive data cleared from memory
- [ ] No secrets in logs
- [ ] No debug output with secrets
- [ ] Error messages don't leak info

**Severity:** ⚡ MEDIUM

---

## 7. Cryptocurrency and Blockchain

### 7.1 Wallet Security
- [ ] No hardcoded mnemonics
- [ ] No hardcoded private keys
- [ ] No exposed seed phrases
- [ ] Wallet signing operations isolated

**Severity:** 🚨 CRITICAL

### 7.2 Transaction Safety
- [ ] Amount validation before transactions
- [ ] Address validation before sending
- [ ] Gas limit checks
- [ ] Transaction signing requires explicit approval

**Severity:** 🚨 CRITICAL

### 7.3 Smart Contracts
- [ ] Contract addresses verified
- [ ] No unlimited approvals
- [ ] Reentrancy protections
- [ ] Access control on functions

**Severity:** ⚠️ HIGH

### 7.4 External Dependencies
- [ ] Audited contract verification
- [ ] No unaudited external calls
- [ ] Checked for known vulnerabilities
- [ ] Verified contract source code

**Severity:** ⚠️ HIGH

---

## 8. Error Handling

### 8.1 Information Leakage
- [ ] No stack traces to users
- [ ] Internal details hidden in errors
- [ ] Generic error messages to users
- [ ] Detailed errors logged securely

**Severity:** ⚡ MEDIUM

### 8.2 Fail-Safe Defaults
- [ ] Fail closed on errors
- [ ] No continue on critical errors
- [ ] Proper error exceptions raised
- [ ] Error recovery procedures documented

**Severity:** ⚡ MEDIUM

---

## 9. Logging and Monitoring

### 9.1 Secure Logging
- [ ] No secrets in logs
- [ ] No sensitive data in logs
- [ ] Log level appropriate (not DEBUG in production)
- [ ] Log tamper-proof

**Severity:** ⚡ MEDIUM

### 9.2 Monitoring
- [ ] Security events logged
- [ ] Alert on suspicious activity
- [ ] Audit trails enabled
- [ ] Log retention policy defined

**Severity:** ℹ️ LOW

---

## 10. Dependencies

### 10.1 Third-Party Packages
- [ ] Dependencies are up-to-date
- [ ] No known vulnerabilities (`pip-audit`, `npm audit`)
- [ ] Only necessary dependencies included
- [ ] License compliance verified

**Severity:** ⚡ MEDIUM

### 10.2 External APIs
- [ ] API credentials secure
- [ ] Rate limiting handled
- [ ] Error codes handled
- [ ] API endpoints verified

**Severity:** ⚠️ HIGH

---

## 11. Agent Skills Specific

### 11.1 Skill Structure
- [ ] SKILL.md exists
- [ ] Proper frontmatter (name, description)
- [ ] No secrets in skill folder
- [ ] Documentation complete

**Severity:** ⚠️ HIGH

### 11.2 Skill Code
- [ ] No dangerous system commands
- [ ] No file operations on system paths
- [ ] No hardcoded credentials
- [ ] Input validation on all parameters

**Severity:** 🚨 CRITICAL

### 11.3 Skill Resources
- [ ] Scripts are executable and safe
- [ ] Reference files don't contain secrets
- [ ] No malicious patterns in dependencies
- [ ] Proper error handling

**Severity:** ⚠️ HIGH

---

## 12. Deployment

### 12.1 Environment Configuration
- [ ] Environment variables defined
- [ ] Different configs for dev/prod
- [ ] Secrets not in version control
- [ ] .gitignore includes sensitive files

**Severity:** 🚨 CRITICAL

### 12.2 Access Control
- [ ] Server access restricted
- [ ] SSH keys are secure
- [ ] Firewall rules configured
- [ ] Admin access limited

**Severity:** ⚠️ HIGH

### 12.3 Updates and Patching
- [ ] Automated security updates
- [ ] Vulnerability scanning scheduled
- [ ] Incident response plan defined
- [ ] Backup and recovery tested

**Severity:** ⚡ MEDIUM

---

## Scoring

**Pass Criteria:**
- 🚨 CRITICAL: 100% required
- ⚠️ HIGH: ≥90% pass (exceptions documented)
- ⚡ MEDIUM: ≥70% pass (exceptions documented)
- ℹ️ LOW: Document exceptions if needed

**Risk Tolerance:**
- Production: All CRITICAL/HIGH must pass
- Development: Document CRITICAL, schedule fixes
- Testing: May accept some MEDIUM/LOW with waivers

---

## Audit Procedure

1. **Automated Scanning**
   ```bash
   python3 scripts/threat_scan.py /path/to/code --severity all
   python3 scripts/secret_scan.py /path/to/code
   python3 scripts/skill_audit.py /path/to/skill
   ```

2. **Manual Review**
   - Review findings
   - Check false positives
   - Verify severity levels
   - Document exceptions

3. **Remediation**
   - Prioritize CRITICAL and HIGH
   - Apply fixes
   - Re-scan
   - Verify fixes

4. **Documentation**
   - Record audit results
   - Track remediation
   - Update security policies
   - Schedule next audit

---

## Tools Reference

| Tool | Purpose | Usage |
|------|---------|-------|
| threat_scan.py | Pattern-based vulnerability detection | Scan codebases for common issues |
| secret_scan.py | Secret detection | Find hardcoded credentials |
| skill_audit.py | Skill security audit | Comprehensive skill security review |
| pip-audit | Python dependency vulnerabilities | `pip-audit` |
| npm audit | Node.js dependency vulnerabilities | `npm audit` |
| bandit | Python security linter | `bandit -r path/` |
| safety | Python dependency checker | `safety check` |

---

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cse.google.com/cse?cx=017710025075936659711:qr5s2zr0qkg&q=CWE+SANS+Top+25)
- [CWE Top 25 Most Dangerous Software Errors](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
