# Aruba IAP Skill for OpenClaw

Comprehensive Aruba Instant AP (IAP) configuration management with automatic baseline capture, rollback support, and health monitoring.

## Features

### ✨ Core Capabilities

- **Device Mode Detection**: Automatically detects Virtual Controller, Single-Node Cluster, or Standalone AP mode
- **Configuration Snapshots**: Full configuration capture with structured JSON output
- **Safe Configuration Changes**: Apply changes with automatic baseline capture and rollback
- **Comprehensive Monitoring**: 40+ monitoring commands across 10 categories
- **Risk Assessment**: Automatic risk evaluation for configuration changes
- **Secret Management**: Secure secret references (no plain-text passwords)
- **Change History**: Full audit trail with timestamped artifacts

### 📊 Monitoring Categories

| Category | Commands | Description |
|----------|-----------|-------------|
| **System** | 4 commands | Version, summary, clock, configuration |
| **AP** | 3 commands | Active APs, database, allowlist |
| **Clients** | 4 commands | Clients list, details, user-table, station-table |
| **WLAN** | 4 commands | SSID profiles, access rules, auth servers |
| **RF** | 1 command | Radio statistics |
| **ARM** | 3 commands | ARM, band-steering, ARM history |
| **Advanced** | 5 commands | Client-match, DPI, IDS, Clarity |
| **Wired** | 6 commands | Ports, interfaces, routing |
| **Logging** | 4 commands | Syslog levels, logs |
| **Security** | 3 commands | Blacklist, auth-tracebuf, SNMP |

### 🔧 Configuration Change Types

| Type | Risk | Description |
|------|-------|-------------|
| `snmp_community` | Low | SNMP community configuration |
| `snmp_host` | Low-Medium | SNMP host/trap destination |
| `syslog_level` | Low | Syslog logging levels |
| `ssid_profile` | Medium | Complete SSID profile with WPA2-PSK |
| `auth_server` | Medium | RADIUS/CPPM authentication server |
| `ap_allowlist` | Medium | Add/remove APs from allowlist |
| `wired_port_profile` | Medium | Wired port configuration |
| `ntp` | Low | NTP server configuration |
| `dns` | Low | DNS server configuration |
| `rf_template` | Low | RF template application |

## Quick Start

### 1. Installation

```bash
cd /Users/scsun/.openclaw/workspace/skills/aruba-iap-publish
./install.sh
```

### 2. Quick Health Check

```bash
./scripts/quick-monitor.sh office-iap 192.168.20.56
```

### 3. Apply Configuration Changes

```bash
./scripts/safe-apply.sh office-iap 192.168.20.56 ./changes.json
```

### 4. Automatic Backup

```bash
./scripts/auto-backup.sh office-iap 192.168.20.56
```

## Usage Examples

### Discovery

```bash
iapctl discover-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --out ./discover
```

### Full Monitoring

```bash
iapctl monitor-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --out ./monitor
```

### Selective Monitoring

```bash
iapctl monitor-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --out ./monitor \
  --categories system ap clients wlan
```

### Configuration Snapshot

```bash
iapctl snapshot-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --out ./snapshot
```

### Apply Changes (Manual)

```bash
# Step 1: Generate diff
iapctl diff-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --in ./changes.json \
  --out ./diff

# Step 2: Review risk
cat ./diff/risk.json

# Step 3: Apply changes
iapctl apply-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --change-id chg_20260223_143022 \
  --in ./diff/commands.json \
  --out ./apply

# Step 4: Verify
iapctl verify-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --level full \
  --out ./verify
```

### Rollback

```bash
iapctl rollback-cmd \
  --cluster office-iap \
  --vc 192.168.20.56 \
  --from-change-id chg_20260223_143022 \
  --out ./rollback
```

## Secret Management

### Using Secret References

Avoid plain-text passwords in your changes file:

```json
{
  "changes": [
    {
      "type": "auth_server",
      "server_name": "cppm",
      "ip": "10.10.10.50",
      "secret_ref": "secret:cppm-radius-key",
      "nas_id_type": "mac"
    }
  ]
}
```

### Load Secrets from File

Create `secrets.json`:

```json
{
  "cppm-radius-key": "MySuperSecretRADIUSKey123!",
  "wpa-psk-key": "WPA2SecurePassword!"
}
```

### Load Secrets from Environment

```bash
export CPPM_RADIUS_KEY="MySuperSecretRADIUSKey123!"
```

Reference in changes:

```json
{
  "secret_ref": "env:CPPM_RADIUS_KEY"
}
```

## File Structure

```
skills/aruba-iap-publish/
├── iapctl/                    # Core CLI tool
│   └── src/iapctl/
│       ├── __init__.py
│       ├── cli.py             # CLI interface
│       ├── connection.py      # SSH connection handling
│       ├── diff_engine.py     # Change generation
│       ├── models.py          # Data models
│       ├── monitor.py         # Monitoring commands
│       ├── operations.py      # Core operations
│       └── secrets.py        # Secret management
├── scripts/                  # Utility scripts
│   ├── quick-monitor.sh       # Quick health check
│   ├── safe-apply.sh        # Safe config change workflow
│   └── auto-backup.sh       # Automatic backup
├── examples/                 # Example files
│   ├── config-changes.json   # Configuration examples
│   └── secrets.json         # Secret examples
├── docs/                    # Documentation
│   ├── CONFIG-CHANGES.md     # Configuration guide
│   └── QUICKSTART-CONFIG.md # Quick start guide
└── SKILL.md                 # Skill documentation
```

## Output Artifacts

All iapctl commands generate structured output:

```
./out/<timestamp>/
├── result.json              # Structured result (machine-readable)
├── raw/                    # Raw CLI outputs (human-auditable)
│   ├── show_version.txt
│   ├── show_running-config.txt
│   ├── show_ap_database.txt
│   └── ...
├── commands.json            # Generated commands (for apply)
├── commands.txt            # Human-readable command list
├── risk.json               # Risk assessment
├── pre_running-config.txt   # Baseline (for apply)
└── post_running-config.txt  # Post-config (for apply)
```

## Device Mode Adaptation

iapctl automatically adapts to three device modes:

### Virtual Controller Mode
- Commands: `show ap database`, `show wlan`, `show ap-group`
- Use case: Multi-AP clusters managed by virtual controller

### Single-Node Cluster Mode
- Commands: `show ap bss-table`, `show ap bss-table`
- Use case: Single AP with VC configuration but only one BSS

### Standalone AP Mode
- Commands: `show ap info`, `wlan`
- Use case: Single AP operating independently

All commands automatically fallback to safe alternatives if primary commands fail.

## Risk Assessment

iapctl automatically assesses risks for each change:

### Risk Levels

- **low**: Minimal impact, safe to apply
- **medium**: May affect connectivity, review recommended
- **high**: Major changes, requires careful planning

### Common Warnings

- Removing WLAN or RADIUS configuration may disconnect users
- WPA passphrase changes will require clients to re-authenticate
- AP allowlist changes may prevent APs from joining cluster
- VLAN changes may affect network connectivity
- Large number of changes - consider applying in stages

## Best Practices

### 1. Always Review Risk Assessment

```bash
cat diff/risk.json
```

### 2. Use Dry Run Mode

```bash
iapctl apply-cmd --dry-run ...
```

### 3. Apply Changes in Stages

Break large change sets into smaller batches:
1. SNMP and syslog
2. Authentication servers
3. SSID profiles
4. AP allowlist and wired ports

### 4. Keep Change History

Archive change sets for audit and rollback:

```bash
mkdir -p /archive/changes/chg_20260223_143022
cp -r diff apply verify /archive/changes/chg_20260223_143022/
```

### 5. Schedule Regular Backups

```bash
# Add to crontab for daily backups
0 2 * * * /path/to/scripts/auto-backup.sh office-iap 192.168.20.56
```

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
4. Manual rollback: `iapctl rollback-cmd --from-change-id <change-id>`

### Rollback Failed

**Error:** `Rollback command 2 failed: ...`

**Solution:**
1. Check `rollback/rollback_step_002.txt` for error details
2. Manual intervention may be required
3. Restore from `pre_running-config.txt` backup if needed

### Device Mode Detection Issues

**Incorrect mode detected:**
```bash
# Check detected mode
cat ./out/discover/result.json | jq '.is_vc, .device_mode'

# Review version output
cat ./out/discover/raw/show_version.txt
```

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation
- **[docs/CONFIG-CHANGES.md](docs/CONFIG-CHANGES.md)** - Configuration change guide
- **[docs/QUICKSTART-CONFIG.md](docs/QUICKSTART-CONFIG.md)** - Quick start guide

## Version History

### v0.5.0 (2026-02-23)
- Monitor command with 10 categories and 40+ commands
- Category-based filtering
- Quick monitoring script
- Safe apply script
- Auto backup script

### v0.4.0 (2026-02-23)
- Config-change commands with auto-baseline
- SNMP configuration support
- Syslog configuration support
- Complete SSID profile support
- RADIUS/CPPM auth servers
- AP allowlist management
- Wired port profiles

### v0.3.0 (2026-02-22)
- Single-Node Cluster mode
- Enhanced device mode detection
- Instant AP command support
- Smart command fallback

### v0.2.0 (2026-02-22)
- Device mode detection
- Command adaptation
- Fallback behavior
- Improved standalone AP support

### v0.1.0 (2026-02-22)
- Initial release
- `discover`, `snapshot`, `diff`, `apply`, `verify`, `rollback` commands
- JSON + raw output format
- SSH key and password authentication

## License

This skill is part of OpenClaw and follows the same license.

## Support

For issues and questions:
- Check [SKILL.md](SKILL.md) for detailed documentation
- Review [docs/CONFIG-CHANGES.md](docs/CONFIG-CHANGES.md) for configuration examples
- Use `--verbose` flag for detailed output

---

**Version:** v0.5.0
**Last Updated:** 2026-02-23
**Author:** scsun
