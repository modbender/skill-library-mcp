# Publish Guide - FIS 3.2.0-lite

> **Publishing FIS to GitHub and ClawHub**

---

## Current Status

| Item | Status |
|------|--------|
| Git repository | ✅ Initialized |
| GitHub remote | ✅ Connected (MuseLinn/fis-architecture) |
| Files updated | ✅ FIS 3.2 documentation |
| Legacy components | ✅ Removed from release (preserved in GitHub history) |

---

## File Manifest

```
fis-architecture/
├── .gitignore              # Git ignore rules
├── skill.json              # Skill metadata
├── README.md               # Project homepage
├── SKILL.md                # Full documentation (⭐ updated to 3.2)
├── QUICK_REFERENCE.md      # Quick command reference (⭐ updated)
├── AGENT_GUIDE.md          # Agent usage guide (⭐ updated)
├── CONFIGURATION.md        # Configuration guide (⭐ updated)
├── POST_INSTALL.md         # Post-install setup (⭐ updated)
├── INSTALL_CHECKLIST.md    # Installation checklist (⭐ updated)
├── OPENCLAW_COMPATIBILITY.md # Compatibility notes (⭐ updated)
├── PUBLISH_GUIDE.md        # This file
├── REVIEW.md               # Review notes
├── package.json            # ClawHub metadata
├── lib/                    # Tools
│   ├── badge_generator_v7.py      # ✅ Badge generation (current)
│   ├── badge_generator_ascii.py   # ✅ ASCII badge gen
│   ├── fis_lifecycle.py           # ✅ Lifecycle helpers
│   ├── fis_subagent_tool.py       # ✅ CLI helper
│   ├── fis_config.py              # ✅ Config utilities
│   └── multi_worker_demo.py       # ✅ Demo script
├── archive/                # Empty (legacy 3.1 in GitHub history only)
└── examples/               # Usage examples
    └── generate_badges.py  # ✅ Badge generation demo
```

---

## Pre-Release Checklist

- [ ] All documentation updated to 3.2
- [ ] Legacy components removed from release (preserved in GitHub history)
- [ ] Version numbers updated in:
  - `skill.json`
  - `package.json`
  - All documentation headers
- [ ] Git status clean (no uncommitted changes)
- [ ] Test badge generation works

---

## Release Steps

### 1. Update Version Numbers

```bash
# Edit skill.json
{
  "name": "fis-architecture",
  "version": "3.2.0-lite",
  ...
}

# Edit package.json
{
  "version": "3.2.0-lite",
  ...
}
```

### 2. Commit Changes

```bash
cd ~/.openclaw/workspace/skills/fis-architecture

git add -A
git commit -m "feat: FIS 3.2.0-lite release

Major changes:
- Simplified architecture: FIS manages workflow, QMD manages content
- Removed overlapping components (memory_manager, skill_registry, etc.)
- Updated all documentation to 3.2
- Archived deprecated files
- Pure file-based ticket system (no Python setup required)

Breaking changes from 3.1:
- memory_manager.py → Use QMD
- skill_registry.py → Use SKILL.md + QMD
- deadlock_detector.py → Use conventions
- fis_lifecycle.py → Use JSON tickets directly"
```

### 3. Push to GitHub

```bash
# Ensure on main branch
git branch -M main

# Push commits
git push origin main

# Create release tag
git tag -a v3.2.0-lite -m "FIS 3.2.0-lite - Simplified Architecture

Core principle: FIS manages workflow, QMD manages content

Features:
- Pure file-based ticket system
- QMD integration for content/search
- Streamlined component set
- Updated documentation"

git push origin v3.2.0-lite
```

### 4. Create GitHub Release

1. Go to: https://github.com/MuseLinn/fis-architecture/releases
2. Click "Create a new release"
3. Choose tag: `v3.2.0-lite`
4. Title: "FIS 3.2.0-lite — Simplified Architecture"
5. Description:
```markdown
## FIS 3.2.0-lite

**Core Principle: FIS manages workflow, QMD manages content**

### What's New
- Simplified file-based ticket system (JSON)
- QMD integration replaces custom registries
- Removed overlapping components
- Updated documentation

### Breaking Changes from 3.1
| Component | Replacement |
|-----------|-------------|
| memory_manager.py | QMD semantic search |
| skill_registry.py | SKILL.md + QMD |
| deadlock_detector.py | Simple conventions |
| fis_lifecycle.py | JSON tickets |

### Migration
Legacy FIS 3.1 components are preserved in GitHub repo history for reference.

### Quick Start
```bash
mkdir -p tickets/active tickets/completed knowledge
echo '{"ticket_id":"TEST","status":"active"}' > tickets/active/test.json
```
```

### 5. Publish to ClawHub

```bash
# Using clawhub CLI
clawhub publish \
  --name fis-architecture \
  --version 3.2.0-lite \
  --description "FIS 3.2 Lite - Simplified multi-agent workflow framework" \
  --tags "multi-agent,workflow,tickets,qmd" \
  --github https://github.com/MuseLinn/fis-architecture
```

Or manually:
1. Visit https://clawhub.com
2. Click "Publish Skill"
3. Fill in:
   - Name: `fis-architecture`
   - Version: `3.2.0-lite`
   - Description: `Federal Intelligence System 3.2 Lite`
   - GitHub: `https://github.com/MuseLinn/fis-architecture`

---

## Post-Release Verification

```bash
# 1. Verify GitHub release
curl -s https://api.github.com/repos/MuseLinn/fis-architecture/releases/latest | grep tag_name

# 2. Test install (if published to ClawHub)
clawhub install fis-architecture --version 3.2.0-lite

# 3. Verify badge generation still works
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py
```

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 3.2.0-lite | 2026-02-19 | Simplified architecture |
| 3.1.3 | 2026-02-18 | Generalized release |
| 3.1.0 | 2026-02-17 | Initial Lite release |

---

*Ready to publish 🚀*
