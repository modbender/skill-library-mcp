# iapctl - Aruba IAP Configuration Management CLI

Stable, secure CLI tool for managing Aruba Instant Access Points (IAP) with standardized JSON output and full audit trail.

## Features

- **Stable Connection**: Handles prompts, pagination, timeouts, and retries automatically
- **Standardized Output**: JSON + raw text logs for OpenClaw auditing/dashboard
- **Secure**: SSH key authentication, secret redaction, approval workflow
- **Complete Operations**: discover, snapshot, diff, apply, verify, rollback

## Installation

```bash
# From local directory
cd iapctl
pip install -e .

# Or from PyPI (when published)
pip install iapctl
```

## Quick Start

```bash
# Discover cluster
iapctl discover --cluster office-iap --vc 192.168.20.56 --out ./out

# Take snapshot
iapctl snapshot --cluster office-iap --vc 192.168.20.56 --out ./out
```

## Commands

### discover
Gather basic IAP cluster information.

```bash
iapctl discover --cluster <name> --vc <ip> --out <dir>
```

### snapshot
Take full configuration snapshot.

```bash
iapctl snapshot --cluster <name> --vc <ip> --out <dir>
```

### diff
Generate diff between current and desired state.

```bash
iapctl diff --cluster <name> --vc <ip> --in changes.json --out <dir>
```

### apply
Apply configuration changes.

```bash
iapctl apply --cluster <name> --vc <ip> --change-id <id> --in commands.json --out <dir>
```

### verify
Verify configuration state.

```bash
iapctl verify --cluster <name> --vc <ip> --level basic --expect expect.json --out <dir>
```

### rollback
Rollback to previous configuration.

```bash
iapctl rollback --cluster <name> --vc <ip> --from-change-id <id> --out <dir>
```

## Authentication

### SSH Key (Recommended)

```bash
# Add SSH key to IAP
ssh-copy-id admin@<iap-ip>

# Configure in ~/.ssh/config
Host office-iap-vc
  HostName 192.168.20.56
  User admin
  IdentityFile ~/.ssh/aruba_iap_key
```

### Password

```bash
iapctl discover --cluster office-iap --vc 192.168.20.56 --ssh-password yourpassword
```

## Output Format

Every command generates:

1. **result.json** - Structured output (machine-readable)
2. **raw/*.txt** - Raw CLI outputs (human-auditable)

### result.json Structure

```json
{
  "ok": true,
  "action": "snapshot",
  "cluster": "office-iap",
  "vc": "192.168.20.56",
  "os_major": "8",
  "is_vc": true,
  "artifacts": [
    {
      "name": "result.json",
      "path": "./out/snapshot/result.json",
      "size_bytes": 1024,
      "content_type": "application/json"
    }
  ],
  "checks": [],
  "warnings": [],
  "errors": [],
  "timing": {
    "total_seconds": 2.5,
    "steps": {
      "version": 0.3,
      "running_config": 0.8,
      "wlan": 0.4
    }
  },
  "timestamp": "2026-02-22T10:30:00.000Z"
}
```

## Changes Format (for diff/apply)

```json
{
  "changes": [
    {
      "type": "ntp",
      "servers": ["10.10.10.1", "10.10.10.2"]
    },
    {
      "type": "ssid_vlan",
      "profile": "Corporate",
      "essid": "CorporateWiFi",
      "vlan_id": 100
    },
    {
      "type": "radius_server",
      "name": "radius-primary",
      "ip": "10.10.10.5",
      "auth_port": 1812,
      "acct_port": 1813,
      "secret_ref": "secret:radius-primary"
    }
  ]
}
```

## Secret Management

Secrets use `secret_ref` pattern, not plain text:

```json
{
  "type": "radius_server",
  "secret_ref": "secret:radius-primary"
}
```

iapctl resolves secret_ref from:
- macOS Keychain
- Environment variables
- Configured vault

All outputs show `***REDACTED***` for secrets.

## OpenClaw Integration

### Allowlist

```json
{
  "allowedTools": [
    "Bash(iapctl:*)"
  ]
}
```

### Approvals

- `apply` and `rollback` require approval
- `discover`, `snapshot`, `diff`, `verify` can be auto-approved

### Workflow

```bash
# 1. Take baseline
iapctl snapshot --cluster office-iap --vc 192.168.20.56 --out ./baseline

# 2. Generate diff
iapctl diff --cluster office-iap --vc 192.168.20.56 --in changes.json --out ./diff

# 3. Review and approve (OpenClaw approval flow)

# 4. Apply changes
iapctl apply --cluster office-iap --vc 192.168.20.56 --change-id chg_20260222_0001 --in ./diff/commands.json --out ./apply

# 5. Verify
iapctl verify --cluster office-iap --vc 192.168.20.56 --level basic --expect ./diff/expect.json --out ./verify
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black iapctl/
ruff check iapctl/

# Type check
mypy iapctl/
```

## License

MIT
