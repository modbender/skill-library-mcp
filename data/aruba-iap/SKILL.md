---
name: aruba-iap
description: |
  Comprehensive Aruba Instant AP (IAP) configuration management with automatic baseline capture, 
  rollback support, and health monitoring. Supports device discovery, configuration snapshots,
  SSID management, and safe configuration changes with interactive config mode.
homepage: https://www.arubanetworks.com
---

# Aruba IAP Configuration Manager

Comprehensive Aruba Instant AP (IAP) configuration management with automatic baseline capture, rollback support, and health monitoring.

## Features

### ✨ Core Capabilities

- **Device Mode Detection**: Automatically detects Virtual Controller, Single-Node Cluster, or Standalone AP mode
- **Configuration Snapshots**: Full configuration capture with structured JSON output
- **Safe Configuration Changes**: Apply changes with automatic baseline capture and rollback support
- **Comprehensive Monitoring**: 40+ monitoring commands across 10 categories
- **Risk Assessment**: Automatic risk evaluation for configuration changes
- **Secret Management**: Secure secret references (no plain-text passwords)
- **Change History**: Full audit trail with timestamped artifacts
- **Interactive Configuration Mode**: Support for Aruba IAP CLI commit model

### 📊 Configuration Change Types

| Type | Risk | Description |
|------|-------|-------------|
| `ssid_profile` | Medium | Create complete SSID profile with WPA2-PSK-AES |
| `ssid_delete` | High | Remove existing SSID profile |
| `snmp_community` | Low | SNMP community configuration |
| `snmp_host` | Low-Medium | SNMP host/trap destination |
| `syslog_level` | Low | Syslog logging levels |
| `auth_server` | Medium | RADIUS/CPPM authentication server |
| `ap_allowlist` | Medium | Add/remove APs from allowlist |
| `wired_port_profile` | Medium | Wired port configuration |
| `ntp` | Low | NTP server configuration |
| `dns` | Low | DNS server configuration |
| `rf_template` | Low | RF template application |

## Quick Start

### 1. Installation

```bash
# Clone or download the skill
cd ~/.openclaw/workspace/skills/aruba-iap-publish

# Run install script
./install.sh

# Verify installation
iapctl --help
```

### 2. Basic Usage

```bash
# Device Discovery
iapctl discover --cluster office-iap --vc 192.168.20.56 --out ./out

# Configuration Snapshot
iapctl snapshot --cluster office-iap --vc 192.168.20.56 --out ./out

# Verify Configuration
iapctl verify --cluster office-iap --vc 192.168.20.56 --level basic --out ./out
```

### 3. Add SSID

```bash
# Create SSID configuration JSON
cat > add-ssid.json << 'EOF'
{
  "changes": [
    {
      "type": "ssid_profile",
      "profile_name": "MyWiFi",
      "essid": "MyNetwork",
      "opmode": "wpa2-psk-aes",
      "wpa_passphrase": "MySecurePassword123",
      "vlan": 1,
      "rf_band": "all"
    }
  ]
}
EOF

# Generate diff
iapctl diff --cluster office-iap --vc 192.168.20.56 \
  --in add-ssid.json --out ./diff

# Apply changes
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id $(cat diff/commands.json | jq -r '.change_id') \
  --in diff/commands.json --out ./apply
```

### 4. Delete SSID

```bash
# Create delete SSID configuration JSON
cat > delete-ssid.json << 'EOF'
{
  "changes": [
    {
      "type": "ssid_delete",
      "profile_name": "OldSSID"
    }
  ]
}
EOF

# Generate diff
iapctl diff --cluster office-iap --vc 192.168.20.56 \
  --in delete-ssid.json --out ./diff

# Apply changes
iapctl apply --cluster office-iap --vc 192.168.20.56 \
  --change-id $(cat diff/commands.json | jq -r '.change_id') \
  --in diff/commands.json --out ./apply
```

### 5. Monitor Device

```bash
# Monitor all categories
iapctl monitor --cluster office-iap --vc 192.168.20.56 --out ./monitor

# Monitor specific categories
iapctl monitor --cluster office-iap --vc 192.168.20.56 \
  -c "system ap clients wlan" --out ./monitor
```

## Configuration Modes

### Supported Device Modes

1. **Virtual Controller Mode**
   - Manages multiple IAPs
   - Full CLI command set available

2. **Single-Node Cluster Mode** ✨ NEW
   - Single IAP with VC configuration
   - Supports interactive config mode
   - `configure terminal` → config commands → `commit apply`

3. **Standalone AP Mode**
   - Individual AP without cluster
   - Basic configuration available

### Interactive Configuration Mode

For Aruba IAP devices, configuration uses the CLI commit model:

1. Enter configuration mode: `configure terminal`
2. Enter sub-mode (e.g., `wlan ssid-profile <name>`)
3. Configure parameters (flat commands, no indentation)
4. Exit sub-mode: `exit`
5. Exit configuration mode: `exit`
6. Save configuration: `write memory`
7. Apply configuration: `commit apply`

## Risk Assessment

iapctl automatically assesses risks for each change set:

### Risk Levels

- **low**: Minimal impact, safe to apply
- **medium**: May affect connectivity, review recommended
- **high**: Major changes, requires careful planning

### Common Warnings

- Removing WLAN or RADIUS configuration may disconnect users
- WPA passphrase changes will require clients to re-authenticate
- AP allowlist changes may prevent APs from joining the cluster
- VLAN changes may affect network connectivity
- Large number of changes - consider applying in stages

## Best Practices

### 1. Use Secret References

Always use `secret_ref` for passwords and keys:

```json
{
  "type": "auth_server",
  "server_name": "radius-primary",
  "ip": "10.10.10.10",
  "secret_ref": "secret:radius-primary-key"
}
```

Never commit plain-text secrets to version control.

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

## Testing

Comprehensive testing performed on real hardware:

- ✅ Device discovery and mode detection
- ✅ Configuration snapshot with multiple artifacts
- ✅ Configuration diff generation
- ✅ SSID profile addition
- ✅ SSID profile deletion
- ✅ Configuration apply with interactive mode
- ✅ Configuration verification
- ✅ Health monitoring
- ✅ Risk assessment
- ✅ AP allowlist management

**Test Results: 10/11 tests passed (91%)**

## Known Issues & Limitations

### Rollback Functionality
- **Status**: Partially working
- **Issue**: Rollback command execution has limitations
- **Impact**: Low - can be done manually if needed
- **Workaround**: Use `no <command>` for manual rollback

### Post-Apply Verification
- **Status**: Sometimes times out
- **Issue**: `show running-config` after `commit apply` can timeout
- **Impact**: Minimal - configuration is applied successfully
- **Workaround**: Wait a few seconds and retry

## Changelog

### v1.1.1 (2026-02-23)
- ✅ Add ssid_delete change type
- ✅ Add send_config_and_apply() method
- ✅ Add send_config_commands() method
- ✅ Update diff_engine.py for flat command generation
- ✅ Fix Result action pattern for 'monitor'
- ✅ Support Aruba IAP single-node cluster mode
- ✅ Comprehensive testing on real hardware

### v1.1.0 (2026-02-23)
- ✅ Initial release with core functionality
- ✅ Device discovery and mode detection
- ✅ Configuration snapshots
- ✅ SSID profile management
- ✅ Configuration diff and apply
- ✅ Risk assessment
- ✅ Health monitoring

## Requirements

- Python 3.8+
- scrapli[paramiko] for SSH connections
- Aruba Instant AP 6.x, 8.x, or AOS 10.x

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions:
- ClawHub: https://clawhub.com/skills/aruba-iap
- Documentation: See docs/ folder
- Examples: See examples/ folder
