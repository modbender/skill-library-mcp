---
name: mindgraph
description: 'Obsidian-style [[wikilink]] knowledge graph and learnable
  MindSkills for OpenClaw workspaces. Use for ALL of these: (1) Any workspace
  file read/write — always use [[wikilinks]] for people, projects, tools,
  concepts. (2) Running learned processes like knockout-test, seo-validator,
  competitor-analysis. (3) Querying knowledge — "what do I know about X", "show
  connections to Y". (4) Learning new repeatable processes — "learn a new
  mindskill called Z". (5) Memory maintenance — finding orphans, dead links,
  unconnected files. This skill is always active — treat [[wikilinks]] as
  standard practice in every markdown file you write.'
---


# MindGraph 🕸️🧠

A knowledge graph + learnable process engine for OpenClaw. Two core features:

1. **Knowledge Graph** — Obsidian-style `[[wikilinks]]` across all workspace files
2. **MindSkills** — Learned, repeatable processes that save graph-connected results

## Always-On Rules

**Every time you write or edit a markdown file, use `[[wikilinks]]` for:**
- People: `[[Alice]]`, `[[Bob]]`
- Projects: `[[my-saas]]`, `[[landing-page]]`
- Companies/tools: `[[Stripe]]`, `[[Vercel]]`, `[[GitHub]]`
- Concepts/frameworks: `[[Knockout Test]]`, `[[B2B SaaS]]`
- Other agents/models: `[[Claude Code]]`, `[[Sonnet]]`

This is not optional. Links are how knowledge connects. No links = isolated notes = useless.

**NEVER use `[[wikilinks]]` in messages to the user** (Telegram, Discord, etc.). Wikilinks are for workspace files only. In conversations, write names plain: "Alice", not "[[Alice]]".

**After significant file changes, rebuild the index:**
```bash
python3 skills/mindgraph/scripts/mindgraph.py index
```

## Graph Commands

```bash
# Build/rebuild index
python3 skills/mindgraph/scripts/mindgraph.py index

# Query a topic (backlinks + context + connections)
python3 skills/mindgraph/scripts/mindgraph.py query "<name>"

# Backlinks only (what references this?)
python3 skills/mindgraph/scripts/mindgraph.py backlinks "<name>"

# Forward links (what does this link to?)
python3 skills/mindgraph/scripts/mindgraph.py links "<file>"

# Bidirectional connections
python3 skills/mindgraph/scripts/mindgraph.py connections "<name>"

# ASCII tree visualization
python3 skills/mindgraph/scripts/mindgraph.py tree "<name>" [depth]

# Find orphans, dead links, unconnected files
python3 skills/mindgraph/scripts/mindgraph.py orphans
python3 skills/mindgraph/scripts/mindgraph.py deadlinks
python3 skills/mindgraph/scripts/mindgraph.py lonely

# Full statistics
python3 skills/mindgraph/scripts/mindgraph.py stats
```

## MindSkills — Learned Processes

MindSkills are repeatable frameworks stored in `skills/mindgraph/mindskills/`. Each has a defined process and saves results as graph-connected markdown.

### Using a MindSkill

```bash
# List all learned mindskills
python3 skills/mindgraph/scripts/mindgraph.py skills

# Show a mindskill's process
python3 skills/mindgraph/scripts/mindgraph.py skill <name>

# List results for a mindskill
python3 skills/mindgraph/scripts/mindgraph.py results <name>
```

When a user asks to run a process (e.g., "run the knockout test on X"), follow this flow:

1. Read the mindskill's `PROCESS.md` for the process definition
2. Execute the process conversationally
3. Save the result to `skills/mindgraph/mindskills/<name>/results/<subject>.md`
4. Use `[[wikilinks]]` throughout the result file
5. Include YAML frontmatter with metadata
6. Rebuild the graph index

Result file template:
```markdown
---
mindskill: <skill-name>
subject: <what was tested/analyzed>
date: <YYYY-MM-DD>
verdict: <outcome>
aliases: [<aliases>]
---
# [[<MindSkill Name>]]: [[<Subject>]]

<Results following the process defined in PROCESS.md>

## Connections
- Related: [[link1]], [[link2]]
```

### Learning a New MindSkill

When a user says "learn a mindskill called X" or describes a repeatable process:

```bash
# Create a new mindskill
python3 skills/mindgraph/scripts/mindgraph.py learn "<name>"
```

This creates the directory structure. Then write the PROCESS.md based on the user's description.

A good PROCESS.md contains:
- **Purpose**: What this process does and when to use it
- **Trigger phrases**: What the user might say to invoke this
- **Steps**: The actual process to follow (numbered)
- **Output format**: What the result file should contain
- **Verdict/scoring**: How to summarize the outcome (if applicable)

### Discovering MindSkills

When a user's request matches a learned mindskill, proactively suggest it:
- "Want me to run the [[Knockout Test]] on that?"
- "I have an [[SEO Validator]] mindskill — should I audit that?"
- "This looks like a [[Competitor Analysis]] — want the full framework?"

## Link Resolution

Links match (case-insensitive) against:
1. File basenames: `[[MEMORY]]` → `MEMORY.md`
2. Project dirs: `[[my-saas]]` → `projects/my-saas/`
3. MindSkill results: `[[Pet Tracker KT]]` → knockout test result
4. YAML aliases: `aliases: [AV-Check]` → `[[AV-Check]]` resolves
5. Unresolved → concept node (still tracked for backlinks)

## File Locations

- Graph index: `mindgraph.json` (workspace root)
- MindSkills: `skills/mindgraph/mindskills/`
- Script: `skills/mindgraph/scripts/mindgraph.py`
