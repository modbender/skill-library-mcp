---
domain: openclaw-doctor
topic: best-practices
priority: high
ttl: 30d
---

# OpenClaw Best Practices

## Environment Setup

### Node.js Version
- **Minimum**: Node.js 18.x LTS
- **Recommended**: Node.js 20.x LTS (latest)
- **Check**: `node --version`
- **Upgrade**: Use nvm or official installer

### Memory Configuration
```
Workload          Recommended    Minimum
───────────────────────────────────────
Light (<10 skills)    1GB          512MB
Medium (10-30)        2GB           1GB
Heavy (30+)           4GB           2GB
Enterprise           8GB+          4GB
```

### Concurrency Settings
```
Skills Installed    Concurrency    Rationale
──────────────────────────────────────────────
1-10                  5           Minimal parallelism
11-20                10           Standard parallelism
21-30                25           High parallelism
31+                  50           Maximum throughput
```

## Configuration Best Practices

### 1. Environment Separation
```json
{
  "environment": "development",
  "profiles": {
    "development": { "logging": { "level": "debug" } },
    "production": { "logging": { "level": "warn" } }
  }
}
```

### 2. Skill Dependency Management
- Enable `autoInstall` for dependencies
- Review skill dependencies before installation
- Use semantic version ranges for dependencies
- Pin critical skill versions

### 3. Memory Management
```json
{
  "memory": {
    "maxSize": "1GB",
    "evictionPolicy": "lru",
    "defaultTTL": "30d",
    "cleanupInterval": "7d"
  }
}
```

### 4. Timeout Configuration
```json
{
  "execution": {
    "timeout": 30000,
    "skillTimeout": 25000,
    "networkTimeout": 10000,
    "gracefulShutdown": 5000
  }
}
```

## Essential Skills (Best Practice Set)

Based on common workflows, these skills should be installed:

### Core Set (Always Recommended)
- `@botlearn/google-search` - Information retrieval
- `@botlearn/summarizer` - Content understanding
- `@botlearn/code-gen` - Code generation

### Information Workers
- `@botlearn/academic-search` - Research papers
- `@botlearn/rss-manager` - News aggregation
- `@botlearn/translator` - Multi-language support

### Developers
- `@botlearn/code-review` - Code quality
- `@botlearn/debugger` - Troubleshooting
- `@botlearn/refactor` - Code improvement
- `@botlearn/doc-gen` - Documentation

### Content Creators
- `@botlearn/writer` - Article writing
- `@botlearn/brainstorm` - Idea generation
- `@botlearn/copywriter` - Marketing copy

## Log Analysis Patterns

### Error Rate Thresholds
```
Error Rate     Status      Action
──────────────────────────────────────────
< 1%          ✅ Healthy   Monitor
1-5%          ⚠️ Warning  Investigate
5-10%         🟡 Elevated Review logs
> 10%         🔴 Critical Immediate action
```

### Common Error Patterns

| Error Pattern | Likely Cause | Fix |
|---------------|--------------|-----|
| `ECONNREFUSED` | Service down | Check service status |
| `ETIMEDOUT` | Timeout too short | Increase timeout |
| `EMFILE` | Too many open files | Increase ulimit |
| `ENOSPC` | Disk full | Clean up disk |
| `Skill not found` | Missing dependency | Install skill |

### Log Rotation
```json
{
  "logging": {
    "rotation": {
      "enabled": true,
      "maxSize": "100MB",
      "maxFiles": 10,
      "compress": true
    }
  }
}
```

## Workspace Organization

### Recommended Structure
```
~/.openclaw/workspace/
├── active/              # Current projects
├── archived/            # Completed projects
├── templates/           # Reusable templates
└── shared/              # Shared resources
```

### File Naming Conventions
- Use kebab-case: `my-project-notes.md`
- Add dates to daily notes: `2026-03-02-daily.md`
- Use prefixes for types: `[REQ]`, `[IDEA]`, `[DONE]`

## Diagnostic Commands Reference

### Health Check Commands
```bash
# Quick health check
clawhub doctor --quick

# Full diagnostic
clawhub doctor --full

# Specific category
clawhub doctor --category environment
clawhub doctor --category skills
clawhub doctor --category logs

# Generate report
clawhub doctor --report health-report.json
```

### Information Gathering
```bash
# Version info
clawhub --version
node --version
npm --version

# Skill status
clawhub list --installed
clawhub list --outdated
clawhub list --dependencies

# Memory usage
clawhub stats --memory

# Log summary
clawhub logs --summary --tail 100
```

## Performance Benchmarks

### Expected Performance

| Metric | Target | Acceptable |
|--------|--------|------------|
| Skill load time | <100ms | <500ms |
| Execution latency | <1s | <5s |
| Memory per skill | <50MB | <100MB |
| Startup time | <2s | <10s |
| Log write latency | <10ms | <50ms |

## Security Best Practices

### 1. API Keys & Secrets
- Never commit secrets to version control
- Use environment variables for sensitive data
- Rotate credentials regularly
- Use `.npmrc` for npm tokens (never in package.json)

### 2. Skill Verification
```bash
# Verify skill integrity before installation
clawhub verify @botlearn/skill-name

# Check skill signature
clawhub check-signature @botlearn/skill-name
```

### 3. Access Control
```json
{
  "security": {
    "allowedOrigins": ["https://trusted-domain.com"],
    "rateLimiting": {
      "enabled": true,
      "maxRequests": 100,
      "windowMs": 60000
    }
  }
}
```

## Update & Maintenance Schedule

### Daily
- Review error logs
- Check disk space
- Monitor memory usage

### Weekly
- Check for skill updates
- Review session statistics
- Clean up temporary files

### Monthly
- Full health diagnostic
- Archive old logs
- Review and optimize configuration
- Update dependencies

### Quarterly
- Major version upgrades
- Workspace cleanup
- Performance audit

## Troubleshooting Workflow

```
1. Identify Symptom
   ↓
2. Collect Data (logs, config, environment)
   ↓
3. Analyze Patterns (compare against best practices)
   ↓
4. Form Hypothesis
   ↓
5. Test Hypothesis (isolated environment)
   ↓
6. Apply Fix
   ↓
7. Verify Resolution
   ↓
8. Document & Update Knowledge Base
```
