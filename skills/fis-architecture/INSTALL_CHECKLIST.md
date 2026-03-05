# Installation Checklist - FIS 3.2.2-lite

> **Minimal installation — maximum clarity**  
> **Security Notice**: Review all Python scripts in `lib/` before execution. Core FIS functionality requires no Python; Python tools are optional helpers.

---

## Security Checklist

Before installing, audit the included files:

- [ ] **Review `lib/` scripts** — Open and verify badge_generator_v7.py and other Python files don't perform unexpected writes or network calls
- [ ] **Understand permissions** — Tickets can include `resources` fields (file_read, code_execute) that affect agent behavior; use with caution
- [ ] **Optional Python tools** — Core FIS works without Python; only run lib/ scripts if you need badge generation
- [ ] **Sandbox first** — Test in an isolated environment before production use

---

## What FIS 3.2 Creates

FIS 3.2 has a **simplified structure**:

```
~/.openclaw/fis-hub/           # Shared Hub (may already exist)
├── tickets/
│   ├── active/                        # Active task tickets
│   └── completed/                     # Archived tickets
├── knowledge/                         # Shared knowledge (QMD-indexed)
├── results/                           # Research outputs
└── .fis3.1/
    └── notifications.json             # Light event log
```

### Directory Details

| Directory | Purpose | Created By |
|-----------|---------|------------|
| `tickets/active/` | Active task JSON files | You (as needed) |
| `tickets/completed/` | Archived task JSON files | You (when archiving) |
| `knowledge/` | Markdown knowledge files | You (as needed) |
| `results/` | Research outputs | SubAgents |
| `.fis3.1/` | Light configuration | Optional |

---

## No Complex Setup Required

Unlike FIS 3.1, **3.2 requires no initialization**:

| Task | FIS 3.1 | FIS 3.2 |
|------|---------|---------|
| Run init script | ✅ Required | ❌ Not needed |
| Create registries | ✅ Required | ❌ Not needed |
| Set Python path | ✅ Required | ❌ Not needed |
| Create complex structure | ✅ Required | ❌ Not needed |
| Create ticket files | ✅ Via API | ✅ Direct JSON |

---

## Optional: First-Time Setup

If `fis-hub/` doesn't exist:

```bash
# Create minimal structure
mkdir -p ~/.openclaw/fis-hub/{tickets/active,tickets/completed,knowledge,results,.fis3.1}
echo '{}' > ~/.openclaw/fis-hub/.fis3.1/notifications.json

echo "✅ FIS 3.2 structure ready"
```

---

## Data Safety

### What FIS Touches

- ✅ Creates: Ticket JSON files
- ✅ Creates: Knowledge Markdown files
- ✅ Creates: Result outputs
- ❌ Never touches: Other agents' Core Files (MEMORY.md, HEARTBEAT.md)
- ❌ Never modifies: OpenClaw configuration files

### Cleanup Behavior

**Task Archiving**:
- Tickets are moved from `active/` to `completed/`
- No automatic deletion
- Manual cleanup if needed

**No Auto-Delete**:
- FIS 3.2 does not auto-delete workspaces
- You control all file lifecycle

---

## Uninstallation

To remove FIS 3.2 (skill only, preserves your data):

```bash
# Remove the skill directory only
rm -rf ~/.openclaw/workspace/skills/fis-architecture

# Your data in fis-hub/ is NOT affected
# To also remove data (WARNING: deletes your tickets/results):
# rm -rf ~/.openclaw/fis-hub/
```

**Note**: The `fis-hub/` directory contains your tickets, results, and knowledge. It is NOT removed by default. Only delete it if you explicitly want to erase all FIS data.

---

## Pre-Installation Check

- [ ] I understand FIS 3.2 is a simplified workflow system
- [ ] I understand no initialization script is needed
- [ ] I understand QMD handles content/search (not FIS)
- [ ] I understand tickets are simple JSON files

## Post-Installation Verify

```bash
# Verify structure
ls ~/.openclaw/fis-hub/tickets/

# Create test ticket
echo '{"ticket_id":"TEST","status":"active"}' > \
  ~/.openclaw/fis-hub/tickets/active/TEST.json

# Verify
cat ~/.openclaw/fis-hub/tickets/active/TEST.json

# Archive
mv ~/.openclaw/fis-hub/tickets/active/TEST.json \
   ~/.openclaw/fis-hub/tickets/completed/

echo "✅ FIS 3.2 working correctly"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Directory not found | Create manually with `mkdir -p` |
| Permission denied | Check `~/.openclaw/` ownership |
| Badge generator fails | Install Pillow: `pip3 install Pillow qrcode` |

---

*FIS 3.2.0-lite — Simple by design 🐱⚡*
