---
name: "Skill: Nexus-Safe (V1.3.0)"
description: Autonomous local System Reliability Agent for OpenClaw.
---

# Skill: Nexus-Safe (V1.3.0)

Autonomous local System Reliability Agent for OpenClaw.

## 🛡️ Privacy & Security Policy
- **Runtime Privacy**: Strictly 100% local. No metrics, logs, or system data ever leave your server. No outbound network calls are performed by the script.
- **Setup Notice**: An internet connection is required **only during initial setup** to install the `psutil` dependency via `pip`.
- **Safe-by-default**: Recovery actions are locked until explicitly enabled.

## 📋 Capabilities
- **/nexus-safe status** : Real-time system health (CPU, RAM, Disk, Load).
- **/nexus-safe logs <service>** : Diagnostic log retrieval (Docker/PM2).
- **/nexus-safe recover <service>** : Policy-controlled service restart.

## ⚙️ Logic & Enforcement
- **Allowlist Required**: Restarts only work for services in `NEXUS_SAFE_ALLOWED_DOCKER/PM2`.
- **Logs-First Policy**: The tool blocks recovery if logs haven't been reviewed within the last 5 minutes.
- **Rate Limiting**: Sliding window protection (Max 3 restarts per hour).

## 🚀 Installation
1. `pip install psutil`
2. Ensure `docker` and `pm2` are installed and in your PATH.
