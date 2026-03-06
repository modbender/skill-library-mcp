# 🎭 Arena System

Adversarial self-improvement framework for AI agents. Reduces hallucinations by making the same agent argue with itself.

## Concept

Give one agent two roles:
- **Agent** - Does the work, writes reports
- **Anti-Agent** - Questions everything, writes counter-reports

When one writes a report, the other critiques it. The loop continues until you say stop.

## Why?

AI agents are overconfident. They'll say "this strategy has 80% win rate" without questioning their own assumptions. Arena forces them to ask "but is that really true?"

## Installation

```bash
./setup.sh ~/my-arena
```

This creates:
```
my-arena/
├── state.json           # Loop state
├── prompts/
│   ├── agent.md         # Main agent prompt
│   └── anti-agent.md    # Critic prompt
└── outputs/             # Reports go here
```

## Usage

Add to your `HEARTBEAT.md`:
```markdown
## Arena Loop
1. Read state.json → whose turn?
2. Run that persona's prompt
3. Write output to outputs/{role}/iteration_N.md
4. Switch turns, increment iteration
5. Save state
```

## Configuration

`state.json`:
```json
{
  "current_turn": "agent",
  "iteration": 0,
  "topic": "my-trading-bot",
  "active": true,
  "max_iterations": 10
}
```

## Use Cases

- Trading strategy development
- Code review
- Risk assessment
- Any task where self-critique helps

## Limitations

- 2x token cost (two personas = two LLM calls)
- Same model = same biases (not a true second opinion)
- Can lead to analysis paralysis if anti-agent is too aggressive

## Results

In testing: prevented 2 premature live deployments, caught 3 bugs, saved money by forcing proper paper trading first.
