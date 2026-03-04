# OpenClaw iFlow Doctor

> **Version**: 1.1.0 | **Updated**: 2026-03-01 | **Cross-Platform**: Linux/Windows/macOS

AI-powered self-healing system for OpenClaw with intelligent diagnosis, automatic bug fixes, and seamless iFlow integration.

## 🎯 What's New in 1.1.0

### Bug Fixes
- ✅ Fix: watchdog.py --daemon not working
- ✅ Fix: Tilde (~) path expansion
- ✅ Fix: Desktop directory not found
- ✅ Add: systemd service for Linux auto-start

### Improvements
- 🚀 Cross-platform support (Linux/Windows/macOS)
- 📦 Better installation scripts
- 🔧 Improved error handling

## Features

- **Smart Problem Classification** - Automatically categorizes issues into 8 types
- **Repair Case Library** - 10 predefined common problems with solutions
- **Repair History** - Tracks previous repairs with deduplication
- **Dynamic BAT Generation** - Creates repair tools specific to the problem type (max 3)
- **Multi-language Support** - Generates Chinese or English reports based on system language
- **Auto-cleanup** - BAT files self-delete after execution
- **iFlow CLI Integration** - Seamlessly connects to iFlow for manual assistance

## Quick Start

### Installation

```bash
# Option 1: Run installer script
cd ~/.openclaw/skills/openclaw-iflow-doctor
python install.py

# Option 2: Manual install
copy skill files to ~/.openclaw/skills/openclaw-iflow-doctor/
```

### Usage

#### Automatic Trigger
The skill automatically activates when OpenClaw detects errors like:
- Gateway crashes
- Memory search failures
- Configuration errors
- API limit errors
- Agent spawn failures

#### Manual CLI
```bash
# Diagnose a problem
python ~/.iflow/memory/openclaw/openclaw_memory.py --fix "Gateway service crashed"

# List all repair cases
python ~/.iflow/memory/openclaw/openclaw_memory.py --list-cases

# Show statistics
python ~/.iflow/memory/openclaw/openclaw_memory.py --stats
```

## Problem Types & Repair Tools

| Problem Type | Generated BAT (CN) | Generated BAT (EN) | Purpose |
|--------------|-------------------|-------------------|---------|
| memory | 重置记忆索引.bat | reset_memory_index.bat | Reset memory index |
| gateway | 重启Gateway服务.bat | restart_gateway_service.bat | Restart Gateway |
| config | 重置配置文件.bat | reset_configuration.bat | Reset config |
| network | 检查网络连接.bat | check_network_connection.bat | Check network |
| api | 检查API额度.bat | check_api_quota.bat | Check API quota |
| agent | 重新加载Agent.bat | reload_agents.bat | Reload agents |
| permission | 修复权限.bat | fix_permissions.bat | Fix permissions |
| install/unknown | 重新安装openclaw.bat | reinstall_openclaw.bat | Reinstall OpenClaw |

**Always includes**: 打开iFlow寻求帮助.bat / open_iflow_for_help.bat

## How It Works

1. **Search Case Library** - First checks 10 predefined repair cases
2. **Search History** - Then checks previous repair attempts
3. **Classify Problem** - Identifies problem type from error description
4. **Generate Report** - Creates diagnosis report (Chinese or English)
5. **Generate Tools** - Creates up to 3 BAT files specific to the problem
6. **Self-delete** - BAT files auto-delete after execution

## File Structure

```
~/.iflow/memory/openclaw/
├── openclaw_memory.py      # Main repair engine
├── cases.json              # Repair case library (10 cases)
├── records.json            # Repair history
├── call_logs.json          # Usage logs
├── config.json             # System configuration
├── skill.md                # OpenClaw skill definition
├── install.py              # Python installer
├── install.bat             # Windows installer
└── README.md               # This file
```

## Repair Case Library

1. **Memory Search Function Broken** - Memory index corruption
2. **Gateway Service Not Starting** - Gateway crash/startup failure
3. **API Rate Limit Exceeded** - 429/quota errors
4. **Agent Spawn Failed** - Agent configuration issues
5. **Channel Configuration Error** - DingTalk/Feishu integration
6. **Model Provider Connection Failed** - API connectivity issues
7. **Configuration File Corrupted** - JSON syntax errors
8. **Multiple Agents Conflict** - Agent routing conflicts
9. **Permission Denied Errors** - File permission issues
10. **Log File Too Large** - Log cleanup needed

## Configuration

Edit `~/.iflow/memory/openclaw/config.json`:

```json
{
  "version": "2.0",
  "enable_bat_generation": true,
  "enable_txt_report": true,
  "similarity_threshold": 0.85,
  "max_records": 100,
  "auto_archive": true
}
```

## Diagnosis Report

When automatic repair is not possible, generates:

- **Chinese Systems**: `openclaw诊断书_YYYYMMDD.txt`
- **English Systems**: `openclaw_diagnosis_report_YYYYMMDD.txt`

Reports include:
- Problem description
- Attempted solutions
- Error logs
- Generated BAT tools with usage explanations
- Instructions for manual assistance

## Integration with iFlow CLI

If automatic repair fails:

1. **Double-click** `打开iFlow寻求帮助.bat` on Desktop
2. **Or** type `iflow` in terminal
3. **Describe** the problem to get manual assistance

## Requirements

- Windows OS
- Python 3.8+
- OpenClaw installed
- iFlow CLI (for manual assistance)

## License

MIT

## Credits

Inspired by [openclaw-self-healing](https://github.com/Ramsbaby/openclaw-self-healing)
