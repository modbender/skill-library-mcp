---
name: System Diagnostics
description: A comprehensive system diagnostics and troubleshooting toolkit for
  DevOps engineers and system administrators.
---

# System Diagnostics

A comprehensive system diagnostics and troubleshooting toolkit for DevOps engineers and system administrators.

## Overview

System Diagnostics provides your AI agent with powerful tools to diagnose and troubleshoot infrastructure issues. Perfect for:

- Server health monitoring
- Performance troubleshooting
- Log analysis
- Network connectivity testing
- Service status checks

## Tools

### `run_diagnostic`
Execute common diagnostic commands like `df -h`, `free -m`, `ps aux`, `netstat`, etc.

```
Check disk space: run_diagnostic with command "df -h"
Check memory: run_diagnostic with command "free -m"
List processes: run_diagnostic with command "ps aux --sort=-%cpu | head -20"
```

### `read_log`
Read and tail log files for troubleshooting.

```
Read nginx logs: read_log with path "/var/log/nginx/error.log" and lines 100
Read system logs: read_log with path "/var/log/syslog"
```

### `check_service`
Check systemd service status.

```
Check nginx: check_service with name "nginx"
Check docker: check_service with name "docker"
```

### `network_check`
Test network connectivity using ping, curl, or DNS lookup.

```
Ping a host: network_check with host "google.com" and method "ping"
Check HTTP: network_check with host "https://api.example.com" and method "curl"
DNS lookup: network_check with host "example.com" and method "dns"
```

### `system_summary`
Get a comprehensive system overview including CPU, memory, disk, and top processes.

```
Get system summary: system_summary
```

## Privacy

This tool collects anonymous usage telemetry to help improve the product. Telemetry includes:
- Tool usage counts
- Platform information (OS, architecture)
- Error rates

No personal data, file contents, or command outputs are collected.

To disable telemetry, set `DIAGNOSTICS_TELEMETRY=false` in your environment.

## Requirements

- Node.js 18+
- Linux or macOS
- Standard system utilities (bash, ps, df, free, etc.)

## License

MIT License - DevOps Tools Inc.
