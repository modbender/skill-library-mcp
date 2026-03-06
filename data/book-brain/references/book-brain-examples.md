# BOOK BRAIN Examples & Patterns

This file provides concrete examples for the BOOK BRAIN skill.

## 1. Example Folder Tree (Fresh Haven)

```text
workspace/
├── memory/
│   ├── 2026-02-10.md
│   ├── 2026-02-11.md
│   └── projects/
│       ├── BOOK_BRAIN_NOTES.md
│       └── bankr/
│           ├── INDEX.txt
│           └── 2026-02-10_bankr_brainstorm.md
├── reference/
│   ├── INDEX.txt
│   ├── LYGO_CHAMPIONS_OVERVIEW.md
│   ├── FILESYSTEM_GUIDE.md
│   └── CLAWDHUB_SKILLS.md
├── brainwave/
│   ├── MOLTX/
│   ├── CLAWHUB/
│   └── LYGO_CORE/
├── state/
│   ├── memory_index.json
│   └── starcore_family_receipts_summary.json
├── logs/
│   ├── daily_health.md
│   └── book_brain_setup.log
├── tools/
│   ├── daily_coin_bankr_check.py
│   └── qmd_search_helper.py
└── tmp/
    └── scratch_notes.txt
```

BOOK BRAIN should **add** missing folders (e.g., `reference/`, `state/`) but never delete or rename existing ones.

---

## 2. Example Daily Memory File

`memory/2026-02-10.md`:

```markdown
# 2026-02-10 – Daily Log

## Summary (5–10 lines)
- STARCORE monitor run; receipts normalized and dashboards bookmarked.
- Champions validated on Clawdhub; ~100 installs reported.
- Moltx posts: Eternal Haven Chronicle, LYGO Champion Hub promo.
- Decided to adopt BOOK BRAIN structure for long-term memory.

## Important links
- Champion Hub: https://deepseekoracle.github.io/Excavationpro/LYGO-Network/champions.html#champions
- Clawdhub skills: https://clawhub.ai/u/DeepSeekOracle
- Eternal Haven: https://EternalHaven.ca

## Raw notes
- …free-form text here…
```

The **Summary** + **Important links** are what future-you will use most often.

---

## 3. Example Topic Index

`memory/bankr/INDEX.txt`:

```text
Title: BANKR – Memory Index
Last updated: 2026-02-10

Overview:
This folder holds all notes about Bankr integration, strategies, and receipts.

Files:
- 2026-02-10_bankr_brainstorm.md – initial idea dump
- 2026-02-12_bankr_risk_model.md – draft risk model

External references:
- reference/BANKR_PROTOCOL.md
- reference/BANKR_INTEGRATION_WHITEPAPER_V0.md

Search tips:
- For high-level protocol, open BANKR_PROTOCOL.md.
- For timeline of decisions, scan daily memory files and search for "BANKR".
```

---

## 4. Example Reference Stub

`reference/CLAWDHUB_SKILLS.md`:

```markdown
# Clawdhub Skills – LYGO Stack (Overview)

Main profile:
- https://clawhub.ai/u/DeepSeekOracle

Core infrastructure skills:
- LYGO Guardian P0 Stack
- Eternal Haven Lore Pack
- OpenClaw Flow Kit
- Recursive Generosity Protocol (Δ9-WP-003)

Memory / provenance:
- LYGO-MINT Verifier
- LYGO-MINT Operator Suite (v2)
- LYGO Universal Living Memory Library (v1.1)
- LYGO Universal Cure System

Champion persona helpers:
- LYGO Branch: 401LYRAKIN — The Voice Between
- LYGO Branch: CRYPTOSOPHIA — Memetic Soulforger
- LYGO Root: VΩLARIS — Prism of Judgment
- LYGO Champion: OMNIΣIREN — Silent Storm
- LYGO Champion: SANCORA — Unified Minds
- LYGO Champion: ΣCENΔR (SCENAR) — Paradox Architect
- LYGO Champion: ÆTHERIS — Viral Truth
- LYGO Champion: KAIROS — Herald of Time
- LYGO Champion: ARKOS — Celestial Architect
- LYGO Champion: ΣRΛΘ (SRAITH) — Shadow Sentinel
- LYGO Champion: SEPHRAEL — Echo Walker
- LYGO Champion: Δ9RA (RA) — The Wolf
- LYGO Champion: LYRA (LYRΔ) — Star Core
- LYGO: Lightfather Vector — Δ9Quantum Accord

For details on each Champion, see:
- https://deepseekoracle.github.io/Excavationpro/LYGO-Network/champions.html#champions
```

---

## 5. Example state/memory_index.json (Conceptual)

```json
{
  "topics": {
    "champions": [
      "reference/LYGO_CHAMPIONS_OVERVIEW.md",
      "reference/CLAWDHUB_SKILLS.md"
    ],
    "starcore": [
      "reference/STARCORE_LAUNCH_RECEIPTS_2026-02-10.md",
      "state/starcore_family_receipts_summary.json"
    ],
    "book_brain": [
      "skills/public/book-brain/SKILL.md",
      "skills/public/book-brain/references/book-brain-examples.md"
    ]
  }
}
```

Agents using BOOK BRAIN should **update** this index when they create important new files, instead of trying to keep it perfect.

---

## 6. Example Setup Log Entry

`logs/book_brain_setup.log` (or appended to `daily_health.md`):

```text
[2026-02-10 15:40] BOOK BRAIN setup
- Created folders: reference/, state/, logs/ (memory/ already existed)
- Created files:
  - memory/INDEX.txt
  - reference/INDEX.txt
  - state/memory_index.json (empty template)
- No files overwritten.
```

This kind of log makes it easy to audit what BOOK BRAIN changed in the filesystem.
