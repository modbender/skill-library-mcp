# Diagnostic Commands

Quick reference for all OpenClaw CLI diagnostic and troubleshooting commands.

## System Health

| Command | Description | Example Output |
|---------|-------------|----------------|
| `openclaw doctor` | Run comprehensive health check | Overall status + issues found |
| `openclaw doctor --full` | Extended diagnostics with all checks | Detailed component status |
| `openclaw doctor --check-auth` | Verify API authentication | Auth status per provider |
| `openclaw doctor --check-env` | Check environment variables | Missing/invalid env vars |
| `openclaw status` | Show gateway and service status | Running/stopped + uptime |
| `openclaw status --watch` | Monitor status continuously | Real-time status updates |
| `openclaw status --detailed` | Detailed status with metrics | CPU/memory/connections |

## Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw config show` | Display current configuration | Full config YAML |
| `openclaw config get <key>` | Get specific config value | `openclaw config get gateway.port` |
| `openclaw config set <key> <value>` | Set config value | `openclaw config set gateway.port 18790` |
| `openclaw config validate` | Validate configuration | Schema validation result |
| `openclaw config validate --show-missing` | List missing required fields | Required fields not set |
| `openclaw config schema` | Show config schema | Full schema with types |
| `openclaw config edit` | Open config in editor | Opens $EDITOR |
| `openclaw config reset` | Reset to defaults | Backup + restore defaults |
| `openclaw config migrate` | Migrate deprecated keys | Update to new format |

## Gateway Management

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw start` | Start gateway | Daemon mode |
| `openclaw start --foreground` | Start in foreground | Verbose output |
| `openclaw stop` | Stop gateway | Graceful shutdown |
| `openclaw restart` | Restart gateway | Stop + start |
| `openclaw status` | Check if running | PID + port + uptime |
| `openclaw logs` | View gateway logs | Recent log entries |
| `openclaw logs --follow` | Stream logs live | Continuous output |
| `openclaw logs --level error` | Filter by log level | Errors only |
| `openclaw logs --last 30m` | Logs from time period | Last 30 minutes |

## Channel Management

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw channels list` | List all channels | Status + config |
| `openclaw channels status` | Show channel status | Connected/disconnected |
| `openclaw channels status --all` | Status of all channels | All channels overview |
| `openclaw channels enable <name>` | Enable channel | `openclaw channels enable whatsapp` |
| `openclaw channels disable <name>` | Disable channel | `openclaw channels disable telegram` |
| `openclaw channels restart <name>` | Restart channel | Reconnect channel |
| `openclaw channels test <name>` | Test channel connection | Connection test result |

### WhatsApp Commands

| Command | Description |
|---------|-------------|
| `openclaw whatsapp link` | Link WhatsApp account |
| `openclaw whatsapp qr-code` | Show QR code for linking |
| `openclaw whatsapp logout` | Unlink WhatsApp |
| `openclaw whatsapp session-info` | Show session details |
| `openclaw whatsapp test-connection` | Test WhatsApp connection |

### Telegram Commands

| Command | Description |
|---------|-------------|
| `openclaw telegram set-webhook` | Configure webhook |
| `openclaw telegram delete-webhook` | Remove webhook |
| `openclaw telegram webhook-info` | Show webhook status |

### Discord Commands

| Command | Description |
|---------|-------------|
| `openclaw discord generate-invite` | Generate bot invite URL |
| `openclaw discord check-permissions` | Verify bot permissions |
| `openclaw discord bot-info` | Show bot details |

### Slack Commands

| Command | Description |
|---------|-------------|
| `openclaw slack verify-signing-secret` | Test signing secret |
| `openclaw slack refresh-token` | Refresh OAuth token |
| `openclaw slack reinstall` | Reinstall app |

## AI Provider Management

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw providers list` | List configured providers | All providers + status |
| `openclaw providers test <name>` | Test provider connection | `openclaw providers test openai` |
| `openclaw providers status` | Show provider health | Connected/rate limits |
| `openclaw quota show` | Display API quota usage | Usage per provider |
| `openclaw quota status` | Check quota limits | Remaining quota |

## Sandbox Management

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw sandbox stats` | Show sandbox metrics | CPU/memory/disk usage |
| `openclaw sandbox exec <cmd>` | Execute in sandbox | `openclaw sandbox exec -- python script.py` |
| `openclaw sandbox history` | Show execution history | Recent executions |
| `openclaw sandbox restart` | Restart sandbox container | Stop + start |

## Skill Management (ClawHub)

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw skills list` | List installed skills | Installed skills |
| `openclaw skills search <query>` | Search ClawHub | `openclaw skills search "image"` |
| `openclaw skills install <name>` | Install skill | `openclaw skills install image-gen` |
| `openclaw skills uninstall <name>` | Remove skill | `openclaw skills uninstall skill-name` |
| `openclaw skills update` | Update all skills | Check + update |
| `openclaw skills sync` | Sync with ClawHub | Refresh catalog |
| `openclaw skills check` | Verify skills | Validation status |

## Plugin Management

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw plugins list` | List installed plugins | All plugins |
| `openclaw plugins doctor` | Check plugin health | Validation + errors |
| `openclaw plugins reload <name>` | Reload plugin | Hot reload |

## Logging and Debugging

| Command | Description | Filters |
|---------|-------------|---------|
| `openclaw logs` | View all logs | Default: last 100 lines |
| `openclaw logs --follow` | Stream logs | Live updates |
| `openclaw logs --level <level>` | Filter by level | debug/info/warn/error |
| `openclaw logs --channel <name>` | Channel-specific logs | `--channel whatsapp` |
| `openclaw logs --filter <text>` | Text search | `--filter "401"` |
| `openclaw logs --last <time>` | Time period | `--last 1h`, `--last 30m` |
| `openclaw logs --json` | JSON output | Machine-readable |
| `openclaw logs --auth-only` | Auth logs only | Authentication events |
| `openclaw logs --sandbox-only` | Sandbox logs only | Execution logs |

## Performance Monitoring

| Command | Description | Output |
|---------|-------------|--------|
| `openclaw status --metrics` | Show performance metrics | CPU/mem/requests |
| `openclaw benchmark --provider <name>` | Test provider latency | Response times |
| `openclaw analytics --metric <name>` | View analytics | Usage statistics |
| `openclaw requests --status <status>` | List active requests | Pending/running/failed |

## Network Diagnostics

| Command | Description | Use Case |
|---------|-------------|----------|
| `openclaw status --provider-health` | Check provider connectivity | Network issues |
| `openclaw connections --active` | Show active connections | Connection debugging |
| `openclaw connections reset` | Reset all connections | Fix stuck connections |

## Cache Management

| Command | Description | Use Case |
|---------|-------------|----------|
| `openclaw cache clear` | Clear all caches | Fix stale data |
| `openclaw cache clear --auth` | Clear auth cache | Auth issues |
| `openclaw cache status` | Show cache stats | Cache size/hits |

## Backup and Restore

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw config backup` | Backup configuration | Creates timestamped backup |
| `openclaw config restore` | Restore from backup | Latest backup |
| `openclaw config export --output <file>` | Export config | `--output backup.yaml` |
| `openclaw config import --input <file>` | Import config | `--input backup.yaml` |

## Alerts and Notifications

| Command | Description | Example |
|---------|-------------|---------|
| `openclaw alerts list` | List configured alerts | All alerts |
| `openclaw alerts add --metric <metric>` | Create alert | `--metric quota --threshold 80` |
| `openclaw alerts remove <id>` | Delete alert | Alert ID |

## Version and Updates

| Command | Description | Output |
|---------|-------------|--------|
| `openclaw --version` | Show version | Current version |
| `openclaw version --check-updates` | Check for updates | Latest version available |
| `openclaw changelog` | View changelog | Recent changes |

## Diagnostic Workflow Examples

### Gateway Won't Start
```bash
# 1. Check what's running
openclaw status

# 2. Check port availability
lsof -i :18789

# 3. Review logs for errors
openclaw logs --level error --last 5m

# 4. Validate configuration
openclaw config validate

# 5. Run health check
openclaw doctor --full
```

### Authentication Issues
```bash
# 1. Check auth configuration
openclaw doctor --check-auth

# 2. Verify environment variables
openclaw doctor --check-env

# 3. Test provider connection
openclaw providers test openai

# 4. View auth-related logs
openclaw logs --auth-only --last 1h
```

### Channel Not Working
```bash
# 1. Check channel status
openclaw channels status whatsapp

# 2. Test channel connection
openclaw channels test whatsapp

# 3. View channel logs
openclaw logs --channel whatsapp --last 30m

# 4. Check permissions (Discord)
openclaw discord check-permissions

# 5. Restart channel
openclaw channels restart whatsapp
```

### Performance Issues
```bash
# 1. Check metrics
openclaw status --metrics

# 2. View active requests
openclaw requests --status pending

# 3. Check sandbox stats
openclaw sandbox stats

# 4. Benchmark providers
openclaw benchmark --provider openai --samples 10

# 5. Review rate limits
openclaw status --rate-limits
```

### Quota/Rate Limit Issues
```bash
# 1. Check quota status
openclaw quota show

# 2. View rate limit events
openclaw logs --filter "429" --last 24h

# 3. Check provider status
openclaw providers status

# 4. View usage analytics
openclaw analytics --metric quota --last 7d
```

## Quick Troubleshooting Commands

```bash
# All-in-one health check
openclaw doctor --full

# System overview
openclaw status --detailed

# Recent errors
openclaw logs --level error --last 1h

# Validate everything
openclaw config validate && \
openclaw channels status --all && \
openclaw providers status

# Full diagnostic report
openclaw doctor --full > diagnostic-report.txt
openclaw status --detailed >> diagnostic-report.txt
openclaw logs --last 1h >> diagnostic-report.txt
```

## Output Formats

Most commands support output formatting:

```bash
# JSON output
openclaw status --json

# YAML output
openclaw config show --format yaml

# Table output
openclaw channels list --format table

# Minimal output
openclaw status --quiet
```

## Related Files

- [Error Catalog](error-catalog.md) - All error types
- [Troubleshooting Workflow](troubleshooting-workflow.md) - Decision trees
- [Auto-Fix Capabilities](auto-fix-capabilities.md) - Automated fixes
