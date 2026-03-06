# Installation Guide

This guide covers multiple installation methods for claw-memory-lite.

## Prerequisites

- OpenClaw installed and running
- Python 3.10+ (sqlite3 built-in)
- Write access to OpenClaw workspace

---

## Method 1: Git Clone (Recommended for Development)

### Step 1: Clone Repository

```bash
cd /home/node/.openclaw/workspace
git clone https://github.com/timothysong0w0/claw-memory-lite.git
```

### Step 2: Copy Scripts

```bash
# Copy Python scripts to workspace
cp claw-memory-lite/scripts/*.py scripts/

# Make executable
chmod +x scripts/*.py
```

### Step 3: Initialize Database

```bash
# Run extraction script (creates database automatically)
python3 scripts/extract_memory.py
```

### Step 4: Verify Installation

```bash
# Query database (should show existing memories)
python3 scripts/db_query.py --stats
```

---

## Method 2: OpenClaw Skill (When Published)

```bash
npx skills add timothysong0w0/claw-memory-lite --agent openclaw --yes
```

The skill installer will automatically:
- Copy scripts to correct locations
- Initialize database
- Update HEARTBEAT.md

---

## Method 3: Manual Download

### Download Files

```bash
# Create project directory
mkdir -p /home/node/.openclaw/workspace/projects/claw-memory-lite

# Download scripts (replace with actual URLs)
curl -O https://raw.githubusercontent.com/timothysong0w0/claw-memory-lite/main/scripts/db_query.py
curl -O https://raw.githubusercontent.com/timothysong0w0/claw-memory-lite/main/scripts/extract_memory.py

# Move to scripts directory
mv *.py /home/node/.openclaw/workspace/scripts/
```

### Initialize

```bash
cd /home/node/.openclaw/workspace
python3 scripts/extract_memory.py
```

---

## Post-Installation Configuration

### 1. Update HEARTBEAT.md

Add memory extraction to your heartbeat tasks:

```bash
python3 /home/node/.openclaw/workspace/scripts/extract_memory.py
```

### 2. Configure Cron (Optional)

For automated daily extraction, add a cron job:

```bash
# Edit crontab
crontab -e

# Add daily extraction at 3 AM UTC
0 3 * * * cd /home/node/.openclaw/workspace && python3 scripts/extract_memory.py
```

### 3. Set Environment Variables (Optional)

Customize database path and workspace:

```bash
export CLAW_MEMORY_DB_PATH="/custom/path/memory.db"
export CLAW_MEMORY_WORKSPACE="/custom/workspace"
```

Add to `.bashrc` or `.zshrc` for persistence.

---

## Verification

Run these commands to verify installation:

```bash
# Check database exists
ls -lh /home/node/.openclaw/database/insight.db

# Query stats
python3 scripts/db_query.py --stats

# List categories
python3 scripts/db_query.py --categories

# Test search
python3 scripts/db_query.py test
```

---

## Troubleshooting

### Database Not Found

```
Error: Database not found at /home/node/.openclaw/database/insight.db
```

**Solution**: Run `python3 scripts/extract_memory.py` to initialize.

### Permission Denied

```
PermissionError: [Errno 13] Permission denied
```

**Solution**: Ensure write access to workspace and database directories.

```bash
chmod -R u+w /home/node/.openclaw/workspace
chmod -R u+w /home/node/.openclaw/database
```

### No Memories Extracted

```
✅ All daily memory files have been processed.
```

**Solution**: This is normal if all files are already processed. Add new content to `memory/*.md` files or run with `--force` flag to re-process.

---

## Next Steps

- [Configure Integration](integration.md) - Set up automated extraction
- [Usage Guide](../README.md#usage) - Learn query commands
- [API Reference](api.md) - Database schema details
