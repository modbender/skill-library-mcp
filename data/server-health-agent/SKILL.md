---
name: server-health-agent
description: Monitor VPS and server health metrics including real-time CPU usage, RAM utilization, disk usage, and Docker container status. Useful for DevOps monitoring, troubleshooting performance issues, and infrastructure health checks.
runtime: node
entry: skill.js
permissions:
  - shell
---

# Server Health Agent

Server Health Agent is a production-ready OpenClaw skill designed to provide real-time monitoring of key server health metrics. It helps developers, DevOps engineers, and system administrators quickly assess the operational health of their VPS or server.

This skill executes safe system-level read-only commands to collect accurate health metrics without modifying the system.

---

# Key Features

## Real-Time CPU Monitoring
Uses live system commands (`top`) to capture current CPU utilization, with fallback mechanisms to ensure reliability even in restricted environments.

## Memory (RAM) Monitoring
Reports accurate RAM usage percentage using system-level commands and Node.js fallback logic.

## Disk Usage Monitoring
Provides root filesystem disk utilization, allowing detection of storage pressure or capacity issues.

## Docker Container Detection
Detects and reports running Docker containers and their status when Docker socket access is available.

Gracefully handles environments where Docker access is restricted.

## Structured Output
Returns structured JSON output optimized for OpenClaw automation workflows and downstream processing.

---

# Use Cases

This skill is useful for:

- VPS health monitoring
- DevOps automation workflows
- Infrastructure monitoring
- Troubleshooting performance issues
- Detecting resource bottlenecks
- Monitoring containerized environments
- Automated system health checks

---

# Example Output

```json
{
  "success": true,
  "skill": "server-health-agent",
  "timestamp": "2026-02-20T12:00:00Z",
  "server_health": {
    "cpu_percent": "12.44",
    "ram_percent": "21.33",
    "disk_usage": "51%",
    "docker_status": "openclaw-openclaw-gateway-1: Up 2 hours"
  }
}
