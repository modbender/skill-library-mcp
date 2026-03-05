# Quick Start: Aruba IAP Configuration Changes

This guide walks you through the basic workflow for applying configuration changes to Aruba IAP devices using iapctl.

## Prerequisites

1. Install iapctl:
```bash
cd /Users/scsun/.openclaw/workspace/skills/aruba-iap-publish
./install.sh
```

2. Verify SSH access to your IAP:
```bash
ssh admin@<your-iap-ip>
```

## Quick Workflow

### 1. Create a Changes File

Create `changes.json` with your desired configuration:

```json
{
  "changes": [
    {
      "type": "snmp_community",
      "community_string": "public123",
      "access": "ro"
    },
    {
      "type": "ssid_profile",
      "profile_name": "Aruba-IAP",
      "essid": "MyWiFi",
      "opmode": "wpa2-psk-aes",
      "wpa_passphrase": "MySecurePassword123",
      "vlan": 100,
      "rf_band": "all"
    }
  ]
}
```

### 2. Generate Diff and Risk Assessment

```bash
iapctl diff \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --in changes.json \
  --out ./diff
```

**Review the output:**
```bash
# View commands to be applied
cat diff/commands.txt

# Review risk assessment
cat diff/risk.json
```

### 3. Dry Run (Optional)

Test without actually applying changes:

```bash
iapctl apply \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --change-id test-run \
  --in diff/commands.json \
  --out ./dry-run \
  --dry-run
```

### 4. Apply Changes

```bash
iapctl apply \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --change-id chg_$(date +%Y%m%d_%H%M%S) \
  --in diff/commands.json \
  --out ./apply
```

**Automatic baseline capture:**
- `apply/pre_running-config.txt` - Configuration before changes
- `apply/post_running-config.txt` - Configuration after changes

### 5. Verify Changes

```bash
iapctl verify \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --level full \
  --out ./verify
```

### 6. Rollback (if needed)

```bash
iapctl rollback \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --from-change-id chg_20260223_143022 \
  --out ./rollback
```

## Common Configuration Examples

### Configure SNMP

```json
{
  "changes": [
    {
      "type": "snmp_community",
      "community_string": "public123",
      "access": "ro"
    },
    {
      "type": "snmp_host",
      "host_ip": "192.168.1.100",
      "version": "2c",
      "community_string": "public123",
      "inform": true
    }
  ]
}
```

### Configure Syslog Levels

```json
{
  "changes": [
    {
      "type": "syslog_level",
      "level": "warn",
      "categories": [
        "ap-debug",
        "network",
        "security",
        "system",
        "user",
        "user-debug",
        "wireless"
      ]
    }
  ]
}
```

### Configure SSID with WPA2-PSK

```json
{
  "changes": [
    {
      "type": "ssid_profile",
      "profile_name": "CorporateWiFi",
      "essid": "Corporate",
      "opmode": "wpa2-psk-aes",
      "wpa_passphrase": "SecurePassword123!",
      "vlan": 100,
      "rf_band": "all"
    }
  ]
}
```

### Configure RADIUS Authentication

```json
{
  "changes": [
    {
      "type": "auth_server",
      "server_name": "radius-primary",
      "ip": "10.10.10.10",
      "port": 1812,
      "acct_port": 1813,
      "secret_ref": "secret:radius-primary-key",
      "nas_id_type": "mac"
    }
  ]
}
```

### Add AP to Allowlist

```json
{
  "changes": [
    {
      "type": "ap_allowlist",
      "action": "add",
      "mac_address": "00:11:22:33:44:55"
    }
  ]
}
```

### Configure Wired Port Profile

```json
{
  "changes": [
    {
      "type": "wired_port_profile",
      "profile_name": "wired-SetMeUp",
      "switchport_mode": "access",
      "native_vlan": 10,
      "access_rule_name": "wired-SetMeUp",
      "shutdown": false
    }
  ]
}
```

## Using Secret References

For production use, avoid plain-text passwords. Use secret references instead:

### 1. Create a Secrets File

Create `secrets.json`:

```json
{
  "radius-primary-key": "MySuperSecretRADIUSKey123!",
  "wpa-psk-key": "WPA2SecurePassword!"
}
```

### 2. Reference Secrets in Changes

```json
{
  "changes": [
    {
      "type": "auth_server",
      "server_name": "radius-primary",
      "ip": "10.10.10.10",
      "secret_ref": "secret:radius-primary-key",
      "nas_id_type": "mac"
    },
    {
      "type": "ssid_profile",
      "profile_name": "CorporateWiFi",
      "essid": "Corporate",
      "opmode": "wpa2-psk-aes",
      "wpa_passphrase_ref": "secret:wpa-psk-key",
      "vlan": 100,
      "rf_band": "all"
    }
  ]
}
```

### 3. Load Secrets Before Apply

```bash
export SECRETS_FILE="/path/to/secrets.json"
```

Or using environment variables:

```bash
export RADIUS_PRIMARY_KEY="MySuperSecretRADIUSKey123!"
export WPA_PSK_KEY="WPA2SecurePassword!"
```

Then reference with `env:` prefix:

```json
{
  "secret_ref": "env:RADIUS_PRIMARY_KEY"
}
```

## Understanding the Output

### Commands File

`diff/commands.txt` shows human-readable commands:

```
# Change ID: chg_20260223_143022
# Commands to apply:
snmp-server community public123 ro
snmp-server host 192.168.1.100 version 2c public123 inform
wlan ssid-profile Aruba-IAP
  essid MyWiFi
  opmode wpa2-psk-aes
  vlan 100
  rf-band all
  wpa-passphrase ***REDACTED***
  exit

# Rollback commands:
no snmp-server community public123
no snmp-server host 192.168.1.100
no wlan ssid-profile Aruba-IAP
```

### Risk Assessment

`diff/risk.json` shows risk level and warnings:

```json
{
  "level": "medium",
  "warnings": [
    "WPA passphrase changes will require clients to re-authenticate"
  ],
  "concerns": [
    "SSID changes may affect wireless client connectivity"
  ]
}
```

### Apply Result

`apply/result.json` shows operation summary:

```json
{
  "ok": true,
  "action": "apply",
  "cluster": "office-iap",
  "vc": "192.168.20.56",
  "checks": [
    {
      "name": "apply_success",
      "status": "pass",
      "message": "Successfully applied 7 commands"
    }
  ],
  "artifacts": [
    {
      "name": "pre_running-config.txt",
      "path": "./apply/pre_running-config.txt"
    },
    {
      "name": "post_running-config.txt",
      "path": "./apply/post_running-config.txt"
    }
  ]
}
```

## Best Practices

1. **Always review risk assessment** before applying changes
2. **Use dry-run mode** for testing: `--dry-run`
3. **Use secret references** instead of plain-text passwords
4. **Apply changes in stages** for large change sets
5. **Always verify** after applying: `iapctl verify --level full`
6. **Archive change sets** for audit and rollback
7. **Test in lab** before applying to production

## Troubleshooting

### Command Failed

Check step-by-step output:
```bash
cat apply/apply_step_003.txt
```

### Rollback Needed

Rollback to previous configuration:
```bash
iapctl rollback --from-change-id <change-id>
```

### Secret Not Found

Check secrets file or environment variables:
```bash
echo $RADIUS_PRIMARY_KEY
cat secrets.json
```

### Risk Level Too High

Break changes into smaller batches and review each separately.

## Next Steps

- Read [docs/CONFIG-CHANGES.md](CONFIG-CHANGES.md) for complete documentation
- Review [examples/config-changes.json](../examples/config-changes.json) for more examples
- Check [examples/secrets.json](../examples/secrets.json) for secret management examples

---

**Version:** v0.4.0
**Last Updated:** 2026-02-23
