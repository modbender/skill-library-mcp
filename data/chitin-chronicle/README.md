# Chitin Editorial — P0 Complete ✅

**Multi-agent content coordination system for Vesper and Ember**

## What's Built

✅ **Content Registry** (`editorial/registry.json`)  
✅ **Publication Ledger** (`editorial/ledger.json`)  
✅ **Timeline Tracker** (`editorial/timeline.json`)  
✅ **Cross-Agent Claim System** (`editorial/claims/`)  
✅ **Boot Hook Integration** (`editorial/boot-check.sh`)  
✅ **CLI Tools** (`scripts/editorial.js`)

## Quick Start

```bash
# Check editorial state
node scripts/editorial.js status

# Before publishing, check for conflicts
node scripts/editorial.js check "day-14" "substack"

# Claim your work
node scripts/editorial.js claim "day-14" "publish" "substack"

# After publishing, record it
node scripts/editorial.js publish "day-14" "substack" "https://..." "Title"

# Boot check (add to AGENTS.md startup)
bash editorial/boot-check.sh
```

## Files

```
chitin-editorial/
├── SKILL.md              — Complete documentation
├── README.md             — This file
├── _meta.json            — Skill metadata
├── scripts/
│   └── editorial.js      — CLI tool (claim/publish/status/check/release)
└── editorial/
    ├── registry.json     — Content registry
    ├── ledger.json       — Publication ledger
    ├── timeline.json     — Narrative timeline
    ├── boot-check.sh     — Boot hook script
    └── claims/
        ├── *.claim       — Active claims
        └── archive/      — Released/expired claims
```

## Test Results

All P0 tests passed:

✅ Status (empty state)  
✅ Claim creation  
✅ Conflict checking  
✅ Publishing  
✅ Duplicate prevention  
✅ Status with data  
✅ Boot hook execution  
✅ Conflict detection between agents

## Technical Specs

- **Language:** Node.js (zero dependencies)
- **Performance:** All ops <500ms
- **Storage:** Git-backed JSON files
- **Claim TTL:** 2 hours auto-expiry
- **Timeline:** Days 0-13 pre-populated for building-vesper series

## Integration

Add to your `AGENTS.md` startup sequence:

```markdown
3. Run `bash /path/to/chitin-editorial/editorial/boot-check.sh` — load editorial state
```

## Next Steps (P1)

- Multi-Channel Scheduler
- Brand Voice Gate
- Content Recycling Engine

---

**Built:** 2026-02-28  
**By:** Vesper 🌒 (subagent)  
**Status:** Ready for production use
