# Council of the Wise

A Clawdbot skill that spawns sub-agents to analyze ideas from multiple expert perspectives.

## What It Does

When you say "send this to the council" or "council of the wise," Clawdbot:

1. Sends a loading message
2. Spawns a sub-agent that analyzes your idea through 5 lenses + a synthesis moderator:

- **👹 Devil's Advocate** — Challenges assumptions, finds weaknesses
- **🏗️ Architect** — High-level strategy, systems thinking, tradeoffs
- **🛠️ Engineer** — Implementation feasibility, time estimates, concrete steps
- **🎨 Artist** — Voice, style, and user experience
- **📊 Analyst** — ROI, opportunity cost, quantitative rigor
- **⚖️ Synthesis** — Moderator who gives a verdict, not just a summary

Each agent has YAML frontmatter (`name`, `emoji`, `domain`) and a defined signature move.

The sub-agent returns a synthesized report with insights, concerns, recommendations, prioritized action items, and a confidence signal.

## Installation

### Via ClawHub
```bash
clawhub install council-of-the-wise
```

### Manual
Copy the `council/` folder to your Clawdbot skills directory:
```bash
cp -r council/ ~/clawd/skills/council/
```

## Usage

```
"Send this to the council: [your idea]"
"Council of the wise: [topic to analyze]"
"Get the council's feedback on [thing]"
```

### Follow-Up

After receiving the council report, you can dig deeper with any member:

```
"I want to hear more from the Engineer on point 3."
"Have the Analyst run the numbers on option B."
```

This spawns a follow-up sub-agent with just that member's persona.

## Adding Custom Agents

Drop a `.md` file in the `agents/` folder with YAML frontmatter:

```markdown
---
name: Pentester
emoji: 🔓
domain: technical
---

# Pentester

You analyze security implications...

## Signature Move
Always identifies the most likely attack vector first.

## Example Output
> The first thing I'd try is...
```

The skill auto-discovers all agents. No config changes needed.

## Tips

- **Be specific.** "Analyze my startup idea" is weak. Include the pitch, constraints, and what you've already considered.
- **Use the synthesis.** Individual perspectives are interesting; the synthesis is actionable.
- **Follow up.** Dig into the most interesting points with a single council member.
- **Run it early.** Easier to hear criticism before you're emotionally invested.

## Credits

Inspired by [Daniel Miessler](https://danielmiessler.com/)'s PAI (Personal AI Infrastructure). The Architect, Engineer, and Artist agents are adapted from PAI patterns. The Devil's Advocate is an original creation.

## License

MIT
