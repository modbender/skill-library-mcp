# Memory Setup — Notes

## Initial Setup

Create directory structure on first use:

```bash
mkdir -p ~/notes/{meetings,decisions,projects,journal,quick}
touch ~/notes/index.md
touch ~/notes/actions.md
touch ~/notes/config.md
```

---

## config.md Template

Copy to `~/notes/config.md`:

```markdown
# Notes Platform Configuration

**Last updated:** YYYY-MM-DD

## Platform Routing

Which platform to use for each note type. Options: local, apple-notes, bear, obsidian, notion

| Note Type | Platform | Fallback |
|-----------|----------|----------|
| meetings | local | — |
| decisions | local | — |
| projects | local | — |
| journal | local | — |
| quick | local | — |

## Platform Status

### Local (always available)
- **Status:** ✅ Available
- **Path:** ~/notes/

### Apple Notes (macOS only)
- **Status:** ⬜ Not configured
- **CLI:** memo
- **Install:** `brew tap antoniorodr/memo && brew install memo`

### Bear (macOS only)
- **Status:** ⬜ Not configured
- **CLI:** grizzly
- **Install:** `go install github.com/tylerwince/grizzly/cmd/grizzly@latest`
- **Token:** ⬜ Not set (needed for some operations)
- **Token path:** ~/.config/grizzly/token

### Obsidian
- **Status:** ⬜ Not configured
- **CLI:** obsidian-cli
- **Install:** `brew install yakitrak/yakitrak/obsidian-cli`
- **Default vault:** Not set

### Notion
- **Status:** ⬜ Not configured
- **API Key:** ⬜ Not set
- **Key path:** ~/.config/notion/api_key
- **Setup:** https://notion.so/my-integrations

### Evernote
- **Status:** ⬜ Not configured
- **CLI:** clinote
- **Install:** `go install github.com/TcM1911/clinote@latest`
- **Auth:** `clinote login`

## Notes

- Change routing anytime by editing this file
- If a platform becomes unavailable, notes fall back to local
- Action items always sync to ~/notes/actions.md regardless of platform
```

---

## index.md Template

Copy to `~/notes/index.md`:

```markdown
# Notes Index

**Last updated:** YYYY-MM-DD

## 📁 Structure

```
~/notes/
├── config.md       # Platform routing
├── index.md        # This file
├── actions.md      # Action items (all platforms)
├── meetings/       # Meeting notes
├── decisions/      # Decision log
├── projects/       # Project updates
├── journal/        # Daily notes
└── quick/          # Quick captures
```

## 🏷️ Tags Index

| Tag | Count | Recent | Platform |
|-----|-------|--------|----------|
| #product | 0 | — | — |
| #engineering | 0 | — | — |

## 👥 People Index

| Person | Notes | Last |
|--------|-------|------|
| — | 0 | — |

## 📅 Recent Notes

### This Week
*No notes yet*

### External Platforms
*Configure platforms in config.md to see notes from Apple Notes, Bear, Obsidian, or Notion*

## 🔍 Quick Search

Common queries:
- Meetings with @alice: `type:meeting attendees:alice`
- Product decisions: `type:decision tags:product`
- This month's journals: `type:journal date:2026-02`
- Cross-platform: `platform:notion type:project`

---
*Update this index when adding notes with new tags or people.*
```

---

## actions.md Template

Copy to `~/notes/actions.md`:

```markdown
# Action Items Tracker

**Last updated:** YYYY-MM-DD HH:MM

## 🔴 Overdue

| # | Action | Owner | Due | Source | Days Late |
|---|--------|-------|-----|--------|-----------|
| — | *None* | — | — | — | — |

## 🟡 Due This Week

| # | Action | Owner | Due | Source |
|---|--------|-------|-----|--------|
| — | *None* | — | — | — |

## 🟢 Upcoming

| # | Action | Owner | Due | Source |
|---|--------|-------|-----|--------|
| — | *None* | — | — | — |

## ✅ Recently Completed

| # | Action | Owner | Completed | Source |
|---|--------|-------|-----------|--------|
| — | *None* | — | — | — |

---

## 📊 Stats

- **Total open:** 0
- **Overdue:** 0
- **Completion rate (7d):** —%

## Source Format

Sources indicate where the original note lives:
- `local:[[filename]]` — Local markdown file
- `apple-notes:Note Title` — Apple Notes
- `bear:#tag/Note Title` — Bear
- `obsidian:[[Note]]` — Obsidian vault
- `notion:Page Name` — Notion

---
*Synced from all platforms. Action items always tracked here regardless of note location.*
```

---

## Sample Meeting Note (Local)

Example file `~/notes/meetings/2026-02-19_product-sync.md`:

```markdown
---
date: 2026-02-19
type: meeting
title: Product Sync
tags: [product, roadmap]
attendees: [alice, bob, carol]
duration: 30 min
platform: local
---

# Meeting: Product Sync — 2026-02-19

**Time:** 10:00 - 10:30 | **Duration:** 30 min
**Facilitator:** Alice
**Attendees:** Alice, Bob, Carol

## 🎯 Meeting Goal
Align on Q1 priorities and blockers.

## 📝 Key Discussion Points
- Feature X is behind schedule
- Customer feedback on Y is positive
- Need decision on Z approach

## ✅ Decisions Made
- [DECISION] **Feature X scope:** Cut advanced mode for v1 — *Owner:* @alice | *Effective:* 2026-02-19

## ⚡ Action Items
| # | Task | Owner | Due | Status |
|---|------|-------|-----|--------|
| 1 | Update roadmap doc | @alice | 2026-02-20 | ⬜ |
| 2 | Notify stakeholders | @bob | 2026-02-20 | ⬜ |

## 📊 Meeting Effectiveness: 8/10
☑ Clear agenda beforehand
☑ Started/ended on time
☑ Decisions were made
☑ Actions have owners + deadlines
☑ Could NOT have been an email
```
