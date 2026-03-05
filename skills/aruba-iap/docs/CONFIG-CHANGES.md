# Aruba IAP Configuration Changes

## Overview

iapctl now supports comprehensive configuration changes with automatic baseline capture and rollback support. All configuration changes follow a safe workflow:

1. **Generate baseline snapshot** - Automatic capture of `show running-config` before changes
2. **Apply changes** - Execute configuration commands
3. **Verify changes** - Post-configuration snapshot
4. **Rollback capability** - Automatic rollback commands for every change

## Supported Configuration Types

### 1. SNMP Configuration

#### SNMP Community

```json
{
  "type": "snmp_community",
  "community_string": "public123",
  "access": "ro"
}
```

**Generated CLI Commands:**
```bash
snmp-server community public123 ro
```

**Rollback Commands:**
```bash
no snmp-server community public123
```

#### SNMP Host

```json
{
  "type": "snmp_host",
  "host_ip": "192.168.1.100",
  "version": "2c",
  "community_string": "public123",
  "inform": true
}
```

**Generated CLI Commands:**
```bash
snmp-server host 192.168.1.100 version 2c public123 inform
```

**Rollback Commands:**
```bash
no snmp-server host 192.168.1.100
```

---

### 2. Syslog Level Configuration

```json
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
```

**Generated CLI Commands:**
```bash
syslog-level warn ap-debug
syslog-level warn network
syslog-level warn security
syslog-level warn system
syslog-level warn user
syslog-level warn user-debug
syslog-level warn wireless
```

**Rollback Commands:**
```bash
syslog-level warn ap-debug
syslog-level warn network
syslog-level warn security
syslog-level warn system
syslog-level warn user
syslog-level warn user-debug
syslog-level warn wireless
```

---

### 3. SSID Profile Configuration

```json
{
  "type": "ssid_profile",
  "profile_name": "Aruba-IAP",
  "essid": "MyWiFi",
  "opmode": "wpa2-psk-aes",
  "wpa_passphrase": "MySecurePassword123",
  "vlan": 100,
  "rf_band": "all"
}
```

**Generated CLI Commands:**
```bash
wlan ssid-profile Aruba-IAP
  essid MyWiFi
  opmode wpa2-psk-aes
  vlan 100
  rf-band all
  wpa-passphrase MySecurePassword123
  exit
```

**Rollback Commands:**
```bash
no wlan ssid-profile Aruba-IAP
```

**Security Note:** For production use, use `secret_ref` instead of plain text password:

```json
{
  "type": "ssid_profile",
  "profile_name": "Aruba-IAP",
  "essid": "MyWiFi",
  "opmode": "wpa2-psk-aes",
  "wpa_passphrase_ref": "secret:my-wifi-psk",
  "vlan": 100,
  "rf_band": "all"
}
```

---

### 4. Authentication Server (RADIUS/CPPM) Configuration

```json
{
  "type": "auth_server",
  "server_name": "cppm",
  "ip": "10.10.10.50",
  "port": 1812,
  "acct_port": 1813,
  "secret_ref": "secret:cppm-radius-key",
  "nas_id_type": "mac"
}
```

**Generated CLI Commands:**
```bash
wlan auth-server cppm
  ip 10.10.10.50
  port 1812
  acctport 1813
  key ***REDACTED***
  nas-id mac
  exit
```

**Rollback Commands:**
```bash
no wlan auth-server cppm
```

---

### 5. AP Allowlist Configuration

#### Add AP to Allowlist

```json
{
  "type": "ap_allowlist",
  "action": "add",
  "mac_address": "00:11:22:33:44:55"
}
```

**Generated CLI Commands:**
```bash
allowed-ap 00:11:22:33:44:55
```

**Rollback Commands:**
```bash
no allowed-ap 00:11:22:33:44:55
```

#### Remove AP from Allowlist

```json
{
  "type": "ap_allowlist",
  "action": "remove",
  "mac_address": "00:11:22:33:44:55"
}
```

**Generated CLI Commands:**
```bash
no allowed-ap 00:11:22:33:44:55
```

**Rollback Commands:**
```bash
allowed-ap 00:11:22:33:44:55
```

---

### 6. Wired Port Profile Configuration

```json
{
  "type": "wired_port_profile",
  "profile_name": "wired-SetMeUp",
  "switchport_mode": "access",
  "native_vlan": 10,
  "access_rule_name": "wired-SetMeUp",
  "shutdown": false
}
```

**Generated CLI Commands:**
```bash
wired-port-profile wired-SetMeUp
  switchport-mode access
  native-vlan 10
  access-rule-name wired-SetMeUp
  no shutdown
  exit
```

**Rollback Commands:**
```bash
no wired-port-profile wired-SetMeUp
```

---

## Secret Management

### Using Secret References

For sensitive values (passwords, keys), use the `secret_ref` pattern instead of plain text:

```json
{
  "type": "auth_server",
  "server_name": "cppm",
  "ip": "10.10.10.50",
  "secret_ref": "secret:cppm-radius-key"
}
```

### Loading Secrets

Create a `secrets.json` file:

```json
{
  "cppm-radius-key": "MySuperSecretRADIUSKey123!",
  "radius-primary-key": "AnotherSecretKey456!",
  "wpa-psk-key": "WPA2SecretPassword!"
}
```

Load secrets before applying changes:

```python
from iapctl.secrets import load_secrets_file

load_secrets_file("/path/to/secrets.json")
```

### Environment Variables

Set secret in environment:

```bash
export RADIUS_SHARED_SECRET="my-secret-value"
```

Reference in changes:

```json
{
  "type": "auth_server",
  "secret_ref": "env:RADIUS_SHARED_SECRET"
}
```

---

## Workflow Example

### Step 1: Prepare Changes File

Create `changes.json`:

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

### Step 2: Load Secrets (if using secret_ref)

```bash
export CPPM_RADIUS_KEY="MySuperSecretRADIUSKey123!"
```

Or create `secrets.json`:

```json
{
  "cppm-radius-key": "MySuperSecretRADIUSKey123!"
}
```

### Step 3: Generate Diff and Commands

```bash
iapctl diff \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --in changes.json \
  --out ./diff
```

**Output:**
- `diff/commands.json` - Commands to apply (with secret redaction)
- `diff/commands.txt` - Human-readable command list
- `diff/risk.json` - Risk assessment
- `diff/raw/show_running-config.txt` - Current config

### Step 4: Review Risk Assessment

```bash
cat diff/risk.json
```

**Example Output:**
```json
{
  "level": "medium",
  "warnings": [
    "WPA passphrase changes will require clients to re-authenticate",
    "AP allowlist changes may prevent APs from joining the cluster"
  ],
  "concerns": [
    "SSID changes may affect wireless client connectivity"
  ]
}
```

### Step 5: Apply Changes (with Dry Run First)

**Dry Run (no changes applied):**
```bash
iapctl apply \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --change-id chg_20260223_143022 \
  --in diff/commands.json \
  --out ./apply \
  --dry-run
```

**Apply Changes:**
```bash
iapctl apply \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --change-id chg_20260223_143022 \
  --in diff/commands.json \
  --out ./apply
```

**Output:**
- `apply/pre_running-config.txt` - **Baseline snapshot** (automatic)
- `apply/apply_step_001.txt` - Step-by-step command outputs
- `apply/post_running-config.txt` - Post-configuration snapshot
- `apply/result.json` - Result summary

### Step 6: Verify Changes

```bash
iapctl verify \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --level full \
  --out ./verify
```

### Step 7: Rollback (if needed)

```bash
iapctl rollback \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --from-change-id chg_20260223_143022 \
  --out ./rollback
```

**Output:**
- `rollback/pre_rollback_running-config.txt` - Pre-rollback snapshot
- `rollback/rollback_step_001.txt` - Step-by-step rollback outputs
- `rollback/post_rollback_running-config.txt` - Post-rollback snapshot
- `rollback/result.json` - Rollback result

---

## Automatic Baseline Capture

iapctl automatically captures baseline configurations for every change:

### Pre-Change Baseline

**File:** `pre_running-config.txt`
**Content:** Full `show running-config` output before any changes
**Purpose:** Exact point-in-time state for rollback reference

### Post-Change Snapshot

**File:** `post_running-config.txt`
**Content:** Full `show running-config` output after changes
**Purpose:** Verification that changes were applied correctly

### Rollback Baseline

**File:** `pre_rollback_running-config.txt` / `post_rollback_running-config.txt`
**Content:** Before/after rollback snapshots
**Purpose:** Track rollback impact

---

## Risk Assessment

iapctl automatically assesses risks for each change set:

### Risk Levels

- **low** - Minimal impact, safe to apply
- **medium** - May affect connectivity, review recommended
- **high** - Major changes, requires careful planning

### Common Warnings

- Removing WLAN or RADIUS configuration may disconnect users
- WPA passphrase changes will require clients to re-authenticate
- AP allowlist changes may prevent APs from joining the cluster
- VLAN changes may affect network connectivity
- Large number of changes - consider applying in stages

### Common Concerns

- VLAN changes may affect network connectivity
- SSID changes may affect wireless client connectivity
- Wired port profile changes may affect wired client connectivity
- AP allowlist changes may prevent APs from joining the cluster

---

## Best Practices

### 1. Use Secret References

Always use `secret_ref` for passwords and keys:

```json
{
  "type": "ssid_profile",
  "wpa_passphrase_ref": "secret:my-wifi-psk"
}
```

**Never commit plain-text secrets to version control.**

### 2. Review Risk Assessment

Always review `risk.json` before applying changes:

```bash
cat diff/risk.json
```

### 3. Use Dry Run First

Test with `--dry-run` to verify commands without applying:

```bash
iapctl apply --dry-run ...
```

### 4. Verify After Changes

Always run `verify` after applying changes:

```bash
iapctl verify --level full ...
```

### 5. Apply Changes in Stages

For large change sets, break them into smaller batches:

- Stage 1: SNMP and syslog configuration
- Stage 2: Authentication servers
- Stage 3: SSID profiles
- Stage 4: AP allowlist and wired ports

### 6. Keep Change History

Archive change sets for audit and rollback:

```bash
# Archive successful change
mkdir -p /archive/changes/chg_20260223_143022
cp -r diff apply verify /archive/changes/chg_20260223_143022/
```

---

## Troubleshooting

### Secret Resolution Failed

**Error:** `Failed to resolve secret_ref: secret:my-key`

**Solution:**
1. Check `secrets.json` exists and contains the key
2. Verify secret reference format: `secret:key-name`
3. Check environment variables if using `env:VAR_NAME`

### Change Failed Partially

**Error:** `Command 3 failed: ...`

**Solution:**
1. Check `apply/apply_step_003.txt` for error details
2. Check `apply/result.json` for errors array
3. Automatic rollback attempts may have occurred
4. Manual rollback: `iapctl rollback --from-change-id <change-id>`

### Rollback Failed

**Error:** `Rollback command 2 failed: ...`

**Solution:**
1. Check `rollback/rollback_step_002.txt` for error details
2. Manual intervention may be required
3. Restore from `pre_running-config.txt` backup if needed

### Risk Level Too High

**Warning:** `Risk level: high - Major changes, requires careful planning`

**Solution:**
1. Review risk assessment in `diff/risk.json`
2. Break changes into smaller batches
3. Schedule maintenance window for high-impact changes
4. Get approval for high-risk changes

---

## Examples

### Example 1: Complete SNMP Configuration

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

### Example 2: SSID with WPA2-PSK

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

### Example 3: RADIUS Authentication

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
    },
    {
      "type": "auth_server",
      "server_name": "radius-secondary",
      "ip": "10.10.10.11",
      "port": 1812,
      "acct_port": 1813,
      "secret_ref": "secret:radius-secondary-key",
      "nas_id_type": "mac"
    }
  ]
}
```

### Example 4: AP Allowlist Management

```json
{
  "changes": [
    {
      "type": "ap_allowlist",
      "action": "add",
      "mac_address": "00:11:22:33:44:55"
    },
    {
      "type": "ap_allowlist",
      "action": "add",
      "mac_address": "00:11:22:33:44:56"
    },
    {
      "type": "ap_allowlist",
      "action": "remove",
      "mac_address": "00:11:22:33:44:57"
    }
  ]
}
```

---

## Reference

### Change Types Summary

| Type | Purpose | Risk Level |
|------|---------|------------|
| `snmp_community` | Configure SNMP community | Low |
| `snmp_host` | Configure SNMP host/trap | Low-Medium |
| `syslog_level` | Set syslog logging levels | Low |
| `ssid_profile` | Configure SSID profile | Medium |
| `auth_server` | Configure RADIUS/CPPM server | Medium |
| `ap_allowlist` | Manage AP allowlist | Medium |
| `wired_port_profile` | Configure wired port profile | Medium |

### Command Structure

All changes follow this pattern:

1. **Enter configuration mode** - `configure terminal`
2. **Apply specific commands** - Change-specific commands
3. **Exit configuration mode** - `exit`
4. **Save configuration** - `write memory`

### Rollback Structure

All rollbacks follow this pattern:

1. **Enter configuration mode** - `configure terminal`
2. **Apply negative commands** - `no <command>` or reverse actions
3. **Exit configuration mode** - `exit`
4. **Save configuration** - `write memory`

---

**Version:** v0.4.0
**Last Updated:** 2026-02-23
**Author:** scsun
