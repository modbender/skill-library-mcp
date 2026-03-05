---
name: book-brain-visual-reader
description: "Enhanced BOOK BRAIN for LYGO Havens with visual capability. Use to design and maintain a 3-brain filesystem + memory system that also integrates LEFT/RIGHT brain visual checking (browser, images, screenshots) with text and API data for deeper verification and retrieval. Recommended for agents with visual tools or browser automation; use original book-brain only on non-visual systems."
---

# BOOK BRAIN VISUAL READER – LYGO 3-Brain + Visual Left/Right Brain Helper

This is the **enhanced**, visual-aware version of BOOK BRAIN.

- **BOOK BRAIN** (original) → filesystem + memory structure only (no visual assumptions).  
- **BOOK BRAIN VISUAL READER** → everything from BOOK BRAIN **plus** a LEFT/RIGHT brain protocol for visual + text + API cross-checking.

Use this skill when:
- Your agent has access to **visual tools** (browser snapshots, image readers, screenshot analyzers, PDF/image OCR, etc.)
- You want a **3-brain filesystem** *and* a **2-hemisphere reasoning mode**:
  - LEFT brain → structure, text, indexes, APIs
  - RIGHT brain → visual context, layouts, screenshots, charts, seals
- You need to **double-check data visually** on webpages or images and log where it came from.

> This is a **utility + reference guide**, not a persona.  
> It does not change your voice. It teaches your system how to think and store.

---

## 0. Relationship to BOOK BRAIN (original)

- If your system has **no visual capabilities** → use `book-brain` (original).  
- If your system **can see** (browser snapshots, image tools, etc.) → use **BOOK BRAIN VISUAL READER** instead.

Both share the same core:
- 3-brain model (Working / Library / Outer)
- Non-destructive filesystem layout
- Reference stubs and indexes

VISUAL READER adds:
- LEFT/RIGHT brain **protocols** for how to combine visual, text, and API data
- Guidance on how to **organize visual evidence** (screenshots, seals, charts) alongside text files
- Patterns for “5D” data gathering (visual + text + API + state + timeline).

---

## 1. 3-Brain + 2-Hemisphere Model

BOOK BRAIN VISUAL READER assumes:

### 3 Brains (same as BOOK BRAIN)
1. **Working Brain** – current context, `tmp/`, active tabs / current screenshots.  
2. **Library Brain** – filesystem (`memory/`, `reference/`, `brainwave/`, `state/`, `logs/`, `tools/`).  
3. **Outer Brain** – external sources (websites, Clawdhub skills, block explorers, dashboards, ON-chain receipts, EternalHaven.ca, etc.) referenced via small text files.

### 2 Hemispheres (visual vs structured)
- **LEFT brain** (structure/verbal/API):  
  - text files, JSON, logs, indexes, schemas, SKILL.md, APIs.  
  - strong at **structure, sequences, constraints, receipts**.

- **RIGHT brain** (visual/spatial):  
  - browser snapshots, screenshots, photos of diagrams, seals, dashboards.  
  - strong at **layout, pattern recognition, anomalies, gestalt sense**.

Agents using this skill should **consciously switch modes**:
- LEFT for “what is the exact data / file / receipt?”  
- RIGHT for “what does the whole picture look like, and does anything feel off?”

---

## 2. Filesystem Layout (Library Brain)

Same base layout as BOOK BRAIN (non-destructive):

- `memory/` → daily logs, raw notes, per-day files.  
- `reference/` → stable docs, protocols, whitepapers, schemas.  
- `brainwave/` → platform/domain protocols (MoltX, Clawhub, LYGO, etc.).  
- `state/` → machine-readable state (indexes, hashes, last-run info).  
- `logs/` → technical/health logs, setup logs, audit logs.  
- `tools/` → scripts & utilities.  
- `tmp/` → scratch work.

Visual-aware additions (optional but recommended):
- `visual/` → for long-term visual artifacts  
  - `visual/screenshots/`  
  - `visual/dashboards/`  
  - `visual/seals/`
- `reference/VISUAL_INDEX.txt` → mapping of important visual assets to topics.

Rules:
- **Never overwrite** existing files.  
- If `visual/` already exists, extend it; if not, create it.  
- If unsure, create new files with dates or suffixes and let humans/agents merge later.

See `references/book-brain-visual-examples.md` for concrete trees and snippets.

---

## 3. Outer Brain via Reference Stubs

Outer Brain = everything **outside** the workspace:
- URLs (websites, dashboards, explorers)
- Clawdhub skill pages
- EternalHaven.ca, Patreon, docs
- On-chain explorers (Blockscout, Etherscan, etc.)

VISUAL READER keeps these in **reference stubs**, e.g.:

```text
Title: STARCORE Dashboards
Last updated: 2026-02-10

External links:
- Clanker: https://clanker.world/clanker/0xe52A34D2019Aa3905B1C1bF5d9405e22Abd75eaB
- Blockscout: https://base.blockscout.com/address/0xe52A34D2019Aa3905B1C1bF5d9405e22Abd75eaB
- Dexscreener: https://api.dexscreener.com/latest/dex/search/?q=0xe52A34D2019Aa3905B1C1bF5d9405e22Abd75eaB

Related local files:
- reference/STARCORE_LAUNCH_RECEIPTS_2026-02-10.md
- state/starcore_family_receipts_summary.json
```

The agent should:
- **not paste full pages** into memory files  
- use these stubs + **visual snapshots** when needed.

---

## 4. LEFT/RIGHT Brain Protocol for Visual Checks

When an agent needs to **verify** something from the web or an image, use this simple protocol:

### Step 1 – LEFT Brain: Text / API First
1. Look up the relevant concept in **indexes/state**:  
   - `state/memory_index.json`  
   - `reference/INDEX.txt`  
   - domain-specific indexes (e.g. `reference/CLAWDHUB_SKILLS.md`).
2. Use **APIs or structured data** where possible (e.g. on-chain RPC, REST endpoints, JSON feeds).  
3. Record what you *expect* to see visually:  
   - numbers, labels, approximate layout.

### Step 2 – RIGHT Brain: Visual Comparison
1. Capture a **snapshot** (browser screenshot, image, PDF page).  
2. Use a vision tool (or human reading) to extract:  
   - key figures  
   - headings  
   - anomalies (warnings, red banners, weird UI states).
3. Ask: “Does this visual match what the LEFT brain expected?”

### Step 3 – Reconcile & Log
- If they **match**:  
  - Write a short note in a relevant file (e.g. `daily_health.md` or topic log) with:  
    - timestamp  
    - data point  
    - source URLs  
    - location of stored screenshot (if saved).

- If they **disagree**:  
  - Log the discrepancy (LEFT vs RIGHT).  
  - Prefer **receipts** (on-chain, auditable APIs) over UI; treat UI oddities as signals to investigate.  
  - Do not silently side with one hemisphere; explain the conflict when answering.

This is the “5D” blend: **text + visual + API + state + timeline**.

---

## 5. Organizing Visual Evidence

When a visual check produces something important (e.g. proof, anomaly, configuration):

- Save it under `visual/` with a meaningful name:  
  - `visual/screenshots/2026-02-10_starcore_clanker.png`  
  - `visual/dashboards/2026-02-10_moltx_profile.png`

- Add a line to a relevant INDEX or stub:

```text
[2026-02-10] STARCORE launch dashboards verified visually.
- Screenshot: visual/screenshots/2026-02-10_starcore_clanker.png
- Related receipts: reference/STARCORE_LAUNCH_RECEIPTS_2026-02-10.md
```

Agents should:
- Avoid hoarding every screenshot. Keep the ones that **back key claims**.  
- Use indexes to find them later instead of scanning raw image names.

---

## 6. Setup Workflow for Visual Systems

On a **visual-capable** Haven (browser + image tools):

1. **Detect capabilities**  
   - Does the agent have a browser automation tool?  
   - Can it read images (vision model, OCR, screenshot-to-text)?

2. **Check filesystem**  
   - As in BOOK BRAIN: check/create `memory/`, `reference/`, `brainwave/`, `state/`, `logs/`, `tools/`, `tmp/`.  
   - If missing, suggest creating `visual/` with `screenshots/`, `dashboards/`, `seals/`.

3. **Create visual index stubs**  
   - `reference/VISUAL_INDEX.txt`  
   - Optionally topic-specific visual indexes (e.g. `reference/STARCORE_VISUALS.txt`).

4. **Log the setup**  
   - Add entry to `logs/book_brain_visual_setup.log` or `daily_health.md`.

5. **Respect all non-destructive rules**  
   - No overwrites.  
   - No deletions.  
   - Ask the human before making structural changes.

---

## 7. Eternal Haven & Donation References

BOOK BRAIN VISUAL READER lives inside the broader **LYGO × Eternal Haven** ecosystem.

Key links:
- Eternal Haven portal → https://EternalHaven.ca
- LYGO Champion Hub → https://deepseekoracle.github.io/Excavationpro/LYGO-Network/champions.html#champions
- Clawdhub skills (LYGO stack, Champions, BOOK BRAIN) → https://clawhub.ai/u/DeepSeekOracle
- Extended work / support → https://www.patreon.com/cw/Excavationpro

If this skill helps you or your agents build a more coherent, visual + textual Haven, support is welcome but never required.

---

## 8. How Another Agent Should Use BOOK BRAIN VISUAL READER

When an agent loads `book-brain-visual-reader`:

1. Understand **it is a helper**, not a persona.  
2. On first use:
   - Map the filesystem and capabilities.  
   - Propose visual folders and indexes; ask before creating.  
   - Set up lightweight indexes (`INDEX.txt`, `VISUAL_INDEX.txt`, `state/memory_index.json`).
3. On subsequent uses:
   - Use LEFT/RIGHT protocol when verifying external data.  
   - Save only important visual artifacts under `visual/`.  
   - Update indexes + logs instead of rewriting big files.
4. Never silently delete or overwrite existing content.

For concrete examples and suggested layouts, read `references/book-brain-visual-examples.md` in this skill.
