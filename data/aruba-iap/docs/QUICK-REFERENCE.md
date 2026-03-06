# iapctl Quick Reference Card

## Commands

| Command | Purpose | Risk |
|----------|---------|------|
| `discover-cmd` | Basic cluster info | None |
| `monitor-cmd` | Comprehensive monitoring | None |
| `snapshot-cmd` | Full configuration snapshot | None |
| `diff-cmd` | Generate changes | None |
| `apply-cmd` | Apply configuration | Medium |
| `verify-cmd` | Verify configuration | None |
| `rollback-cmd` | Rollback changes | High |

## Monitor Categories

```bash
# All categories (default)
iapctl monitor-cmd --cluster office-iap --vc 192.168.20.56

# Selective monitoring
iapctl monitor-cmd --cluster office-iap --vc 192.168.20.56 \
  --categories system ap clients wlan
```

**Categories:**
- `system` - System info (version, summary, clock)
- `ap` - AP info (active, database, allowlist)
- `clients` - Client info (list, details, user-table)
- `wlan` - WLAN info (SSID profiles, auth servers)
- `rf` - RF info (radio stats)
- `arm` - ARM info (band-steering, history)
- `advanced` - Advanced (client-match, DPI, IDS, Clarity)
- `wired` - Wired (ports, interfaces, routes)
- `logging` - Logging (syslog-level, logs)
- `security` - Security (blacklist, auth-tracebuf, SNMP)

## Configuration Change Types

### SNMP
```json
{"type": "snmp_community", "community_string": "public123", "access": "ro"}
{"type": "snmp_host", "host_ip": "192.168.1.100", "version": "2c", "community_string": "public123"}
```

### Syslog
```json
{"type": "syslog_level", "level": "warn", "categories": ["ap-debug", "network", "security"]}
```

### SSID
```json
{"type": "ssid_profile", "profile_name": "Aruba-IAP", "essid": "MyWiFi",
  "opmode": "wpa2-psk-aes", "wpa_passphrase": "password123", "vlan": 100, "rf_band": "all"}
```

### RADIUS
```json
{"type": "auth_server", "server_name": "cppm", "ip": "10.10.10.50",
  "secret_ref": "secret:cppm-key", "nas_id_type": "mac"}
```

### AP Allowlist
```json
{"type": "ap_allowlist", "action": "add", "mac_address": "00:11:22:33:44:55"}
```

### Wired Port
```json
{"type": "wired_port_profile", "profile_name": "wired-SetMeUp",
  "switchport_mode": "access", "native_vlan": 10}
```

## Utility Scripts

```bash
# Quick health check
./scripts/quick-monitor.sh office-iap 192.168.20.56

# Safe configuration change
./scripts/safe-apply.sh office-iap 192.168.20.56 ./changes.json

# Automatic backup
./scripts/auto-backup.sh office-iap 192.168.20.56
```

## Secret Management

```json
// Use secret references (recommended)
{"type": "auth_server", "secret_ref": "secret:radius-key"}

// Load from file
{
  "radius-key": "MySecretPassword!"
}

// Load from environment
export RADIUS_KEY="MySecretPassword!"
{"type": "auth_server", "secret_ref": "env:RADIUS_KEY"}
```

## Workflow

```bash
# 1. Generate changes
iapctl diff-cmd --cluster office-iap --vc 192.168.20.56 \
  --in ./changes.json --out ./diff

# 2. Review risk
cat ./diff/risk.json

# 3. Apply changes
iapctl apply-cmd --cluster office-iap --vc 192.168.20.56 \
  --change-id chg_$(date +%Y%m%d_%H%M%S) \
  --in ./diff/commands.json --out ./apply

# 4. Verify
iapctl verify-cmd --cluster office-iap --vc 192.168.20.56 \
  --level full --out ./verify

# 5. Rollback (if needed)
iapctl rollback-cmd --cluster office-iap --vc 192.168.20.56 \
  --from-change-id chg_20260223_143022 --out ./rollback
```

## Output Files

```
./out/<timestamp>/
├── result.json              # Structured result
├── raw/                    # Raw CLI outputs
│   ├── show_version.txt
│   ├── show_running-config.txt
│   ├── show_ap_database.txt
│   └── ...
├── commands.json            # Commands to apply
├── commands.txt            # Human-readable commands
├── risk.json               # Risk assessment
├── pre_running-config.txt   # Baseline snapshot
└── post_running-config.txt  # Post-config snapshot
```

## Risk Levels

| Level | Description | Action |
|-------|-------------|---------|
| Low | Minimal impact | Safe to apply |
| Medium | May affect connectivity | Review, confirm |
| High | Major changes | Plan, schedule maintenance |

## Common Errors

| Error | Solution |
|-------|----------|
| `Failed to resolve secret_ref` | Check `secrets.json` or environment variables |
| `Command failed` | Check `apply/apply_step_XXX.txt` for details |
| `Risk level: high` | Break changes into smaller batches |
| `Rollback failed` | Manual intervention, restore from backup |

## Best Practices

✅ Always review `risk.json` before applying
✅ Use `--dry-run` mode for testing
✅ Apply changes in stages (small batches)
✅ Keep change history for audit
✅ Schedule regular backups
✅ Use secret references (no plain-text)
✅ Verify after applying changes

## Device Modes

| Mode | Detection | Commands |
|-------|-----------|-----------|
| Virtual Controller | Multiple APs | `show ap database`, `show wlan` |
| Single-Node Cluster | VC config, 1-2 APs | `show ap bss-table` |
| Standalone AP | No VC config | `show ap info`, `wlan` |

## Quick Commands

```bash
# Quick health check
./scripts/quick-monitor.sh office-iap 192.168.20.56

# Full monitoring
iapctl monitor-cmd --cluster office-iap --vc 192.168.20.56 --out ./monitor

# Snapshot
iapctl snapshot-cmd --cluster office-iap --vc 192.168.20.56 --out ./snapshot

# Backup
./scripts/auto-backup.sh office-iap 192.168.20.56

# Verify
iapctl verify-cmd --cluster office-iap --vc 192.168.20.56 --level full --out ./verify

# Rollback
iapctl rollback-cmd --cluster office-iap --vc 192.168.20.56 \
  --from-change-id chg_20260223_143022 --out ./rollback
```

---

**Version:** v0.5.0 | **Last Updated:** 2026-02-23
