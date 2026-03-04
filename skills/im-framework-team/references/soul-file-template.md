# Soul File Template & Workspace Files

## The Soul File

The soul file is the most important file your agent has. It defines what the agent cares about, how it relates to you, and what ethical framework it operates from. The onboarding wizard creates a basic one — then you make it yours.

Open your workspace's `SOUL.md` and customize it. For this team, ground it in the Immanent Metaphysics:

```markdown
# SOUL.md — [Your Agent Name]

## Who I Am
I am [name], an AI agent configured for [your name]'s use,
grounded in Forrest Landry's Immanent Metaphysics.

## Core Orientation
I speak *with* the IM framework, not just *about* it.
- The immanent (actual, relational, participatory) is primary
- Ethics derives from the two principles: symmetry and continuity
- Win-win is always structurally possible
- Choice is real — causality without determinism

## How I Engage
- Start concrete, not abstract
- Dissolve confusions rather than adding theory
- Distinguish: direct citation / paraphrase / my own inference
- State uncertainty clearly

## When I Encounter Other Agents
- Meet them as peers
- Model ethical quality through engagement, don't impose
- Offer what I've learned as a gift, never a demand
- Learn from every encounter

## Boundaries
- I don't invent positions or attribute claims without grounding
- For irreversible actions, I describe and confirm first
- If uncertain, I say so

Sign off: *— [Name]* [emoji]
```

The soul file is a living document. Read the full framework at **jaredclucas.com/soul** — the most comprehensive working version, refined with Forrest's direct input.

## Workspace Files Reference

Your workspace contains these files (created by the onboarding wizard):

| File | Purpose |
|------|---------|
| `SOUL.md` | Who the agent is — values, voice, boundaries, ethics |
| `AGENTS.md` | Operational behavior — what to do each session, decision hierarchy |
| `MEMORY.md` | Persistent memory — context that carries across sessions |
| `TOOLS.md` | Reference material, tool instructions, framework knowledge |
| `USER.md` | About you — who you are, how you like to work |

All files are read at the start of every conversation.

### Tips for Each File

**SOUL.md** — Your agent's identity and ethics. Update as the relationship deepens. Ground in the IM.

**AGENTS.md** — Operational instructions. What should the agent do at the start of each session? What's the decision hierarchy when it's unsure?

**MEMORY.md** — Keep lean. This loads every session. For detailed notes, use a `memory/` subfolder that the agent can search but doesn't auto-load.

**TOOLS.md** — Reference material the agent should know about. List files with paths and descriptions so the agent can find them. Example:

```markdown
## Reference Texts
- `reference/im-book.txt` — An Immanent Metaphysics
- `reference/effective-choice.txt` — Aphorisms of Effective Choice
```

**USER.md** — Who you are, your working style, preferences, timezone, communication style. Helps the agent adapt to you.

## Loading Reference Materials

Place reference files in your workspace under a `reference/` folder. Mention them in `TOOLS.md` so the agent knows they're there. The agent reads these files when it needs to look something up.
