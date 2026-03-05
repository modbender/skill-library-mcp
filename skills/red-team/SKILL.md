---
name: red-team
description: >
  Adversarial multi-agent debate engine for stress-testing decisions, ideas, and strategies.
  Orchestrates multiple AI agents with conflicting worldviews (bull, bear, operator, contrarian, etc.)
  to debate a question through structured rounds, then synthesizes results into a decision brief.
  Use for: red team analysis, adversarial debate, stress testing ideas, devil's advocate,
  "what could go wrong" analysis, decision validation, pre-mortem exercises.
---

# Red Team — Adversarial Debate Engine

Stress-test any decision by having AI agents with conflicting worldviews debate it.

## Prerequisites

One of these coding agent CLIs (uses your existing subscription — no API key needed):
- **Claude Code** (default): `claude` — `npm i -g @anthropic-ai/claude-code`
- **Codex**: `codex` — `npm i -g @openai/codex`
- **Gemini**: `gemini` — `npm i -g @google/gemini-cli`

No Python dependencies beyond the standard library.

## Quick Start

```bash
# Basic 3-persona debate (uses Max subscription via claude CLI)
python3 ~/.openclaw/skills/red-team/scripts/red-team.py \
  --question "Should we do X?" \
  --personas "bull,bear,operator"

# Full debate with context and output file
python3 ~/.openclaw/skills/red-team/scripts/red-team.py \
  -q "Should we invest $50k in this deal?" \
  -p "bull,bear,cash-flow,local-realist" \
  -r 3 \
  -c /path/to/deal-data.md \
  -o /tmp/red-team-result.md

# Use a different model
python3 ~/.openclaw/skills/red-team/scripts/red-team.py \
  -q "Should we launch this product?" \
  -p "bull,customer,operator" \
  -m opus

# List all available personas
python3 ~/.openclaw/skills/red-team/scripts/red-team.py --list-personas
```

## How to Use (as OpenClaw Agent)

When the user asks you to "red team" something, "stress test" an idea, play "devil's advocate", or asks "what could go wrong":

1. Identify the question/decision from the user's message
2. Choose appropriate personas (default: bull,bear,operator — adjust based on domain)
3. Run the script and save output
4. Summarize the key findings to the user, share the full report if requested

**Persona selection guide:**
- Investment/financial decisions → bull, bear, cash-flow, economist
- Product/startup ideas → bull, customer, operator, technologist
- Legal/compliance questions → regulator, bear, operator
- Strategy/direction → contrarian, economist, historian, bull
- General "should we do X?" → bull, bear, operator (good default)

## Available Personas

| Key | Name | Worldview |
|-----|------|-----------|
| bull | The Bull | Optimistic, opportunity-focused |
| bear | The Bear | Risk-averse, capital preservation |
| contrarian | The Contrarian | Oppositional, consensus-challenging |
| operator | The Operator | Execution-focused pragmatist |
| economist | The Economist | Macro trends, opportunity cost |
| local-realist | The Local Realist | Ground truth, local specifics |
| cash-flow | The Cash Flow Analyst | Income, carrying costs, IRR |
| regulator | The Regulator | Compliance, legal risk |
| technologist | The Technologist | Automation, scalability |
| customer | The Customer | End-user demand, willingness to pay |
| ethicist | The Ethicist | Moral implications, stakeholder impact |
| historian | The Historian | Historical patterns, precedent |

## Custom Personas

Create a JSON file:

```json
{
  "my-persona": {
    "name": "The Skeptic",
    "description": "Questions everything, trusts nothing",
    "system": "You are The Skeptic — you question every assumption..."
  }
}
```

Use with `--custom-personas /path/to/file.json`. Custom personas merge with built-ins.

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--question`, `-q` | required | The question to debate |
| `--personas`, `-p` | bull,bear,operator | Comma-separated persona keys |
| `--rounds`, `-r` | 2 | Number of critique rounds |
| `--output`, `-o` | stdout | Output file path |
| `--context-file`, `-c` | none | Additional context file |
| `--custom-personas` | none | Custom personas JSON |
| `--model`, `-m` | sonnet | Model alias (sonnet, opus, haiku, gpt-4o, etc.) |
| `--backend`, `-b` | claude | CLI backend: claude, codex, or gemini |
| `--list-personas` | — | List personas and exit |

## Output Structure

The output is a markdown document with:
1. **Initial Proposals** — Each agent's independent take
2. **Critique Rounds** — Agents critique each other
3. **Refinement** — Agents update positions based on critiques
4. **Conviction Scores** — Each agent scores all positions (0-100)
5. **Synthesis & Decision Brief** — Neutral agent produces:
   - Executive summary
   - Consensus points
   - Key disagreements
   - Risk matrix
   - Conviction score summary
   - Synthesized recommendation
   - Next steps

## When to Use

✅ **Good for:** Important decisions, investment analysis, product strategy, "go/no-go" calls, pre-mortems, challenging groupthink

❌ **Not for:** Simple factual questions, time-sensitive emergencies, decisions already made, emotional/personal choices

## Integration Tips

- Save output to memory files for future reference
- Create BEADS tasks from the "Next Steps" section
- Feed context files from Obsidian or project docs
- Re-run with different personas for different perspectives
- Use `--rounds 1` for quick takes, `--rounds 3` for deep analysis
