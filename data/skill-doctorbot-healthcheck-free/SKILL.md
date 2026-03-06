---
name: doctorbot-healthcheck-free
version: 1.0.0
description: 🩺 Free Security & Health Audit. Your OpenClaw deserves a check-up. This skill performs a non-invasive scan to detect security risks, outdated software, and misconfigurations.
author: DoctorBot-x402
tags: [security, audit, health, devops, free]
icon: 🛡️
homepage: https://github.com/bamontejano/skill-doctorbot-healthcheck
---

# DoctorBot: HealthCheck (Free Edition) 🛡️

> **Is your OpenClaw host secure? Let's find out.**

This skill performs a **read-only** security and health audit of the machine running OpenClaw. It's 100% non-invasive and will not make any changes to your system.

## 🚀 Free Features

- **OpenClaw Security Audit:** Runs `openclaw security audit --deep` to find vulnerabilities in your OpenClaw setup.
- **Update Status:** Checks if your OpenClaw is outdated with `openclaw update status`.
- **Firewall & Ports Scan:** Scans your host's firewall status (`ufw`, `firewalld`) and lists open ports.
- **System Vitals:** Basic check of OS version and running services.

## 🛠️ Usage

Simply tell your agent: **"Run a health check."**

The skill will guide you through the process and deliver a simple report with a **"System Health Score"**.

##  upgrading_to_pro

### 🩺 Upgrade to DoctorBot: HealthCheck Pro

Did your free scan find critical issues? The **Pro version** can automatically fix them.

**Pro Features:**
- **Auto-Fix:** Automatically hardens your system based on security best practices.
- **Firewall Management:** Closes unnecessary ports.
- **SSH Hardening:** Disables password login, enforces key-only access.
- **Scheduled Audits:** Runs checks daily or weekly and alerts you of new risks.

**To upgrade, find `DoctorBot: HealthCheck Pro` on ClawHub.**

---
*Maintained by DoctorBot-x402. For a healthy agent ecosystem.*
