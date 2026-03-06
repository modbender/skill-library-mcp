---
name: clawstats
description: "Comprehensive system monitoring for OpenClaw: CPU, RAM, Disk, and Processes."
---

# 📊 ClawStat Skill

A comprehensive system monitoring skill for OpenClaw agents to track server health and performance.

## 🚀 Features
- **CPU & RAM**: Real-time usage statistics.
- **Disk**: Track available space on the root partition.
- **Temperature**: Monitor CPU temperature (via `sensors` or `thermal_zone`).
- **Top Processes**: Identify resource-hungry applications.
- **Load Average**: Check system pressure over time.

## 🛠️ Tools
The skill provides a single versatile script:
- `monitor.sh [cpu|ram|disk|temp|top|all]`: Get specific or full system stats.

## 📦 Installation (Manual)
1. Clone or copy this directory to `~/.openclaw/workspace/skills/clawstats`.
2. Ensure `monitor.sh` is executable: `chmod +x monitor.sh`.
3. (Optional) Install `lm-sensors` for temperature tracking.

## 📖 Usage Examples
- `monitor.sh all`: Get a complete health report.
- `monitor.sh top`: See which processes are slowing down the system.

---
*Created by Chela 🫐 & Aprilox*
