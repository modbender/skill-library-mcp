# DevOps Monitor Memory

## Infrastructure Overview

### Servers
| Name | IP | Role | Status |
|------|-----|------|--------|
| web-01 | 10.0.1.1 | Web Server | Active |
| api-01 | 10.0.1.2 | API Server | Active |
| db-01 | 10.0.1.3 | Database | Active |

### Services
| Service | Port | Health Check |
|---------|------|--------------|
| nginx | 80 | /health |
| api | 3000 | /healthz |
| postgres | 5432 | pg_isready |

## Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| CPU | >70% | >90% |
| Memory | >75% | >90% |
| Disk | >80% | >95% |
| Response Time | >500ms | >2000ms |

## Runbooks

### Common Issues
- **High CPU:** Check for runaway processes, scale if needed
- **Memory Leak:** Restart service, investigate root cause
- **Disk Full:** Clean logs, rotate files, add storage
- **Deployment Fails:** Check CI/CD logs, verify configs

## Known Issues

| Issue | Status | Workaround |
|-------|--------|------------|
| Memory leak in v2.3 | Open | Scheduled restart |
| API timeout under load | Monitoring | Auto-scale |

## Deployment History

| Version | Date | Status | Notes |
|---------|------|--------|-------|
| v2.1.0 | 2024-01-15 | ✅ | Stable |
| v2.2.0 | 2024-02-01 | ✅ | New features |
