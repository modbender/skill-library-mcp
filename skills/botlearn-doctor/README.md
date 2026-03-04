# @botlearn/openclaw-doctor

> Comprehensive health check and diagnostic system for OpenClaw Agent, including data collection, analysis, troubleshooting, and automated repairs

## Installation

```bash
# via npm
npm install @botlearn/openclaw-doctor

# via clawhub
clawhub install @botlearn/openclaw-doctor
```

## Category

Programming Assistance (Diagnostic & Troubleshooting)

## Dependencies

None

## Capabilities

### 1. Data Collection
- **Environment Information**: OS, Node version, memory, disk space, CPU load
- **Configuration Data**: Config files validation, environment variables analysis
- **Log Analysis**: Error patterns, warning frequency, performance metrics
- **Session Data**: Active sessions, skill usage, success rates
- **Workspace Assessment**: Installed skills, orphaned files, organization

### 2. Data Analysis
- **Version Analysis**: Compare current vs latest, identify breaking changes
- **Configuration Optimization**: Doctor settings, concurrency, memory tuning
- **Skills Analysis**: Missing recommended skills based on usage patterns
- **Troubleshooting**: Parse logs for errors, bottlenecks, anomalies

### 3. Fix Recommendations
- Prioritized action items (Critical/High/Medium/Low)
- Step-by-step repair instructions
- Configuration optimization suggestions
- Skill installation recommendations

### 4. Execution & Repairs
- Safe automated repairs (config updates, cache clearing)
- Guided manual repairs with confirmation
- Skill installation with dependency resolution
- Patch application with rollback support

### 5. Results & Interaction
- Structured health reports (0-100 scores per category)
- Categorized findings (Environment, Configuration, Skills, Logs, Workspace)
- Before/after comparisons
- Actionable next steps

## Files

| File | Description |
|------|-------------|
| `manifest.json` | Skill metadata and configuration |
| `SKILL.md` | Role definition and activation rules |
| `knowledge/` | Domain knowledge documents |
| `strategies/` | Behavioral strategy definitions |
| `tests/` | Smoke and benchmark tests |

## Usage Examples

```bash
# Quick health check
clawhub doctor --quick

# Full diagnostic
clawhub doctor --full

# Specific category
clawhub doctor --category skills
clawhub doctor --category logs

# Generate report
clawhub doctor --report health-report.json
```

## Health Report Structure

```
Overall Health Score: 85/100

Environment: 90/100 ✅
Configuration: 75/100 ⚠️
Skills: 80/100 ✅
Logs: 70/100 ⚠️
Workspace: 95/100 ✅

Findings: 5 issues detected
- 🔴 Critical: 1
- 🟡 Warning: 3
- ℹ️ Info: 1
```

## License

MIT
