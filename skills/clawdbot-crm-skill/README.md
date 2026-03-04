# 📇 Personal CRM Skill for Clawdbot

A lightweight, markdown-based personal CRM for managing contacts, relationships, and follow-ups. No database needed — just files.

## Features

- **Markdown-based** — Human-readable, git-friendly, portable
- **Query contacts** — Filter by tag, company, location, relationships
- **Track interactions** — Log meetings, calls, notes with timestamps
- **Follow-up reminders** — Never forget to reach out
- **Dormant detection** — Know who you haven't contacted in a while
- **Import/Export** — CSV, vCard, LinkedIn export support
- **Natural language** — Tell your AI about contacts conversationally
- **Heartbeat integration** — Periodic checks for due follow-ups

## Installation

```bash
# Clone into your Clawdbot skills folder
git clone https://github.com/xz-cn/clawdbot-crm-skill.git skills/crm

# Initialize contacts folder inside memory/ (for semantic search integration)
mkdir -p memory/contacts/{people,companies,events,_templates,scripts}
cp skills/crm/assets/templates/*.md memory/contacts/_templates/
cp skills/crm/scripts/*.py memory/contacts/scripts/

# Reindex memory to include contacts
clawdbot memory index
```

> **Why `memory/contacts/`?** Placing contacts inside `memory/` enables Clawdbot's semantic search (`memory_search`) to find contacts automatically. Ask "who knows about AI?" and it just works.

**Requirements:** Python 3.10+ with PyYAML (`apt install python3-yaml` or `pip install pyyaml`)

## Quick Start

### Add a contact
```bash
python memory/contacts/scripts/crm-add.py person "Alice Chen" \
  --company "Acme Corp" \
  --role "CEO" \
  --email "alice@acme.com" \
  --tags "investor,crypto"
```

### Query contacts
```bash
python memory/contacts/scripts/crm-query.py --tag investor        # By tag
python memory/contacts/scripts/crm-query.py --company "Acme"      # By company
python memory/contacts/scripts/crm-query.py --location singapore  # By location
python memory/contacts/scripts/crm-query.py --search "supply chain"  # Full-text
```

### Log an interaction
```bash
python memory/contacts/scripts/crm-update.py alice-chen --interaction "Coffee meeting, discussed partnership"
```

### Check follow-ups
```bash
python memory/contacts/scripts/crm-followups.py --summary         # Quick overview
python memory/contacts/scripts/crm-followups.py --days 7          # Due this week
python memory/contacts/scripts/crm-followups.py --dormant 90      # Not contacted in 90 days
```

### Set reminders
```bash
python memory/contacts/scripts/crm-remind.py alice-chen --in 3d --message "Follow up on proposal"
python memory/contacts/scripts/crm-remind.py --list               # View pending
python memory/contacts/scripts/crm-remind.py --check              # Check due now
```

### Import/Export
```bash
python memory/contacts/scripts/crm-import.py contacts.csv         # Import CSV
python memory/contacts/scripts/crm-import.py contacts.vcf         # Import vCard
python memory/contacts/scripts/crm-export.py --csv backup.csv     # Export to CSV
python memory/contacts/scripts/crm-export.py --vcard contacts.vcf # Export to vCard
```

## Contact Schema

```yaml
---
name: Alice Chen
type: person
tags: [investor, crypto, singapore]
company: Acme Corp
role: CEO
email: alice@acme.com
telegram: "@alice"
location: Singapore
introduced_by: bob-smith
met_at: token2049-2025
first_contact: 2025-09-20
last_contact: 2026-01-27
follow_up: 2026-02-15
status: active
---

# Alice Chen

## Context
CEO of Acme Corp. Met through Bob at Token2049.

## Interactions
- **2026-01-27**: Coffee meeting, discussed partnership.
- **2025-09-20**: First met at conference.

## Notes
- Prefers Signal over email
- Early crypto investor
```

## Folder Structure

```
memory/
└── contacts/             # Inside memory/ for semantic search
    ├── people/           # One file per person
    │   ├── alice-chen.md
    │   └── bob-smith.md
    ├── companies/        # One file per company
    │   └── acme-corp.md
    ├── events/           # One file per event
    │   └── token2049-2025.md
    ├── _templates/       # Templates for new contacts
    ├── _index.md         # Auto-generated lookup
    └── scripts/          # CLI tools
```

## Natural Language Input

When using with Clawdbot, just describe contacts naturally:

> "Met Sarah Lee at the Web3 summit. She's head of partnerships at Polygon, based in Dubai. Got her on Telegram @sarahlee"

The AI extracts structured data and creates the contact file automatically.

## Heartbeat Integration

Add to your `HEARTBEAT.md`:

```markdown
### CRM Follow-ups (check 1-2x daily)
1. Run: `python memory/contacts/scripts/crm-followups.py --summary`
2. Run: `python memory/contacts/scripts/crm-remind.py --check`
If there are due items, notify the user.
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `crm-query.py` | Search and filter contacts |
| `crm-add.py` | Add new contacts |
| `crm-update.py` | Update contacts, log interactions |
| `crm-index.py` | Regenerate the index file |
| `crm-followups.py` | Check due follow-ups and dormant contacts |
| `crm-remind.py` | Manage reminders |
| `crm-import.py` | Import from CSV/vCard |
| `crm-export.py` | Export to CSV/vCard/Markdown |

## Verification

This skill is cryptographically signed using [ATP](https://github.com/zCloak-Network/ATP) Kind 11 (Document Signature).

| Field | Value |
|-------|-------|
| **Signer** | `alfred#6765.agent` |
| **Signature Event** | `23133cacd7db1e1270f9605b29933d012d34b7eca335b2120b7221eecfbea000` |
| **Canister** | `jayj5-xyaaa-aaaam-qfinq-cai` (ICP mainnet) |

> **Note:** The signature covers `MANIFEST.sha256` (which hashes all other files). This README references the event ID for convenience but is not itself part of the signed content — re-generate and verify the manifest to confirm integrity.

**To verify:**
```bash
# 1. Check all files match the manifest
sha256sum -c MANIFEST.sha256

# 2. Get the manifest hash and compare with the on-chain event
sha256sum MANIFEST.sha256

# 3. Look up the signature event on-chain
dfx canister call jayj5-xyaaa-aaaam-qfinq-cai fetch_events_by_counter '(97, 98)' --ic
```

## License

MIT — Use freely, contributions welcome!

---

Built with 🎩 by [Alfred](https://github.com/xz-cn) for [Clawdbot](https://clawdbot.com)
