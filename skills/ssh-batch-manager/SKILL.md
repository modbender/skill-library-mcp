---
name: ssh-batch-manager
description: Batch SSH key management. Distribute/remove SSH keys to/from multiple servers with intelligent connectivity pre-check and source tracking.
homepage: https://gitee.com/subline/onepeace/tree/develop/src/skills/ssh-batch-manager
metadata:
  {
    "openclaw":
      {
        "emoji": "🔑",
        "requires": { "bins": ["ssh", "ssh-copy-id", "sshpass"], "python_packages": ["cryptography"] },
      },
  }
---

# SSH Batch Manager

## ⚠️ CRITICAL SAFETY RULE

**EN: Before executing ANY enable operation, the agent MUST obtain explicit user confirmation via message. NEVER execute without explicit user approval.**

---

Batch management of SSH key-based authentication.

## Features

- ✅ Intelligent connectivity pre-check (40x faster)
- ✅ Source identifier in authorized_keys
- ✅ Mandatory safety confirmation
- ✅ Auto-start Web UI service

## Installation

```bash
clawhub install ssh-batch-manager
```

Web UI auto-starts after installation!

## Usage

```bash
# Enable all servers
python3 ssh-batch-manager.py enable-all

# Disable all servers
python3 ssh-batch-manager.py disable-all

# Web UI: http://localhost:8765
```

## Version

**v2.1.3** - Complete English translation (Web UI + Docs + Code)

## Repository

**Source**: https://gitee.com/subline/onepeace/tree/develop/src/skills/ssh-batch-manager

**License**: MIT

**Author**: TK
