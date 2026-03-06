# Operational Command Board - Extension Proposal

## Current State

**openclaw-ops-elvatis** currently provides:
- `/cron` - Cron dashboard (jobs, scripts, reports)
- `/privacy-scan` - GitHub privacy scanning
- `/limits` - Provider auth expiry + cooldown windows
- `/release` - Staging gateway QA checklist
- `/staging-smoke` - Full staging smoke testing
- `/handoff` - Latest handoff log tail

## Proposed Extensions for Comprehensive Ops Dashboard

### 1. System Health & Monitoring

#### `/health`
**Purpose:** Quick system health overview
- Gateway status (default + staging profiles)
- Active plugins count
- System resource usage (CPU, memory, disk)
- Last error timestamp
- Response time check

#### `/resources`
**Purpose:** Detailed resource monitoring
- Memory usage per profile/process
- Disk space warnings
- CPU load (1m, 5m, 15m averages)
- Top resource-consuming plugins
- Network connection status

#### `/logs [service] [tail]`
**Purpose:** Unified log viewer
- Gateway logs (streaming option)
- Plugin logs (by name)
- System logs (journalctl integration)
- Error-only filter
- Time-range filtering

### 2. Service Management

#### `/services`
**Purpose:** Comprehensive service status
- All OpenClaw profiles (default, staging, custom)
- Gateway state per profile
- Systemd service status (if applicable)
- Port bindings & conflicts
- Auto-restart status

#### `/restart [service]`
**Purpose:** Controlled service restart
- Gateway restart (default or specified profile)
- Individual plugin reload
- Full stack restart with health check
- Graceful vs. force restart options
- Pre/post restart validations

#### `/profiles`
**Purpose:** Profile management dashboard
- List all profiles
- Active vs. inactive
- Config drift detection
- Last used timestamp
- Quick switch mechanism

### 3. Plugin Management

#### `/plugins`
**Purpose:** Enhanced plugin dashboard
- All installed plugins (across profiles)
- Version info + update available
- Dependencies & conflicts
- Load/execution time stats
- Usage frequency metrics
- Enable/disable state

#### `/plugin-health [name]`
**Purpose:** Individual plugin diagnostics
- Installation status
- Configuration validation
- Command registration status
- Tool execution stats
- Error rate & recent failures
- Resource consumption

#### `/deps`
**Purpose:** Dependency checker
- Node.js packages audit
- Outdated dependencies
- Security vulnerabilities (npm audit)
- Binary dependencies check
- Version compatibility matrix

### 4. Performance & Metrics

#### `/metrics`
**Purpose:** Performance metrics dashboard
- Command execution times (p50, p95, p99)
- Tool call frequency
- Error rates by plugin
- Gateway throughput
- Memory leak detection indicators
- Cache hit/miss rates

#### `/perf [command]`
**Purpose:** Performance profiling
- Run command with profiling
- Execution time breakdown
- Memory allocation tracking
- I/O operations count
- Bottleneck identification

#### `/benchmark`
**Purpose:** System benchmarking
- Standard workload execution
- Compare current vs. baseline
- Historical performance trends
- Regression detection
- Hardware capability check

### 5. Configuration Management

#### `/config [plugin]`
**Purpose:** Configuration viewer/validator
- Show current config (all or by plugin)
- Validate against schema
- Diff against defaults
- Environment variable resolution
- Secret masking

#### `/config-backup`
**Purpose:** Config backup/restore
- Create timestamped backup
- List available backups
- Restore from backup
- Auto-backup before changes
- Cloud sync status (if configured)

#### `/env`
**Purpose:** Environment overview
- All env vars relevant to OpenClaw
- API keys status (present but masked)
- Path validations
- Workspace location
- Node version & platform info

### 6. Security & Privacy

#### `/security-scan`
**Purpose:** Comprehensive security check
- Run multiple security scans
- Check permissions on sensitive files
- Audit plugin capabilities
- Network exposure check
- Secret leak detection
- Update security status

#### `/audit`
**Purpose:** Operational audit trail
- Recent admin commands
- Config changes timeline
- Plugin install/uninstall history
- Security events
- Access patterns

### 7. Backup & Recovery

#### `/backup`
**Purpose:** Full system backup
- Backup all profiles
- Plugin configurations
- Command history
- Custom scripts
- Workspace state
- Verification & compression

#### `/restore [backup-id]`
**Purpose:** Disaster recovery
- List available backups
- Restore full or partial
- Dry-run mode
- Rollback capability
- Health check after restore

### 8. Alerting & Notifications

#### `/alerts`
**Purpose:** Alert dashboard
- Active alerts
- Historical alert log
- Alert rules configuration
- Notification channels status
- Silence/acknowledge alerts
- Escalation paths

#### `/watch [metric] [threshold]`
**Purpose:** Set up monitoring
- Create threshold alerts
- Watch specific metrics
- Notification preferences
- Auto-recovery triggers
- Condition expressions

### 9. Development & Debugging

#### `/debug [plugin]`
**Purpose:** Interactive debugging
- Enable debug mode
- Live log streaming
- Breakpoint-like pauses
- Variable inspection
- Step-through execution tracking

#### `/test [plugin]`
**Purpose:** Quick testing
- Run plugin test suite
- Integration tests
- E2E tests for workflows
- Coverage report
- Test result history

#### `/validate`
**Purpose:** System validation
- Check all installations
- Verify configurations
- Test connectivity
- Validate permissions
- Schema compliance
- Report inconsistencies

### 10. Workflow & Automation

#### `/workflows`
**Purpose:** Automation dashboard
- List active workflows
- Scheduled tasks (beyond cron)
- Workflow execution history
- Success/failure rates
- Trigger configurations
- Manual trigger capability

#### `/runbook [name]`
**Purpose:** Operational runbooks
- Predefined operational procedures
- Step-by-step guided execution
- Automated runbook execution
- Runbook repository
- Custom runbook definition

## Implementation Priorities

### Phase 1 (Immediate - High Impact)
1. `/health` - Quick health dashboard
2. `/services` - Service status overview
3. `/logs` - Unified log viewer
4. `/plugins` - Enhanced plugin dashboard

### Phase 2 (Short-term - Core Operations)
5. `/metrics` - Performance metrics
6. `/config` - Configuration management
7. `/security-scan` - Extended security checks
8. `/backup` - Backup capability

### Phase 3 (Mid-term - Advanced Features)
9. `/alerts` - Alerting system
10. `/workflows` - Automation framework
11. `/debug` - Debugging tools
12. `/benchmark` - Performance benchmarking

### Phase 4 (Long-term - Enterprise Features)
13. `/watch` - Monitoring setup
14. `/runbook` - Runbook automation
15. `/perf` - Advanced profiling
16. `/audit` - Full audit trail

## Technical Considerations

### Architecture
- Keep commands lightweight and fast (<2s response time)
- Use async operations for long-running tasks
- Provide both summary and detailed views
- Cache expensive operations
- Support multiple output formats (text, JSON, table)

### User Experience
- WhatsApp-friendly output formatting
- Progressive disclosure (summary → details)
- Color coding for status (if terminal supports)
- Consistent command naming convention
- Clear error messages with remediation steps

### Integration Points
- Systemd (for service management)
- Prometheus/Grafana (for metrics export)
- Syslog/Journald (for log aggregation)
- Git (for config versioning)
- Cloud storage (for backups)

### Security
- Auth requirements for destructive operations
- Audit logging for all admin commands
- Config validation before apply
- Rollback capability for all changes
- Secret masking in all outputs

## Configuration Schema Extension

```json
{
  "openclaw-ops-elvatis": {
    "enabled": true,
    "workspacePath": "~/.openclaw/workspace",
    "monitoring": {
      "healthCheckInterval": 60,
      "metricsRetention": "7d",
      "alerting": {
        "enabled": true,
        "channels": ["console", "file"],
        "thresholds": {
          "cpu": 80,
          "memory": 85,
          "disk": 90
        }
      }
    },
    "backup": {
      "enabled": true,
      "autoBackup": true,
      "schedule": "0 2 * * *",
      "retention": 14,
      "location": "~/.openclaw/backups"
    },
    "security": {
      "scanInterval": "1d",
      "requireAuthForDestroy": true,
      "auditLog": true
    }
  }
}
```

## Next Steps

1. Review and prioritize features
2. Implement Phase 1 commands
3. Add integration tests
4. Update README with new commands
5. Create comprehensive examples
6. Add monitoring dashboards
7. Document operational procedures

