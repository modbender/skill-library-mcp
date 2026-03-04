---
name: dev-chronicle
description: Generate narrative chronicles of developer work from git history, session transcripts, and memory files. Use when the user asks "what did I do today/this week", wants a work summary, daily/weekly chronicle, standup notes, or portfolio narrative. Also triggers on "chronicle", "dev diary", "work story", "recap", or "standup".
---

# DevChronicle — Narrative Engineering Journal

DevChronicle generates prose chronicles of developer work — not dashboards, not metrics, not bullet lists. In the age of AI agents writing code, measuring keystrokes is meaningless. What matters is what you *decided*, what you *killed*, and where you're *going*.

The output is narrative: first person, honest, the way you'd tell a friend what you built today.

## Setup

On first use, check for `{baseDir}/config.json`. If it doesn't exist, create it by asking the user:

```json
{
  "projectDirs": ["~/Projects"],
  "projectDepth": 3,
  "memoryDir": null,
  "sessionsDir": null
}
```

- `projectDirs`: directories to scan for git repos (array, supports `~`)
- `projectDepth`: how deep to search for `.git` folders (default: 3)
- `memoryDir`: path to OpenClaw memory files, or `null` to auto-detect (`<workspace>/memory`)
- `sessionsDir`: path to session transcripts, or `null` to auto-detect (`~/.openclaw/agents/main/sessions`)

## Gathering Data

Run the gather script to collect raw data for a period:

```bash
bash {baseDir}/scripts/gather.sh [YYYY-MM-DD] [days]
```

Examples:
- `bash {baseDir}/scripts/gather.sh` — today only
- `bash {baseDir}/scripts/gather.sh 2026-02-19 7` — week ending Feb 19

The script reads `{baseDir}/config.json` for paths. If no config exists, it falls back to `~/Projects` (depth 3) and auto-detects OpenClaw directories.

After gathering, read the output and generate a chronicle.

### Data Sources (priority order)

1. **Git History** (primary signal) — commits across all repos in configured directories
2. **Memory Files** — `memory/YYYY-MM-DD.md` files contain decisions, context, things worth remembering
3. **Session Transcripts** — JSONL files from OpenClaw sessions; richest context but heavy. Scan metadata line first, only read relevant sessions.
4. **External Tools** (optional) — Trello, Notion, calendar, etc. Enrichment, not primary.

## Generating the Chronicle

### Voice

**Critical**: Read `{baseDir}/references/voice-profile.md` before generating any chronicle. The voice IS the product.

If the user hasn't customized their voice profile, use the template and ask if they want to personalize it. A chronicle without voice is just a changelog.

Core rules (regardless of voice profile):
- **Decisions > tasks.** What got rejected matters as much as what shipped.
- **No corporate speak.** No "leveraged", "synergized", "deliverables", "open threads", "action items".
- **Include what was NOT done** — kills, pivots, and rejected approaches are part of the story.
- **Emotional beats matter** — the satisfaction, frustration, surprise. These are human signals.
- **Be personal.** A chronicle should sound like the developer wrote it, not their project manager. If it reads like a status report, rewrite it.
- **Structure is a suggestion, not a cage.** If the day had one big theme, write one section. If it was chaos, let it be chaotic. Don't force headers.

### Formats

**Daily Chronicle** (default — aim for ~500-800 words, not a novel)
```markdown
# Chronicle — [Date]

[Opening: set the scene in 1-2 punchy sentences]

## [Theme 1]
[Narrative: what happened, why, what got killed or rejected, how it felt]

## [Theme 2]
[...]

[Weave metrics naturally: "12 commits later..." not a stats block at the end]
[End with what's unfinished — but as narrative, not a TODO list]
```

Rules:
- **Daily = tight.** One screen of text. Save the epic for weekly.
- **No "Metrics" section.** If commit count matters, weave it in. "67 commits across two days" belongs in a sentence, not a table.
- **No "Open Threads" or "Next Steps".** If something's unfinished, say it where it fits: "El Press Kit sigue esperando que Angélica suba el PDF." Done.
- **Numbers without story are noise.** "5 deploys" means nothing. "Deployed 5 times because the server kept OOM-killing on a 914MB box" means something.

**Weekly Chronicle** — roll up daily themes into arcs. This one CAN be long. Emphasize direction and pivots over individual tasks.

**Standup** — telegraphic: yesterday / today / blockers. Three bullets max each.

**Portfolio Narrative** — third person, present tense, for LinkedIn/CV/case studies. Punchy and honest, not marketing-speak.

## Direction/Execution Ratio

When enough data exists (weekly+), calculate and mention:
- **Spec lines vs code lines** — are you building or planning?
- **Commits vs decisions** — activity vs impact
- **Kills** — what got cut and why (kills show taste)
- **Pivots** — direction changes and their reasoning

This is not a KPI. It's a mirror.
