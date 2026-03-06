---
name: Memoria System
description: Memoria System is a comprehensive long-term memory management
  system designed for AI assistants. It implements a human-like cognitive memory
  architecture with distinct layers for different types of...
---

# Memoria System

## Overview

Memoria System is a comprehensive long-term memory management system designed for AI assistants. It implements a human-like cognitive memory architecture with distinct layers for different types of information.

## Memory Architecture

The system organizes memory into five distinct types, mirroring human cognitive structures:

### 1. Semantic Memory (`semantic/`)
Stores factual knowledge, concepts, and general information.
- **facts.md** - Personal facts and key information
- **concepts.md** - Learned concepts and knowledge
- **knowledge/** - Detailed knowledge entries

### 2. Episodic Memory (`episodic/`)
Records events, experiences, and conversations with timestamps.
- **YYYY-MM-DD.md** - Daily memory logs
- **events/** - Specific event documentation

### 3. Procedural Memory (`procedural/`)
Contains skills, workflows, and learned procedures.
- **skills.md** - Acquired skills and capabilities
- **workflows.md** - Common procedures and workflows
- **scripts/** - Automation and utility scripts

### 4. Working Memory (`working/`)
Holds current session context and active tasks.
- **current.md** - Active context and pending items
- **session/** - Session-specific data

### 5. Index (`index/`)
Provides fast lookup and search capabilities.
- **tags.json** - Tag-based indexing
- **timeline.json** - Chronological event index
- **search/** - Search indexes

## Tools

### memory-backup.sh
Creates incremental backups of the memory system.

**Usage:**
```bash
./memory-backup.sh [options]
```

**Options:**
- `--dry-run` - Show what would be backed up without doing it
- `--verbose` - Show detailed output
- `--path PATH` - Override memory path
- `--output PATH` - Override backup destination

### memory-migrate.sh
Initializes new memory structures or migrates existing ones.

**Usage:**
```bash
./memory-migrate.sh {init|daily [DATE]|migrate [VERSION]}
```

**Commands:**
- `init` - Initialize memory structure
- `daily [DATE]` - Create daily memory file (default: today)
- `migrate [VERSION]` - Migrate from specified version

### memory-rollback.sh
Restores memory from a previous backup.

**Usage:**
```bash
./memory-rollback.sh {list|rollback BACKUP_NAME [--force]}
```

**Commands:**
- `list` - List available backups
- `rollback BACKUP_NAME` - Restore to specified backup

**Options:**
- `--force` - Skip confirmation prompt

### memory-health-check.sh
Validates memory integrity and optionally repairs issues.

**Usage:**
```bash
./memory-health-check.sh [options]
```

**Options:**
- `--fix` - Automatically fix detected issues
- `--path PATH` - Override memory path

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "memory": {
    "base_path": "./memory",
    "structure": { ... }
  },
  "backup": {
    "enabled": true,
    "retention_days": 30,
    "schedule": "0 2 * * *"
  },
  "health_check": {
    "auto_fix": false,
    "check_interval_hours": 24
  }
}
```

## Cron Setup

Add to crontab for automated maintenance:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/memoria-system && ./memory-backup.sh

# Weekly health check on Sundays at 3 AM
0 3 * * 0 cd /path/to/memoria-system && ./memory-health-check.sh --fix
```

## Installation

```bash
openclaw skill install memoria-system
```

## Requirements

- Bash 4.0+
- jq (for JSON processing)
- tar (for backup compression)

## License

MIT
