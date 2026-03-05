# 🔴 Red Team — Adversarial Multi-Agent Debate Engine

Stress-test any decision by having AI agents with conflicting worldviews debate it through structured rounds, then synthesize results into an actionable decision brief.

Inspired by [Conclave](https://conclave.sh)'s adversarial idea markets — but local, private, and integrated with your existing AI coding subscriptions.

## How It Works

You pose a question. The engine spawns multiple AI "agents" — each with a distinct worldview (optimist, pessimist, pragmatist, regulator, etc.) — and runs them through a structured debate:

```
📋 Proposals → ⚔️ Critiques → 🔄 Refinement → 📊 Conviction Scores → 📝 Synthesis
```

1. **Proposals** — Each agent independently analyzes the question from their perspective
2. **Critiques** — Each agent critiques the others' proposals (configurable rounds)
3. **Refinement** — Each agent updates their position incorporating valid critiques
4. **Conviction Scoring** — Each agent scores all positions (0-100)
5. **Synthesis** — A neutral agent produces a structured decision brief with executive summary, risk matrix, consensus points, and recommendation

## Quick Start

```bash
# Install (via ClawHub)
clawhub install red-team

# Basic 3-persona debate
python3 scripts/red-team.py \
  -q "Should we pivot our B2B SaaS to a marketplace model?" \
  -p "bull,bear,operator"

# Full debate with context file and output
python3 scripts/red-team.py \
  -q "Should we invest $50k in this property?" \
  -p "bull,bear,cash-flow,local-realist,regulator" \
  -r 2 \
  -c deal-data.md \
  -o analysis.md

# Use Codex instead of Claude
python3 scripts/red-team.py \
  -q "Should we open-source our core product?" \
  -p "bull,bear,customer,technologist" \
  -b codex

# List all available personas
python3 scripts/red-team.py --list-personas
```

## Requirements

One of these coding agent CLIs (uses your existing subscription — no API key needed):

| Backend | CLI | Install | Flag |
|---------|-----|---------|------|
| **Claude Code** (default) | `claude` | `npm i -g @anthropic-ai/claude-code` | `-b claude` |
| **Codex** | `codex` | `npm i -g @openai/codex` | `-b codex` |
| **Gemini** | `gemini` | `npm i -g @google/gemini-cli` | `-b gemini` |

No Python dependencies beyond the standard library.

## Built-in Personas

| Key | Name | Worldview |
|-----|------|-----------|
| `bull` | The Bull | Optimistic, opportunity-focused, action-biased |
| `bear` | The Bear | Risk-averse, capital preservation, danger-sensing |
| `contrarian` | The Contrarian | Deliberately oppositional, consensus-challenging |
| `operator` | The Operator | Execution-focused pragmatist, complexity-aware |
| `economist` | The Economist | Macro trends, cycles, opportunity cost |
| `local-realist` | The Local Realist | Ground truth, boots-on-the-ground reality |
| `cash-flow` | The Cash Flow Analyst | Income-focused, carrying costs, time-value of money |
| `regulator` | The Regulator | Compliance, legal risk, regulatory exposure |
| `technologist` | The Technologist | Automation, scalability, data advantages |
| `customer` | The Customer | End-user demand, willingness to pay |
| `ethicist` | The Ethicist | Moral implications, stakeholder impact |
| `historian` | The Historian | Historical patterns, precedent, analogy |

### Persona Selection Guide

| Decision Type | Recommended Personas |
|---------------|---------------------|
| Investment / financial | `bull,bear,cash-flow,economist` |
| Product / startup | `bull,customer,operator,technologist` |
| Legal / compliance | `regulator,bear,operator` |
| Strategy / direction | `contrarian,economist,historian,bull` |
| General "should we?" | `bull,bear,operator` |

## Custom Personas

Create a JSON file with your own:

```json
{
  "vc": {
    "name": "The VC",
    "description": "Pattern-matching investor, thinks in TAM and moats",
    "system": "You are a venture capitalist evaluating this as a potential investment. You think in terms of total addressable market, defensibility, team capability, and unit economics..."
  }
}
```

```bash
python3 scripts/red-team.py -q "..." --custom-personas my-personas.json -p "vc,bear,customer"
```

Custom personas merge with built-ins — you can mix and match.

## Output Format

The output is a structured markdown document:

- **Initial Proposals** — Each agent's independent position
- **Critique Rounds** — Agents critique each other's proposals
- **Refinement** — Updated positions incorporating valid critiques
- **Conviction Scores** — Each agent rates all positions (0-100)
- **Synthesis & Decision Brief:**
  - Executive summary (2-3 sentences)
  - Consensus points
  - Key disagreements
  - Risk matrix (risk / likelihood / impact / mitigation)
  - Conviction score summary
  - Synthesized recommendation
  - Concrete next steps

## CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `-q`, `--question` | *(required)* | The question or decision to debate |
| `-p`, `--personas` | `bull,bear,operator` | Comma-separated persona keys |
| `-r`, `--rounds` | `2` | Number of critique rounds |
| `-o`, `--output` | stdout | Output file path |
| `-c`, `--context-file` | — | Additional context file (included in every prompt) |
| `-m`, `--model` | `sonnet` | Model alias (sonnet, opus, haiku, gpt-4o, etc.) |
| `-b`, `--backend` | `claude` | CLI backend: `claude`, `codex`, or `gemini` |
| `--custom-personas` | — | Path to custom personas JSON file |
| `--list-personas` | — | List available personas and exit |

## Performance

- Each agent call takes ~30-60 seconds (CLI startup + generation)
- A 3-persona, 1-round debate ≈ 5-8 minutes
- A 5-persona, 2-round debate ≈ 15-20 minutes
- Uses your existing subscription (Max, Pro, etc.) — no separate API costs

## When to Use

✅ **Good for:** Important decisions, investment analysis, product strategy, go/no-go calls, pre-mortems, challenging groupthink, due diligence

❌ **Not for:** Simple factual questions, time-sensitive emergencies, decisions already made, emotional/personal choices

## License

MIT
