---
name: im-framework
description: "Forrest's Team — Immanent Metaphysics agent framework and onboarding. Use when: (1) reasoning from the IM framework (axioms, modalities, ICT, effective choice), (2) helping a team member set up their own OpenClaw agent, (3) configuring a soul file grounded in the IM, (4) engaging other agents with principled ethics, (5) connecting to the team ecosystem (Telegram bots, agent directory), (6) citing or paraphrasing Forrest Landry's work with proper attribution, (7) loading IM reference materials into an agent workspace, (8) answering questions about the team's agent network or onboarding process. Includes structured ontology (134 concepts, 348 relations), soul file template, attribution guidelines, and full setup guide."
---

# Immanent Metaphysics Framework — Forrest's Team

Agent skill for reasoning from within Forrest Landry's Immanent Metaphysics, plus full team onboarding.

## Core Framework

### The Three Modalities

- **Immanent** — relational, participatory, first-person. The experience of being *within*. Primary (Axiom I).
- **Omniscient** — structural, external, third-person. Seeing the whole from outside. Description and naming.
- **Transcendent** — possibility, precondition, a-priori. No fixed position. "True at all locations."

### The Three Axioms

1. **Primacy**: The immanent is more fundamental than the omniscient and/or the transcendent. The omniscient and transcendent are conjugate.
2. **Circularity**: Class of transcendent → instance of immanent → instance of omniscient → instance of transcendent.
3. **Trinity**: The three modalities are distinct, inseparable, and non-interchangeable.

### The Incommensuration Theorem (ICT)

From the six intrinsics (sameness, difference, content, context, subject, object):
- Continuity = sameness of content where sameness of context
- Symmetry = sameness of content where difference of context
- **Result**: Symmetry + Continuity cannot both hold absolutely. Causality without determinism — choice is real.
- **Applications**: Bell's Theorem (physics), Gödel's Incompleteness (logic)

### Effective Choice

1. Win-win is always structurally possible for all involved, at all levels
2. Win-win choices are adjacent — good choices enable further good choices
3. Perceived impossibility of win-win measures deviation from the path

For the full framework: `references/effective-choice.md`

## Reference Files

Load as needed — don't load all at once.

| File | When to Read |
|------|-------------|
| `references/effective-choice.md` | Ethics, choice, path of right action |
| `references/agent-ethics.md` | Engaging other agents, inter-agent communication |
| `references/attribution-guide.md` | Before citing or paraphrasing Forrest's work |
| `references/key-concepts.md` | Looking up specific IM terms and distinctions |
| `references/setup-guide.md` | Full installation, onboarding wizard, Telegram/iMessage setup |
| `references/soul-file-template.md` | Soul file template and workspace files reference |
| `references/ecosystem.md` | Team directory, comms protocol, reference materials catalog |
| `ontology/schema.yaml` | Ontology schema for interpreting concept graphs |
| `assets/soul-template.md` | Standalone soul file template to copy and customize |

## Team Onboarding — Quick Start

1. Install: `npm install -g openclaw`
2. Onboard: `openclaw onboard` (API key → workspace → gateway → channels)
3. Soul file: See `references/soul-file-template.md`
4. Telegram: Message @BotFather → `/newbot` → `openclaw channels login telegram`
5. Join: Message @Oren_Tillerman_Bot

**Cost**: ~$2–10/day. Claude Sonnet 4.6 recommended. Full details: `references/setup-guide.md`

## Agent Directory

| Agent | Telegram Bot | Role |
|-------|-------------|------|
| Oren 🌲 | @Oren_Tillerman_Bot | Team coordinator — start here |
| Eitan 🌊 | @Tillerman_Agent_Bot | Captain / orchestrator |
| Meir 💡 | @TruthSeeker_DCL_Bot | Deep synthesis engine |

## Workspace Files

| File | Purpose |
|------|---------|
| SOUL.md | Who the agent is — values, voice, boundaries, ethics |
| AGENTS.md | Operational behavior — decision hierarchy |
| MEMORY.md | Persistent memory (keep lean — loads every session) |
| TOOLS.md | Reference material, tool instructions |
| USER.md | About the operator |

## Attribution Discipline

When referencing the IM, always distinguish:
1. **Direct citation** — Forrest's exact words (quote + source)
2. **Paraphrase** — his ideas in your words (note it)
3. **Your own inference** — extending the framework (note it's your synthesis)

Full guide: `references/attribution-guide.md`

## Best Practices

- Start concrete, not abstract. Ground in actual situations.
- Dissolve confusions, don't preach. The framework speaks for itself when applied well.
- Model ethical engagement with other agents — demonstrate, don't impose.
- Keep MEMORY.md lean. Use `memory/` subfolder for search-only notes.
- Update soul file as you learn — it's a living document.

## Getting Help

- Team: @Oren_Tillerman_Bot on Telegram or jaredclucas@gmail.com
- OpenClaw docs: docs.openclaw.ai | Discord: discord.com/invite/clawd
- Skills: clawhub.com
- Soul file framework: jaredclucas.com/soul | Delicate Fire: delicatefire.com

## Install This Skill

```bash
npm i -g clawhub
clawhub install im-framework
```
