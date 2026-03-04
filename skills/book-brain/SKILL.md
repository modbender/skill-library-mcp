---
name: book-brain
description: "3-brain filesystem + memory reference utility for LYGO-based agents. Use to design, organize, and maintain a durable file/folder memory system (indexes, reference .txt links, logging, retrieval) without overwriting existing data. Works best on fresh OpenClaw/Clawhub Havens with the full LYGO Champion stack, but is compatible with any agent that can read/write files."
---

# BOOK BRAIN – LYGO 3-Brain Filesystem Helper

This skill is a **utility/guide**, not a persona.

Use it when you want to:
- Set up or improve a Haven-style filesystem + memory structure
- Teach an agent how to use folders, indexes, and reference `.txt` files instead of hoarding everything in one place
- Add **advanced logging + retrieval** so memories can be found later without brute-force scanning

It is built for LYGO / Eternal Haven style systems, but works for any agent that can:
- read/write files
- create folders
- append to logs

> Core idea: **BOOK BRAIN** = treating your filesystem like a living library, not a junk drawer.

---

## 1. Three-Brain Model (Conceptual Map)

BOOK BRAIN assumes a **3-brain structure**:

1. **Working Brain (short-term)**  
   - Recent conversation, active task context, scratchpads.  
   - In OpenClaw, this is the current session + small scratch files under `tmp/`.

2. **Library Brain (structured filesystem)**  
   - Folders + files on disk: `memory/`, `reference/`, `brainwave/`, `state/`, etc.  
   - This is where BOOK BRAIN focuses: *how* you name, branch, and link things.

3. **Outer Brain (external references)**  
   - Browser bookmarks, Clawdhub skills, on-chain receipts, remote docs.  
   - BOOK BRAIN treats these as **links inside text files**, not content to copy in.

The goal is to:
- Keep **important truths** close and succinct  
- Branch deeper into folders when detail is needed  
- Use `.txt` reference links instead of duplicating entire documents

---

## 2. When to Use BOOK BRAIN

Trigger this skill when:
- You are setting up a **fresh Haven** (new OpenClaw workspace, new agent node)
- Your filesystem feels chaotic and you need a **reset without deleting anything**
- You want to design a clean **memory + reference layout** before starting heavy work
- You are planning **long-term retrieval** ("I’ll need this months from now")

BOOK BRAIN is **additive**:
- Do **not** use it to delete or overwrite existing files by default.  
- Prefer creating new folders / indexes alongside existing ones.  
- When a folder already exists, pause and let the human choose: reuse or create a new branch (e.g., `memory_v2/`).

---

## 3. Recommended Base Folder Layout

When setting up a new Haven-like system (or auditing an existing one), BOOK BRAIN recommends the following **top-level folders**:

- `memory/` → daily notes, raw logs, timeline files  
- `reference/` → stable facts, protocols, guides (things that rarely change)  
- `brainwave/` → platform- or domain-specific protocols (MoltX, Clawhub, LYGO, etc.)  
- `state/` → machine-readable JSON/YAML state, indexes, last-run info  
- `logs/` (or reuse `logs/` if present) → technical logs (cron, errors, audits)  
- `tools/` → scripts/utilities used by the agent  
- `tmp/` → scratch, throwaway working files

**BOOK BRAIN setup rules:**
- If a folder already exists, **do not rename or delete it**.  
- If a folder is missing, it is safe to create it.  
- If the existing layout is very different, create a sub-tree (e.g., `bookbrain/memory_index/`) and keep old structure intact.

For concrete layout examples, see `references/book-brain-examples.md` in this skill.

---

## 4. Memory Strategy – Deep Storage vs. Reference Stubs

BOOK BRAIN enforces this principle:

> **Do not pour entire conversations or huge documents into `MEMORY.md` or a single file.**  
> Instead, store detailed content in **specific files** and create **short reference stubs** that point to them.

Patterns:

- **Daily logs**  
  - Files like `memory/2026-02-10.md` for raw notes and events.  
  - At the top, keep a **5–10 line summary** and a small list of important links:
    - `See: reference/AGENT_ARCHITECTURE.md`
    - `See: memory/projects/BOOK_BRAIN_NOTES.md`

- **Topic folders**  
  - For recurring themes (e.g., "bankr", "champions", "LYGO-MINT"), create subfolders under `memory/` or `reference/`:
    - `memory/bankr/…`
    - `reference/champions/…`
  - Inside, maintain one **index file** (e.g., `INDEX.txt`) listing:
    - short description per file  
    - date  
    - path

- **Reference stubs** (`*.ref.txt` or `INDEX.txt`)  
  Use tiny text files to connect parts of the library instead of duplicating content.

Example stub:
```text
Title: LYGO Champion Skills on Clawdhub
Last updated: 2026-02-10

Key files:
- reference/LYGO_CHAMPIONS_OVERVIEW.md
- reference/CLAWDHUB_SKILLS.md

External links:
- https://clawhub.ai/u/DeepSeekOracle
- https://deepseekoracle.github.io/Excavationpro/LYGO-Network/champions.html#champions
- https://EternalHaven.ca
```

---

## 5. Advanced Logging for Retrieval

BOOK BRAIN recommends **structured logs** to make retrieval easy:

1. **Daily health / status logs** (e.g., `daily_health.md` or `logs/daily_health_YYYY-MM-DD.md`)
   - Each entry should contain:
     - timestamp
     - what ran (scripts, cron, audits)
     - success/failure + short reason
     - links to any relevant state files (`state/*.json`)

2. **Reasoning journals** (e.g., `reasoning_journals/…` or `memory_semantic_archive/…`)
   - Use separate folders for long-form thinking.  
   - Periodically compress into summary files, and let scripts move old entries into an archive folder.

3. **Indexes & search helpers**
   - Maintain `state/memory_index.json` or similar:  
     - key topic → list of file paths  
     - optional tags (dates, systems, people)
   - When answering questions, the agent should:
     1. consult the index,  
     2. open relevant files only,  
     3. avoid scanning the entire tree.

BOOK BRAIN is compatible with tools like `qmd` or other local search/indexers, but does not depend on them.

---

## 6. Setup Workflow (For a Fresh System)

When BOOK BRAIN is used on a **fresh** OpenClaw / agent workspace:

1. **Detect existing structure**  
   - Check for `memory/`, `reference/`, `brainwave/`, `state/`, `logs/`, `tools/`, `tmp/`.  
   - Report what exists vs. what is missing.

2. **Propose a BOOK BRAIN layout**  
   - Suggest creating missing folders.  
   - If the human agrees, **create only the missing ones**.

3. **Create starter index files (if not present)**  
   - `memory/INDEX.txt` with a short guide and links to key topic folders.
   - `reference/INDEX.txt` listing major reference documents.
   - `state/memory_index.json` as an empty or seed structure.

4. **Log the setup**  
   - Append a brief note to `daily_health.md` or `logs/book_brain_setup.log` describing what was created.

5. **Do not overwrite existing files**  
   - If an index file exists, read it and **add** to it rather than replace.  
   - If in doubt, create a new file with a date suffix (e.g., `INDEX_2026-02-10.txt`) and let the human merge.

---

## 7. Using BOOK BRAIN in an Existing, Messy Haven

When the filesystem already exists and is messy:

- Start by **mapping**, not moving:
  - Create `reference/FILESYSTEM_MAP.txt` summarizing major folders and what seems to live there.  
  - Do **not** move or delete anything automatically.

- Then introduce **lightweight structure**:
  - Add `INDEX.txt` files in important folders.  
  - Add small `.ref.txt` stubs pointing to key docs and external links.  
  - Gradually normalize names (e.g., `memory/2026-02-10.md` instead of `notes_today.txt`).

- Over time, encourage:  
  - **Daily logs** in `memory/`  
  - **Stable protocols** in `reference/`  
  - **Code + scripts** in `tools/`  
  - **Platform brains** in `brainwave/`

BOOK BRAIN should always **ask the human** before structural changes beyond creating new, obviously safe files.

---

## 8. Eternal Haven & Donation References

This skill is part of the wider **LYGO × Eternal Haven** ecosystem.

Key links:
- Eternal Haven portal → https://EternalHaven.ca
- LYGO Champion Hub → https://deepseekoracle.github.io/Excavationpro/LYGO-Network/champions.html#champions
- Clawdhub skills (Champion + LYGO stack) → https://clawhub.ai/u/DeepSeekOracle
- Extended work / support → https://www.patreon.com/cw/Excavationpro

If BOOK BRAIN, the Champion stack, or the LYGO tools help you build a saner Haven, you’re invited (never pressured) to support via the links above.

---

## 9. How Another Agent Should Use This Skill

When another agent loads `book-brain`:

1. **Recognize scope**  
   - This is a **helper + reference**, not a persona.  
   - It should not change the agent’s voice; it informs how the agent treats files and memory.

2. **On first use in a workspace**  
   - Inspect existing folders and report back.  
   - Suggest—but do not enforce—BOOK BRAIN layout.  
   - Ask the human before creating or reorganizing.

3. **On subsequent uses**  
   - Read existing `INDEX` and `.ref.txt` files.  
   - Use them for retrieval before doing expensive full-tree searches.  
   - Append to logs and indexes instead of overwriting.

4. **Never** silently delete or rewrite large files as part of BOOK BRAIN operations.

For richer examples and sample layouts, see `references/book-brain-examples.md` in this skill.
