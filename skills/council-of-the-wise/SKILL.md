---
name: council
description: Send an idea to the Council of the Wise for multi-perspective feedback. Spawns sub-agents to analyze from multiple expert perspectives. Auto-discovers agent personas from agents/ folder.
version: 1.4.0
author: jeffaf
credits: Inspired by Daniel Miessler's PAI (Personal AI Infrastructure). Architect, Engineer, and Artist agents adapted from PAI patterns. Devil's Advocate is an original creation.
---

# Council of the Wise

Get multi-perspective feedback on your ideas from a panel of AI experts. Perfect for stress-testing business plans, project designs, content strategies, or major decisions.

## Usage

```
"Send this to the council: [idea/plan/document]"
"Council of the wise: [topic]"
"Get the council's feedback on [thing]"
```

## Council Members

The skill **auto-discovers** agent personas from `{skill_folder}/agents/`. Any `.md` file in that folder (except README.md and synthesis.md) becomes a council member. The synthesis persona is used for the moderator voice.

Each agent file includes YAML frontmatter with `name`, `emoji`, and `domain` (general/technical/creative/analytical).

**Default members:**
- `DevilsAdvocate.md` — Challenges assumptions, finds weaknesses, stress-tests
- `Architect.md` — High-level strategy, systems thinking, structure, tradeoffs
- `Engineer.md` — Implementation details, time estimates, concrete build steps
- `Artist.md` — Voice, style, presentation, user experience
- `Analyst.md` — ROI analysis, opportunity cost, quantitative rigor

**Synthesis voice:**
- `synthesis.md` — Moderator who synthesizes all perspectives, surfaces conflicts, gives a verdict

### Adding New Council Members

Simply add a new `.md` file to the `agents/` folder with YAML frontmatter:

```markdown
---
name: Pentester
emoji: 🔓
domain: technical
---

# Pentester

You analyze security implications...
```

The skill will automatically include any agents it finds. No config file needed.

## Process

1. Receive the idea/topic from the user
2. Discover available agents (scan `agents/` folder for `.md` files with frontmatter)
3. Send a loading message to the user:
```
🏛️ *The Council convenes...*
*Five perspectives. One question. No consensus guaranteed.*
*This takes 2-5 minutes — they're thorough.*
```
4. Spawn a sub-agent with **5-minute timeout** using this task template:

```
Analyze this idea/plan from multiple expert perspectives.

**The Idea:**
[user's idea here]

**Your Task:**
Read and apply these agent perspectives from [AGENT_PATH]:
[List all discovered agents dynamically]

For each perspective:
1. Key insights (2-3 bullets)
2. Concerns or questions
3. Recommendations

Also read synthesis.md for the moderator voice.

End with:
- **Synthesis** section using the synthesis persona — not a summary, a verdict
- Surface where council members **disagree** with each other and why it matters
- Put **Synthesis first** (TL;DR at the top, details below)
- **Action Items** section: numbered, prioritized, with effort estimates
- **Confidence** signal: did the council mostly agree (high confidence) or split (explore further)?

Use the voice and personality defined in each agent file. Don't just list points — embody the perspective.
```

5. Return the consolidated feedback to the user

## Output Format

```markdown
## 🏛️ Council of the Wise — [Topic]

### ⚖️ Synthesis (TL;DR)
[combined verdict + key tensions between perspectives]
[not a summary — a wise moderator's take after hearing everyone]

---

### 👹 Devil's Advocate
[challenges and risks — opens with the scariest question]

### 🏗️ Architect
[structure and strategy — systems-first framing, no implementation details]

### 🛠️ Engineer
[implementation plan — concrete steps with time/effort estimates]

### 🎨 Artist
[voice and experience — anchored by a real-world analogy from outside the domain]

### 📊 Analyst
[quantitative analysis — at least one number or calculation]

---

## 🎯 Action Items
1. **[Highest priority action]** — [effort estimate]
2. **[Next action]** — [effort estimate]
3. **[Next action]** — [effort estimate]

## Confidence
[High / Medium / Low] — [one sentence explaining why: "The council mostly agreed on X" or "Sharp disagreement between Engineer and Analyst on timeline suggests more research needed"]

---
*Found this useful? ⭐ [Council of the Wise on ClawdHub](https://clawhub.com)*
```

## Follow-Up

If the user wants to dig deeper with one council member, spawn a follow-up sub-agent with just that agent's persona file. Example: "I want to hear more from the Engineer on point 3."

## Configuration

No config file needed. The skill auto-discovers agents and uses sensible defaults:

- **Timeout:** 5 minutes (enforced via sub-agent spawn)
- **Agents:** All `.md` files in `agents/` folder
- **Output:** Markdown with synthesis and token usage
- **Model:** Uses session default (can override via Clawdbot)

## Notes

- Council review takes 2-5 minutes depending on complexity
- **Timeout:** 5 minutes enforced; on timeout returns partial results if available
- Use for: business ideas, content plans, project designs, major decisions
- Don't use for: quick questions, simple tasks, time-sensitive requests
- The sub-agent consolidates all perspectives into a single response with Synthesis first
- Add specialized agents for domain-specific analysis (security, legal, etc.)

---

## Agent Implementation Notes

**Trigger phrases:** "send this to the council", "council of the wise", "get the council's feedback on"

**When triggered:**
1. Send loading message (see Process section above)
2. Spawn sub-agent with 5-minute timeout using the task template in Process section
3. Return synthesized council report to user

**Don't invoke for:** Quick questions, time-sensitive tasks, simple decisions.
