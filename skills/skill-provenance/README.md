---
skill_bundle: skill-provenance
file_role: reference
version: 7
version_date: 2026-02-28
previous_version: 6
change_summary: >
  Added pi0/skillman and arxiv survey paper references to ecosystem
  and research sections.
---

# Skill Provenance — README

## What this is

A metaskill that prevents version confusion when skill projects move between
sessions, surfaces (Chat, IDE, CLI, Cowork), and platforms (Claude, Gemini
CLI, Codex, Copilot). It keeps version identity with the bundle, inside files
when practical and always in the manifest, tracks staleness across related
files, and maintains a manifest so any session can verify what it has.

You need this if you've ever uploaded a skill file to a new session and
couldn't tell whether it was the latest version, or discovered that the
SKILL.md was updated but the evals weren't, or lost track of what changed
between sessions.


## The .skill format

Claude's settings UI exports and imports skills as `.skill` files. These
are standard ZIP archives containing a directory with the skill's files.
Claude's importer only looks for `SKILL.md` and the expected directory
structure — it ignores files it doesn't recognize. This means versioning
artifacts live safely inside the ZIP:

```
my-skill.skill (ZIP)
└── my-skill/
    ├── SKILL.md
    ├── MANIFEST.yaml          ← versioning: file inventory
    ├── CHANGELOG.md           ← versioning: change history
    ├── README.md              ← versioning: human instructions
    ├── assets/
    │   └── template.md
    └── references/
        ├── guidelines.md
        ├── examples.md
        └── checklist.md
```

When you download a `.skill` from Claude settings, the versioning
artifacts come with it. When you upload one, they're preserved. No
separate file management needed for the core skill bundle.

**What doesn't fit in .skill:** Some skill projects include evals,
generation scripts, rendered outputs (.docx, .pdf), and handoff notes.
The `.skill` format only carries the skill definition and its references.
These extra files travel separately (uploaded to conversations, stored
in working directories, or committed to git). The manifest tracks all
files regardless — it's the complete inventory, not just the packaged
subset.


## Quick start

### 1. Make the skill available to Claude

The skill-provenance SKILL.md needs to be accessible in whatever Claude
surface you're working in. How you do that depends on the surface:

| Surface | How to load the skill |
|---|---|
| **Claude Chat** (no project) | Upload `SKILL.md` at the start of the conversation along with your bundle files. Reference it explicitly: "Use the skill-provenance skill to bootstrap this bundle." |
| **Claude Chat** (project) | Add `SKILL.md` to the project knowledge. It will be available in every conversation within that project. |
| **Claude Cowork** | Place the `skill-provenance/` folder in your Cowork skill directory. Claude will discover it automatically. |
| **Claude Code** | Place the `skill-provenance/` folder in your project's skill directory (typically alongside other skills). Reference it in your CLAUDE.md if needed. |
| **Gemini CLI** | Copy or symlink the `skill-provenance/` folder to `~/.gemini/skills/skill-provenance/` for user-wide availability, or `.gemini/skills/skill-provenance/` for a single project. Use `frontmatter_mode: minimal` in the manifest. |

The checked-in `skill-provenance/` directory is the canonical source bundle
and now ships in `frontmatter_mode: minimal`, so the same `SKILL.md` works
for Claude, Codex, and Gemini CLI. The `.skill` file is just a Claude-friendly
ZIP wrapper around that directory.

### Where to find and manage skills in Claude settings

**To view installed skills:**
`claude.ai` → Profile icon (bottom-left) → `Settings` → `Skills`

**To download an existing skill:**
`Settings` → `Skills` → click the skill name → `Download` (downloads as `.skill` ZIP)

**To upload/install a skill:**
`Settings` → `Skills` → `Add Skill` → select the `.skill` file

**To view a skill within a project:**
Open the project → `Project Settings` (gear icon) → `Skills` section

### 2. Bootstrap an existing skill bundle

Upload all the files that belong to your skill bundle (SKILL.md, evals,
scripts, outputs, handoff notes — everything) and tell Claude:

> "Bootstrap this skill bundle with skill-provenance. Call it [MAJOR.MINOR.PATCH]."

If you don't know the version number, just say "bootstrap this bundle"
and Claude will ask. Claude inventories the files itself — you don't
need to list them or count them.

Claude will:
- Inventory all files
- Add internal version headers where safe and record manifest-only versions
  for strict-format files
- Create `MANIFEST.yaml` (file inventory with roles and hashes)
- Create `CHANGELOG.md` (with a single entry summarizing known history)
- Return the updated bundle

### 3. Use it in ongoing work

Once a bundle is versioned, the protocol is automatic at session boundaries:

**Opening a session:** Upload the bundle files. Tell Claude to verify the
bundle. Claude reads the manifest, checks for missing or stale files,
and flags issues before you start working.

**During a session:** Work normally. The versioning system stays out of
your way until you're ready to save.

**Closing a session:** Tell Claude you're done. Claude updates internal
headers where applicable, the manifest, and the changelog for everything
that changed, flags anything stale, and packages the deliverables.


## Applying to an existing skill (worked example)

Say you have a skill called `weekly-newsletter` installed in Claude.
Here's how to apply versioning to it.

### Step 1: Download the skill

`claude.ai` → Profile icon → `Settings` → `Skills` → click
`weekly-newsletter` → `Download`

This gives you `weekly-newsletter.skill`, which is a ZIP containing:

```
weekly-newsletter/
├── SKILL.md
├── assets/
│   └── template.md
└── references/
    ├── guidelines.md
    ├── examples.md
    └── checklist.md
```

### Step 2: Unpack locally

The `.skill` extension is not recognized by macOS Finder or Archive
Utility, so double-clicking won't work. Use Terminal:

```bash
# Extract to a specific directory (recommended)
unzip ~/Desktop/weekly-newsletter.skill -d ~/Desktop/

# Without -d, files extract to your current working directory (~ by default),
# which can be confusing — always use -d to control the destination.
```

On Windows, rename `.skill` to `.zip` first, then extract normally:

```powershell
# PowerShell
Copy-Item weekly-newsletter.skill weekly-newsletter.zip
Expand-Archive weekly-newsletter.zip -DestinationPath ./newsletter-bundle
```

You now have the raw files in a working directory.

### Step 3: Bootstrap versioning in Claude

Open a new Claude Chat conversation (or use the project where the skill
lives). Upload:

- `skill-provenance/SKILL.md` (the versioning skill itself)
- All files from the extracted skill directory

Then say:

> "Bootstrap this skill bundle with skill-provenance. Call it 1.0.0."

Claude will inventory the files itself — you don't need to list them
or count them. If Claude needs clarification (version number, bundle
name, which files are references vs. assets), it will ask.

### Step 4: What Claude produces

Claude will:
- Add internal headers to frontmatter-friendly files and track strict-format
  files (such as JSON, scripts, and binaries) via `MANIFEST.yaml`
- Create `MANIFEST.yaml` listing all files with roles, versions, and hashes
- Create `CHANGELOG.md` with a 1.0.0 bootstrap entry
- Return all updated files

### Step 5: Repack and reinstall

Put the updated files back into the directory structure:

```
weekly-newsletter/
├── SKILL.md              ← updated; may remain manifest-only in minimal mode
├── MANIFEST.yaml         ← new (versioning)
├── CHANGELOG.md          ← new (versioning)
├── README.md             ← new (versioning, optional)
├── assets/
│   └── template.md       ← updated with version header
└── references/
    ├── guidelines.md     ← updated with version header
    ├── examples.md       ← updated with version header
    └── checklist.md      ← updated with version header
```

Re-ZIP:

```bash
# macOS / Linux — run from the directory containing the skill folder
cd ~/Desktop
zip -r weekly-newsletter.skill weekly-newsletter/

# Windows (PowerShell) — rename .zip to .skill after creating
Compress-Archive -Path weekly-newsletter -DestinationPath weekly-newsletter.zip
Rename-Item weekly-newsletter.zip weekly-newsletter.skill
```

Then reinstall: `Settings` → `Skills` → remove the old version →
`Add Skill` → select the new `.skill` file.

The versioning artifacts survive the round-trip through Claude's settings
because they're inside the ZIP alongside the files Claude already knows
about.

### Step 6: Ongoing use

From now on, when you iterate on the skill in any Claude conversation,
the internal headers (when present) and manifest travel with it. When you download
it again, the versioning artifacts come with it.


## Porting bundles between surfaces

Each Claude surface handles files differently, and there's no shared
filesystem between them. The bundle travels through you — typically as
a `.skill` ZIP or as loose files in a working directory.

### What to carry

At minimum, carry these files when moving between surfaces:
- `MANIFEST.yaml` (the source of truth)
- `CHANGELOG.md` (the history)
- Every file listed in the manifest

The manifest tells the receiving session what it should have. If you
forget a file, the opening protocol will catch it.

### The .skill ZIP as transport container

For moves involving Claude Chat or settings, the `.skill` ZIP is the
natural transport format. The versioning artifacts (`MANIFEST.yaml`,
`CHANGELOG.md`) live inside the ZIP alongside the other skill files.

For moves involving Claude Code or local git repos, loose files in a
directory are more natural. The ZIP is just a container — the versioning
system works identically either way.

### Surface → Surface workflows

#### Chat → Chat (new conversation, same or different project)

1. **Close the old session.** Tell Claude to package the bundle. Claude
   updates versioning artifacts and tells you which files to save.
2. **Download all output files** from the conversation.
3. **Open a new conversation.** Upload all bundle files.
4. **Tell Claude to verify the bundle.** Claude reads the manifest and
   confirms everything arrived intact.

If you're working with installed skills (visible in Settings → Skills),
download the `.skill` ZIP, unpack, update, repack, and reinstall.

#### Chat → Code

1. **Close the Chat session** and download all bundle files (or download
   the `.skill` ZIP and unpack it).
2. **Place files in your Code project** in a directory structure:
   ```
   skills/
     my-skill/
       SKILL.md
       MANIFEST.yaml
       CHANGELOG.md
       evals.json
       scripts/
       outputs/
   ```
3. **In Code**, Claude can verify the bundle by reading the manifest.
   Hashes can be verified or omitted since git handles integrity.
4. **Commit the bundle** as your initial versioned state. From here,
   git and the manifest work together: git tracks every change, the
   manifest tracks roles and staleness.

#### Code → Chat

1. **Ensure the bundle is clean** in your repo (no uncommitted changes
   that you care about).
2. **Copy the bundle files** out of your repo into a local directory.
3. **Upload to Chat.** Tell Claude to verify the bundle.
4. **Or repack as .skill:** ZIP the directory, rename to `.skill`,
   and install via Settings → Skills → Add Skill.

Note: Chat doesn't see your git history. The changelog and manifest are
what preserve context across this boundary.

#### Chat → Cowork / Cowork → Chat

Same pattern as Chat → Code, but files go into Cowork's filesystem
instead of a git repo. Cowork has filesystem persistence within a
project, so the bundle stays put between sessions.

#### Any surface → Obsidian (offline storage)

1. **Close the session** and download updated bundle files.
2. **Copy the bundle directory** into your Obsidian vault.
3. The manifest, changelog, and any internal headers are all plain
   markdown and YAML — they render natively in Obsidian.
4. When you return, upload from Obsidian to whichever surface you're
   using next.

#### Any surface → Git (publishing)

1. **Ensure bundle is clean and versioned** (all files have current
   internal headers when applicable, manifest is up to date, changelog
   has latest entry).
2. **Copy the bundle directory** into your git repo.
3. **Commit with a message** that references the bundle version:
   `my-skill 5.1.0: added validation phase, updated checklist`
4. **Optionally tag:** `git tag my-skill-5.1.0`
5. The manifest hashes can be omitted in git since git handles integrity,
   but version numbers and change summaries remain required.

### What if I forget to carry the manifest?

Claude can reconstruct one from the files you upload, but it will need
to ask you about version numbers and history. This is the bootstrap
flow — it works, but you lose hash verification and staleness tracking
for that transition. Better to carry the manifest.


## Gemini Gems workflow

Gemini Gems are Google's equivalent of Claude Skills/Projects in the
web UI. A Gem consists of a name, a system prompt (the "instructions"
field), and optional knowledge files uploaded to the Gem's knowledge
base. Unlike Claude's `.skill` ZIP format, Gems don't accept a single
bundle — instructions are copy-pasted and files are uploaded individually
through the Gem Manager.

### Tracking a Gem with skill-provenance

To version-track a Gem alongside its associated files:

1. **Save the Gem's system prompt** as a file in your bundle (e.g.,
   `GEM_INSTRUCTIONS.md`). Track it in the manifest with
   `file_role: reference`. This becomes the source of truth for the
   Gem's instructions — edit it locally, then update the Gem.

2. **Version the bundle normally** using skill-provenance. The Gem
   instructions file gets internal headers when appropriate, changelog
   entries, and manifest tracking like any other file.

3. **On session close**, ask the skill to generate a "Gem update
   summary." This tells you:
   - Whether `GEM_INSTRUCTIONS.md` changed (and if so, the full text
     to copy-paste into the Gem Manager's instructions field)
   - Which files in the bundle need to be re-uploaded to the Gem's
     knowledge base (any file that changed this session)
   - The version number and change summary for your records

### Example prompt

> "Package the bundle. I also maintain a Gemini Gem for this skill —
> tell me what I need to update in the Gem Manager."

### Limitations

- Gem updates are manual (copy-paste instructions, re-upload files).
  There is no API for programmatic Gem management.
- Gems have file size and count limits for their knowledge base. Check
  current limits in the Gem Manager.
- The Gem's instructions field is plain text, not YAML frontmatter.
  Copy the body of `GEM_INSTRUCTIONS.md` without the internal header.


## File naming

The versioning system uses stable filenames:

| Do this | Not this |
|---|---|
| `SKILL.md` | `SKILL_v5.md` |
| `evals.json` | `evals_v3.json` |
| `generate.js` | `generate-v4.js` |

The version lives inside the file and in the manifest. If your local
workflow requires version-numbered filenames (e.g., to keep multiple
versions visible in a directory), the manifest's version field is the
tiebreaker for which is canonical.


## Local hash validation

LLMs can compute SHA-256 hashes when they have shell access (Claude Code,
Cowork), but hash computation in Chat sessions is slower and can be
unreliable on large files. For reliable pre-upload verification, use the
included `validate.sh` script.

### Verify mode (default)

```bash
# From inside the bundle directory
./validate.sh

# Or pass the bundle path
./validate.sh path/to/my-skill
```

Output:
```
OK       SKILL.md
OK       evals.json
MISMATCH README.md
  expected: abc123...
  actual:   def456...
MISSING  generate.js

Checked 4 files, skipped 0, errors 2
```

### Update mode

After editing files locally, recompute all hashes in MANIFEST.yaml:

```bash
./validate.sh --update
```

Output:
```
UPDATED  SKILL.md
OK       evals.json
UPDATED  README.md

Checked 3 files, skipped 0, updated 2
MANIFEST.yaml updated.
```

This closes the local editing loop: edit files in your IDE or
Obsidian, run `./validate.sh --update`, then upload to Chat with
correct hashes already in place.

### Details

The script reads `MANIFEST.yaml`, computes actual SHA-256 hashes for
each file, and reports matches, mismatches, and missing files. Files
without hashes in the manifest are skipped. `MANIFEST.yaml` itself is not
self-listed, so the script treats it as the control file rather than a
hash target. Exit code 0 means all hashes verified (or updated); exit code 1
means missing files were found.

Zero dependencies beyond `bash`, `shasum` or `sha256sum`, and `awk`.


## Troubleshooting

**I can't open a .skill file on macOS.**
macOS Finder and Archive Utility do not recognize the `.skill` extension.
They won't offer to open it, even via `Open With`. Use Terminal:
`unzip my-skill.skill -d ~/Desktop/`. Always use `-d` to specify a
destination — without it, files extract to your current working directory
(usually `~`), which makes them hard to find.

**I ran unzip but can't find the extracted files.**
Unlike Finder's Archive Utility (which extracts next to the ZIP file),
Terminal's `unzip` command extracts to your current working directory,
not the directory where the `.skill` file lives. If you ran
`unzip ~/Desktop/my-skill.skill` from `~`, the files are in
`~/my-skill/`, not on your Desktop. Always use `-d` to control the
destination: `unzip ~/Desktop/my-skill.skill -d ~/Desktop/`.

**Claude doesn't recognize the skill-provenance skill.**
Make sure the SKILL.md is loaded — either uploaded in the conversation,
in project knowledge, or in the skills directory. If you renamed it,
that's fine — Claude identifies it by frontmatter, not filename.

**Version numbers disagree between a file and the manifest.**
This is a conflict. Claude will present both claims and ask you to
decide. Default: trust the more recent `version_date`.

**I have files that aren't in the manifest.**
New files created during a session won't appear in the manifest until
you close the session and Claude updates the manifest. If you're
uploading files that should be tracked, tell Claude to add them.

**The changelog is getting long.**
That's fine. It's append-only by design. For very mature skills, you
can archive older entries into a `CHANGELOG-archive.md` and keep only
the last 10-15 entries in the active changelog. Note this in the
changelog itself.

**I want to version source material too.**
Source material (user-provided articles, images, data) is tracked in
the manifest for completeness but not versioned. If source material
changes, update the hash in the manifest and note it in the changelog.


## Relationship to the Agent Skills specification

The Agent Skills format (agentskills.io) defines a `metadata` field in
SKILL.md frontmatter that supports arbitrary key-value pairs, including
a `version` key. Bundles can use that field for SKILL.md version headers
when they choose `frontmatter_mode: claude` (see the frontmatter constraint
above).

However, the official spec's `version` field is a static label — it
doesn't address cross-session staleness tracking, changelogs, manifests,
or bundle integrity verification. This skill fills that gap. It is
complementary to the spec, not a replacement.

This bundle ships in `frontmatter_mode: minimal` for maximum portability,
so its own SKILL.md version lives in `MANIFEST.yaml`.

The API's skill versioning system (epoch timestamps via `/v1/skills`)
handles version management for skills deployed through the API. This
skill handles version management for skills in development, moving
between sessions, and stored locally — the workflow that precedes
API deployment.


## References

### Official documentation

- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — architecture, progressive disclosure, cross-surface availability
- [Agent Skills best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — authoring guidance for SKILL.md
- [Agent Skills specification](https://agentskills.io/specification) — the open standard format definition
- [Skills cookbook](https://platform.claude.com/cookbook/skills-notebooks-01-skills-introduction) — API usage tutorial with Excel, PowerPoint, PDF examples
- [Using Skills with the API](https://platform.claude.com/docs/en/build-with-claude/skills-guide) — `/v1/skills` endpoints, custom skill uploads

### Blog posts and announcements

- [Introducing Agent Skills](https://claude.com/blog/skills) — launch announcement (October 2025)
- [Organization Skills and Directory](https://claude.com/blog/organization-skills-and-directory) — org-wide management, partner directory (December 2025)

### Ecosystem

- [Agent Skills open standard](https://agentskills.io/home) — cross-platform spec, adopted by Claude, GitHub Copilot, Cursor, Codex, and others
- [Agent Skills GitHub](https://github.com/agentskills/agentskills) — specification source, reference library, validation tools
- [Anthropic example skills](https://github.com/anthropics/skills) — official skill examples and templates
- [Connectors directory](https://claude.com/connectors) — partner-built skills and MCP connectors
- [Gemini CLI creating skills](https://geminicli.com/docs/cli/creating-skills/) — Gemini CLI skill authoring guide
- [Gemini Gems](https://support.google.com/gemini/answer/16504957) — creating and sharing Gemini Gems
- [Skillman](https://github.com/pi0/skillman) — JS/TS skill manager for installing, updating, and organizing agent skills from npm and GitHub
- [Skillman (Python)](https://github.com/chrisvoncsefalvay/skillman) — Python CLI for installing and locking agent skills from GitHub repos

### Research

- [Agent Skills for Large Language Models](https://arxiv.org/abs/2602.12430) — survey of skill architecture, acquisition, security, and governance (Xu & Yan, 2026)

### Support articles

- [What are Skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using Skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom Skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Teach Claude your way of working using Skills](https://support.claude.com/en/articles/12580051-teach-claude-your-way-of-working-using-skills)
