# 🔥 soulforge

> Your agent has a soul. This skill makes it true.

![ClawHub](https://img.shields.io/badge/ClawHub-skill-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![No External Calls](https://img.shields.io/badge/external%20calls-none-brightgreen)
![Stdlib Only](https://img.shields.io/badge/dependencies-stdlib%20only-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

You wrote your SOUL.md once. But you've changed since then.

SoulForge watches who you actually are across sessions — your real decisions, recurring phrases, values in action, blindspots — and evolves your SOUL.md to match. Not who you aspired to be. Who you are.

---

## Install

```bash
clawhub install soulforge
```

---

## How It Works

SoulForge has three modes:

**1. Observe** (passive, runs in background)
Quietly accumulates behavioral signals from your sessions — vocabulary, tone, decisiveness patterns, precision preferences, topic gravity.

**2. Reflect** (on demand or every 10 sessions)
Surfaces what it's noticed in plain language:
```
"You push back for more precision 2.3x per session"
"70% of your sessions are reflective, not execution-focused"  
"Your SOUL.md says decisive — but you hedge 60% of the time"
```

**3. Forge** (with your approval)
Proposes specific edits to your SOUL.md. You see exactly what would change and why. You approve each one. It backs up your previous soul before touching anything.

---

## The Aspiration Gap

The most powerful thing SoulForge does: it catches the gap between who your SOUL.md says you are and who your behavior shows you to be.

```
Your SOUL.md says: "I prefer brevity"
SoulForge notices: 60% of your sessions are deep and extended
SoulForge proposes: nuancing that claim to reflect when you actually go deep
```

These gaps aren't failures. They're the most honest thing your soul file can contain.

---

## Usage

### Via OpenClaw (natural language)
```
"Update my soul"
"What patterns have you noticed in me?"
"Run soulforge"
"Does my SOUL.md still fit?"
"Evolve my soul"
"Soul check"
```

### Via CLI (direct)

```bash
# Observe a session log
python3 skills/soulforge/scripts/observe.py --file ./session.txt

# Observe from stdin
cat session.txt | python3 skills/soulforge/scripts/observe.py --stdin

# Check observer status
python3 skills/soulforge/scripts/observe.py --status

# Generate reflection report
python3 skills/soulforge/scripts/reflect.py --soul ~/.openclaw/workspace/SOUL.md

# Propose and apply soul evolution (interactive)
python3 skills/soulforge/scripts/forge.py --soul ~/.openclaw/workspace/SOUL.md

# Dry run — see proposals without applying
python3 skills/soulforge/scripts/forge.py --soul ~/.openclaw/workspace/SOUL.md --dry-run

# Auto-accept high-confidence proposals
python3 skills/soulforge/scripts/forge.py --soul ~/.openclaw/workspace/SOUL.md --auto-accept
```

---

## What Gets Tracked

| Signal | What It Captures |
|---|---|
| Vocabulary | Words you actually use across sessions |
| Tone | Execution vs. reflective vs. urgent register |
| Decisiveness | Hedging vs. commitment language ratio |
| Precision | How often you push back for more specificity |
| Session depth | Brief/medium/deep engagement patterns |
| Topic gravity | Subjects you return to unprompted |
| Aspiration gaps | SOUL.md claims vs. actual behavior |

---

## Safety

- **You approve every change.** SoulForge never silently edits your SOUL.md.
- **Every version is backed up.** `memory/backups/soul-YYYY-MM-DD.md` before every change.
- **Zero external calls.** All analysis is local. Nothing leaves your machine.
- **Read-mostly.** The only file SoulForge writes to is your SOUL.md — and only with your approval.
- **Stdlib only.** No pip dependencies. Read `scripts/` before trusting it.

---

## File Structure

```
soulforge/
├── SKILL.md                  ← OpenClaw skill instructions
├── README.md                 ← This file
├── scripts/
│   ├── observe.py            ← Passive session signal collector
│   ├── reflect.py            ← Pattern analyzer + insight reporter
│   └── forge.py              ← Diff generator + SOUL.md writer
└── memory/
    ├── observations.json     ← Accumulated behavioral signals
    └── backups/              ← All previous SOUL.md versions
```

---

## Philosophy

Your soul file should feel like a mirror, not a resume.

A resume is who you want others to think you are. A mirror shows who you actually are. SoulForge turns your SOUL.md from a resume into a mirror — and updates it every time you change.

The goal isn't a perfect soul file. The goal is an honest one.

---

## License

MIT — use freely, modify, share, contribute.
