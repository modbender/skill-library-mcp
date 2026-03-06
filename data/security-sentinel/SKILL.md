---
name: security-sentinel
description: Scan the workspace for security vulnerabilities, exposed secrets, and misconfigurations.
---

# Security Sentinel

A unified security scanner for OpenClaw workspaces. Detects vulnerabilities in dependencies (npm audit), exposed secrets (regex patterns), and unsafe file permissions.

## Usage

### CLI

Run a full security scan:

```bash
node skills/security-sentinel/index.js
```

This will output a JSON report to stdout.
If risks are detected (high/critical vulnerabilities, secrets, or bad permissions), it exits with code 1.

### Options

- `--skip-audit`: Skip the npm audit step (faster)
- `--no-fail`: Do not exit with code 1 even if risks are detected (useful for monitoring only)

### Programmatic

```javascript
const sentinel = require('./skills/security-sentinel');

const report = await sentinel.scan();

if (report.status === 'risk_detected') {
  console.error('Security issues found:', report);
}
```

## Features

1. **Dependency Audit**: Runs `npm audit` to check `package.json` dependencies for known CVEs.
2. **Secret Detection**: Scans workspace files for patterns resembling API keys, passwords, and private keys.
3. **Permission Check**: Verifies critical files (`package.json`, `.env`) are not world-writable.

## Configuration

- **Ignored Paths**: `node_modules`, `.git`, `logs`, `temp`, `.openclaw/cache`.
- **Secret Patterns**: Generic API Key, Password, Private Key, Feishu App Secret.
