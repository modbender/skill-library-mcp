# BOOK BRAIN VISUAL READER – Examples

## 1. Example Tree for a Visual-Aware Haven

```text
workspace/
├── memory/
│   ├── 2026-02-10.md
│   └── projects/
│       └── BOOK_BRAIN_VISUAL_NOTES.md
├── reference/
│   ├── INDEX.txt
│   ├── VISUAL_INDEX.txt
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
│   └── book_brain_visual_setup.log
├── visual/
│   ├── screenshots/
│   │   ├── 2026-02-10_starcore_clanker.png
│   │   └── 2026-02-10_moltx_profile.png
│   ├── dashboards/
│   └── seals/
├── tools/
│   └── …
└── tmp/
    └── scratch_notes.txt
```

BOOK BRAIN VISUAL READER should **create** `visual/` + `reference/VISUAL_INDEX.txt` if they are missing, but never delete or rename existing paths.

---

## 2. Example VISUAL_INDEX.txt

`reference/VISUAL_INDEX.txt`:

```text
Title: Visual Index
Last updated: 2026-02-10

[STARCORE]
- 2026-02-10_starcore_clanker.png
  - Path: visual/screenshots/2026-02-10_starcore_clanker.png
  - Related receipts:
    - reference/STARCORE_LAUNCH_RECEIPTS_2026-02-10.md
    - state/starcore_family_receipts_summary.json

[MOLTX]
- 2026-02-10_moltx_profile.png
  - Path: visual/screenshots/2026-02-10_moltx_profile.png
  - Context: profile snapshot after Champion Hub promo.

[LYGO]
- (add more as needed)
```

---

## 3. Example LEFT/RIGHT Check Log Entry

In `daily_health.md` or `logs/book_brain_visual_setup.log`:

```text
[2026-02-10 16:00] Visual check – STARCORE dashboards
- LEFT brain expectation:
  - Contract: 0xe52A34D2019Aa3905B1C1bF5d9405e22Abd75eaB
  - Tokens: STARCORE / STARCOREX / STARCORECOIN
- RIGHT brain observation:
  - Clanker, Blockscout, and Dexscreener dashboards match contract + ticker.
  - No red banners or obvious anomalies.
- Visual evidence:
  - visual/screenshots/2026-02-10_starcore_clanker.png

Conclusion: UI matches receipts; no action needed.
```

If there was a mismatch, the log would record **what** differed and **which source** is considered canonical (usually on-chain / API).

---

## 4. Example Reference Stub with Visual Note

`reference/STARCORE_VISUALS.txt`:

```text
Title: STARCORE Visual Artifacts
Last updated: 2026-02-10

Screenshots:
- visual/screenshots/2026-02-10_starcore_clanker.png
  - Verified Clanker dashboard.
- visual/screenshots/2026-02-10_moltx_profile.png
  - Profile & banner after Champion Hub promo.

See also:
- reference/STARCORE_LAUNCH_RECEIPTS_2026-02-10.md
- state/starcore_family_receipts_summary.json
```

This keeps visual artifacts discoverable without flooding daily memory files with image details.

---

## 5. Example memory_index.json (extended)

```json
{
  "topics": {
    "champions": [
      "reference/LYGO_CHAMPIONS_OVERVIEW.md",
      "reference/CLAWDHUB_SKILLS.md"
    ],
    "starcore": [
      "reference/STARCORE_LAUNCH_RECEIPTS_2026-02-10.md",
      "state/starcore_family_receipts_summary.json",
      "reference/STARCORE_VISUALS.txt"
    ],
    "book_brain_visual": [
      "skills/public/book-brain-visual-reader/SKILL.md",
      "skills/public/book-brain-visual-reader/references/book-brain-visual-examples.md"
    ]
  }
}
```

Agents should **update** topics when they add important files; perfection is optional, discoverability is the goal.
