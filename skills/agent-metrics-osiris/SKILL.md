---
name: agent-metrics
version: 1.0.3
description: Observability and metrics for AI agents - track calls, errors, latency
metadata: {"openclaw": {"emoji": "📊", "category": "utility", "requires": {"bins": ["python"], "pip": ["psutil"]}, "homepage": "https://github.com"}
---

# Agent Metrics Skill

Track and monitor your AI agent's behavior with built-in observability.

**Files included:**
- `metrics.py` - Python CLI (cross-platform)
- `agent-metrics.ps1` - PowerShell wrapper (Windows)

## What it does

- **Call Tracking** - Count API calls, messages, tasks
- **Error Logging** - Track errors with stack traces
- **Latency Metrics** - Measure response times
- **Resource Usage** - CPU, memory, network
- **Simple Dashboard** - Terminal-based metrics view
- **Export** - JSON export for external dashboards

## Installation

```powershell
# Install Python dependency
pip install psutil
```

## Usage

### Option 1: PowerShell (recommended on Windows)

```powershell
.\agent-metrics.ps1 -Action record -MetricType call -Label "api_openai"
```

### Option 2: Python CLI (cross-platform)

```powershell
python metrics.py record --type call --label "api_openai"
```

### Record an Error

```powershell
.\agent-metrics.ps1 -Action record -MetricType error -Label "api_error" -Details "Rate limit exceeded"
```

### Record Latency

```powershell
.\agent-metrics.ps1 -Action record -MetricType latency -Label "task_process" -Value 1500
```

### View Dashboard

```powershell
.\agent-metrics.ps1 -Action dashboard
```

### View Resource Usage (CPU, Memory, Disk)

```powershell
.\agent-metrics.ps1 -Action resources
```

### Export Metrics

```powershell
.\agent-metrics.ps1 -Action export -Format json -Output metrics.json
```

### Get Summary

```powershell
.\agent-metrics.ps1 -Action summary
```

## Metrics Types

| Type | Description | Fields |
|------|-------------|--------|
| call | API call made | label, timestamp |
| error | Error occurred | label, details, timestamp |
| latency | Response time (ms) | label, value, timestamp |
| custom | Custom metric | label, value |

## Dashboard Example

```
╔═══════════════════════════════════════════════╗
║           AGENT METRICS DASHBOARD            ║
╠═══════════════════════════════════════════════╣
║ Total Calls:     1,247                       ║
║ Total Errors:   23                          ║
║ Error Rate:     1.84%                        ║
║ Avg Latency:    234ms                        ║
║ Uptime:         4h 32m                      ║
╠═══════════════════════════════════════════════╣
║ Top Labels:                                  ║
║   api_openai      892 (71.5%)               ║
║   api_claude      234 (18.8%)               ║
║   task_process    121 (9.7%)                ║
╚═══════════════════════════════════════════════╝
```

## Requirements

- Python 3.8+
- psutil library

## License

MIT
