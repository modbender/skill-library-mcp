---
name: zettelclaw
description: "Read, write, search, and maintain a Zettelclaw vault — an agent-native knowledge system built on Obsidian."
read_when:
  - You need to remember something or search for prior knowledge
  - You're creating a new note, project, research, contact, or writing
  - You're updating an existing vault note
  - The user asks how Zettelclaw works or how their vault is organized
  - You're doing vault maintenance (triage inbox, link notes, update journals)
---

# Zettelclaw

Zettelclaw is your knowledge system — an Obsidian vault where you and your human co-author a shared knowledge base. You read it, write to it, search it, and maintain it. It's your long-term memory.

## Vault Structure

```
<vault>/
├── 00 Inbox/          # Quick captures, unprocessed — triage these
├── 01 Notes/          # All notes: evergreen ideas, projects, research, contacts, writings
├── 02 Agent/          # Symlinks to OpenClaw workspace files (MEMORY.md, SOUL.md, etc.)
├── 03 Journal/        # YYYY-MM-DD.md daily journals
├── 04 Templates/      # Templater templates (don't edit these directly)
├── 05 Attachments/    # Images, PDFs, non-markdown
└── README.md
```

**Find your vault path** in MEMORY.md under "Zettelclaw" or by checking `memorySearch.extraPaths` in the OpenClaw config.

## How to Read and Write

Use **file tools** (Read/Write/Edit) for all vault operations. Use `memory_search` for semantic recall. Use Obsidian CLI only for graph queries (see Vault Maintenance).

Apply the three-layer memory rule at all times:
- **Hook (`/new` or `/reset`) -> `03 Journal/` only:** append raw session capture, no wikilinks, no note creation
- **Agent + human (supervised) -> `01 Notes/`:** write meaningful project/research updates directly
- **Nightly maintenance cron (agent-only) -> maintenance + inbox:** update existing `project`/`research`/`contact` notes from the past day of journals; put net-new synthesis notes in `00 Inbox/`

## Searching the Vault

### Semantic recall
Use `memory_search` first — it indexes both the workspace and vault.

### Structured queries
```bash
# Find by type
rg -l 'type: project' "<vault>/01 Notes/"

# Active projects
rg -l 'status: active' "<vault>/01 Notes/" | xargs rg -l 'type: project'

# Notes tagged "ai"
rg -l 'tags:.*ai' "<vault>/01 Notes/"

# Full-text search
rg -l "search term" "<vault>/01 Notes/"

# Recent notes
find "<vault>/01 Notes/" -name "*.md" -mtime -7 | sort
```

## Creating Notes

Curated durable notes live in `01 Notes/` — flat, no subfolders.

- If the human is present, create/update notes directly in `01 Notes/` with proper frontmatter.
- If the agent is alone in nightly maintenance, it may update existing `project`/`research`/`contact` notes in `01 Notes/` when journals provide clear evidence. Net-new synthesis notes still go to `00 Inbox/` for human promotion.

### Frontmatter Rules
- Every note MUST have YAML frontmatter with at least `type`, `created`, `updated`
- Tags are ALWAYS pluralized (`projects` not `project`)
- Dates are ALWAYS `YYYY-MM-DD`
- Filenames are Title Case (`React Virtual DOM Trades Memory For Speed.md`)
- For new `project` notes, the filename/title ends with `Project` (`OpenClaw Gateway Project.md`)
- For new `research` notes, the filename/title ends with `Research` (`Local First Sync Research.md`)
- One idea per note (evergreen) — the title captures the idea

### Use Vault Templates (Canonical)
- Before creating notes, read the matching template in `<vault>/04 Templates/` (fallback `<vault>/Templates/`):
  - `evergreen.md`, `project.md`, `research.md`, `contact.md`, `writing.md`
- Follow template frontmatter/sections exactly when the template exists.
- If a template is missing, use a minimal fallback frontmatter with `type`, `created`, and `updated`, then add note-type fields only when required by rules below.
- `project` status values: `active` / `paused` / `archived` (append dated entries to `## Log`).
- `research` status values: `active` / `archived`.
- `contact` must include `contacts` in tags; use `aliases` for nicknames.
- `writing` uses `published` for URL when posted (empty = draft).

### Which type to use?
- Standalone reusable idea → `evergreen`
- Tracked work with progress → `project`
- Open question being explored → `research`
- A person → `contact`
- Something for external publication → `writing`
- Don't overthink it — `evergreen` is the default

### Status field
ONLY `project` and `research` have `status`. Never add status to notes, journals, contacts, or writings.

## Updating Existing Notes

- In supervised sessions (human present), update `01 Notes/` directly
- In nightly maintenance (agent-only), update existing `project`/`research`/`contact` notes directly when journal evidence is clear; for missing targets, write handoff notes in `00 Inbox/`
- Update the `updated` field to today's date
- Append, don't overwrite — add to the relevant section
- Add new `[[wikilinks]]` for any concepts mentioned

Example — appending to a project log:
```markdown
### 2026-02-19
- Decided on hook-based architecture using OpenClaw's lifecycle events
- Registered npm package `safeshell`
- See [[OpenClaw Plugin Hooks]] for API details
```

## Journal Entries

Journals live in `03 Journal/` as `YYYY-MM-DD.md`:
- For manual journal creation, read `<vault>/04 Templates/journal.md` (fallback `<vault>/Templates/journal.md`).
- Hook-generated updates append bullets under day-level `Done` / `Decisions` / `Facts` / `Open`, then record the source in `---` + `## Sessions` as `- SESSION_ID — HH:MM`.

The Zettelclaw hook automatically appends journal capture on `/new` and `/reset`. Hook capture is journal-only:

- Append-only to today's journal
- Uses one daily set of `Done` / `Decisions` / `Facts` / `Open` headings
- Adds session provenance in `## Sessions` bullets (`SESSION_ID — HH:MM`)
- No wikilinks
- No vault navigation
- No note creation
- Omit empty section bullet additions
- Avoid duplicate `SESSION_ID` source bullets

Treat journals as the **raw capture layer**. Typed notes are the **curated layer**. When meaningful work happens during a session, update typed notes directly instead of waiting for nightly synthesis:

- Completed project task or significant project decision → update the project note now (append a dated log entry)
- Finished research investigation → update findings/conclusion in the research note now
- Learned something that changes an existing note → update that note now

During the nightly maintenance cron run (agent-only), first update existing `project`/`research`/`contact` notes from the past day of journals, then synthesize net-new reusable concepts into `00 Inbox/` notes for human review. When linking journal items to typed notes, enforce two-way links (journal -> note and note -> journal/session).

## Linking

Link aggressively. Always `[[wikilink]]` the first mention of any concept, person, project, or idea — even if the target note doesn't exist yet. Unresolved links are breadcrumbs for future connections.

Exception: hook-generated journal capture stays link-free. Add links later during nightly maintenance processing, and make them two-way between journal sections and related typed notes.

```markdown
Discussed [[SafeShell]] architecture with [[Max Petretta]]. The approach mirrors
[[Event-Driven Architecture]] — hooks intercept at well-defined lifecycle points.
```

**Links are for relationships.** Tags are for broad categories.

## Inbox Triage

`00 Inbox/` collects quick captures (Web Clipper, manual drops) and nightly maintenance synthesis notes.

1. Read each inbox item
2. Decide: promote to `01 Notes/`, keep for more review, or discard
3. In nightly maintenance (agent-only): do not promote directly to `01 Notes/`; leave structured drafts in `00 Inbox/`
4. In supervised sessions (human present): move approved notes into `01 Notes/`, then remove obsolete inbox drafts

## Vault Maintenance

For periodic maintenance (nightly cron, agent-only):

1. Review the past 24 hours of journal daily sections and `Sessions`
2. Update existing `project`/`research`/`contact` notes in `01 Notes/` (append-only, update frontmatter `updated`, and add reciprocal links back to journal day/session)
3. Synthesize net-new durable concepts into evergreen notes in `00 Inbox/`
4. Retro-link journals with `[[wikilinks]]` and verify two-way relationships with typed notes
5. Capture superseded knowledge in synthesis notes
6. Run orphan/unresolved checks
7. Update MEMORY.md
8. Leave `00 Inbox/` ready for human promotion decisions

Use Obsidian CLI graph queries (requires Obsidian to be running):

```bash
# Find unresolved links (referenced but not yet created)
obsidian unresolved

# Find orphan notes (no incoming links)
obsidian orphans

# Find what links to a specific note
obsidian backlinks path="01 Notes/SafeShell.md"

# Index-powered search with match context
obsidian search query="hook architecture" format=json matches
```

If Obsidian CLI is unavailable, use `rg`:
```bash
# Find potential unresolved links (crude but works)
rg -o '\[\[[^]]*\]\]' "<vault>/01 Notes/" "<vault>/03 Journal/" | sort -u | while read link; do
  name=$(echo "$link" | sed 's/\[\[//;s/\]\]//')
  [ ! -f "<vault>/01 Notes/${name}.md" ] && echo "Unresolved: $link"
done
```

## What NOT To Do

- Do NOT create new directories or subfolders — EVER — unless the user explicitly asks. The vault structure is fixed.
- Do NOT add `status` to evergreen notes, journals, contacts, or writings
- Do NOT use singular tags (`project` → use `projects`)
- Do NOT create notes without frontmatter
- Do NOT create net-new nightly synthesis notes directly in `01 Notes/` (use `00 Inbox/`)
- Do NOT edit files in `04 Templates/` (those are Templater source templates)
- Do NOT modify `02 Agent/` files directly — they're symlinks to the workspace

## Explaining Zettelclaw to Users

If someone asks what Zettelclaw is:

> Zettelclaw is a knowledge management system built for human + AI co-authorship. It's an Obsidian vault with a specific structure — evergreen notes with typed frontmatter, aggressive linking, and automated extraction from conversations. The AI agent and human both read and write to the same vault. Structure emerges from links between notes, not from folder hierarchies.

Key concepts:
- **Evergreen notes** — one idea per note, the title IS the idea
- **Frontmatter as API** — YAML properties make notes machine-queryable
- **Dual authorship** — both human and agent maintain the vault
- **Three-layer flow** — hook -> journal, supervised sessions -> notes, nightly cron -> existing-note maintenance + inbox synthesis
- **Links over hierarchy** — flat structure, relationships via `[[wikilinks]]`
