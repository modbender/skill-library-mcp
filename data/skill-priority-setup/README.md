# Skill Priority Setup - Package Summary

## Files Created

```
skill-priority-setup/
├── SKILL.md                      # Main skill definition
├── clawhub.yaml                  # ClawHub publishing metadata
├── README.docx                   # DOCX format README
├── README.md                     # This file
└── scripts/
    ├── setup.py                  # Main setup wizard
    └── generate_docx.py          # DOCX generator
```

## What This Package Does

1. **Scans** all installed skills in standard directories
2. **Analyzes** skill types and dependencies
3. **Suggests** L0-L3 tier assignments
4. **Configures** injection policy for optimal token usage
5. **Validates** configuration and creates backups

## Key Features

- **4-Tier Architecture**: L0 (ROM) → L1 (Routing) → L2 (Domain) → L3 (Extensions)
- **Token Budget Control**: ≤900 tokens/round with overflow protection
- **Interactive Wizard**: Review and modify suggestions before applying
- **Safety First**: Automatic backups, dry-run mode, JSON validation
- **Customizable**: Configurable tier patterns and budgets

## Usage Flow

```
User runs setup.py
    ↓
System scans installed skills
    ↓
Analyzes and suggests L0-L3 tiers
    ↓
User reviews/modifies suggestions
    ↓
Applies configuration
    ↓
Validates and reports token savings
```

## For ClawHub Users

This skill is designed to be **adaptive**:
- Works with any skill collection
- Analyzes YOUR specific installed skills
- Provides customized tier suggestions
- Non-destructive (backups always created)

## Post-Install

After running setup.py, your system will have:
- `SKILL_PRIORITY_POLICY.md` - Your custom policy
- Updated `AGENTS.md` - ROM constraints
- Updated message injector config
- Backups in `~/.openclaw/backup/`

## ClawHub URL

**Published at**: https://clawhub.ai/halfmoon82/skill-priority-setup

## Upload to ClawHub

```bash
# Method 1: CLI (if authenticated)
npx clawhub publish

# Method 2: Manual upload
# 1. Download skill-priority-setup-v1.0.0.zip
# 2. Go to https://clawhub.com/upload
# 3. Upload the zip file
```
