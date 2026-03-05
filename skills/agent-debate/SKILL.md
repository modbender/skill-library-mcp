# Agent Debate Skill

Spawn multiple sub-agents to debate approaches and converge on the best solution.

## Overview

Uses parallel sub-agents with file-based coordination to simulate adversarial debate. Each agent investigates independently, writes findings, then a synthesis agent reviews all positions and picks the winner.

## Pattern: Competing Hypotheses

Best for: architecture decisions, debugging, strategy, trade analysis

### How It Works

1. **Lead defines the question** and spawns 2-4 debate agents
2. Each agent writes their position to `plans/debate-{id}/agent-{n}.md`
3. A synthesis agent reads all positions and produces a verdict
4. Lead reviews and acts on the verdict

### File Structure

```
plans/debate-{topic}/
├── question.md          # The question being debated
├── agent-1.md           # Agent 1's position
├── agent-2.md           # Agent 2's position
├── agent-3.md           # Agent 3's position (optional)
├── rebuttal-1.md        # Agent 1's rebuttal (round 2)
├── rebuttal-2.md        # Agent 2's rebuttal (round 2)
├── synthesis.md         # Final synthesis and verdict
└── decision.md          # Lead's final decision
```

### Usage

#### Single Round (Fast)
3 agents, one round, synthesis. ~5 minutes.

```
1. Write question to plans/debate-{topic}/question.md
2. Spawn 3 agents simultaneously:
   - Agent A: "Argue FOR approach X. Read plans/debate-{topic}/question.md. Write your position with evidence to plans/debate-{topic}/agent-1.md"
   - Agent B: "Argue FOR approach Y. Read plans/debate-{topic}/question.md. Write your position with evidence to plans/debate-{topic}/agent-2.md"
   - Agent C: "Argue FOR approach Z. Read plans/debate-{topic}/question.md. Write your position with evidence to plans/debate-{topic}/agent-3.md"
3. Wait for all to complete
4. Spawn synthesis agent:
   "Read all positions in plans/debate-{topic}/. Score each on: feasibility (1-10), risk (1-10), speed (1-10), quality (1-10). Write verdict to plans/debate-{topic}/synthesis.md"
```

#### Two Round (Thorough)
3 agents, position + rebuttal, synthesis. ~10 minutes.

```
Round 1: Same as single round (positions)
Round 2: Each agent reads others' positions and writes rebuttals
  - "Read all agent-*.md files. Write a rebuttal challenging the other positions. Save to rebuttal-{n}.md"
Round 3: Synthesis reads everything and decides
```

#### Red Team (Adversarial)
1 builder + 1 attacker. Best for security/robustness.

```
1. Builder: "Design/implement X. Write to plans/debate-{topic}/proposal.md"
2. Attacker: "Read proposal.md. Find every flaw, vulnerability, and edge case. Write to plans/debate-{topic}/attack.md"
3. Builder: "Read attack.md. Address each issue. Write to plans/debate-{topic}/defense.md"
4. Synthesis: "Score the final defense. Is it production-ready?"
```

## Model Assignment

- **Debate agents:** Opus 4.6 (needs deep reasoning)
- **Synthesis agent:** Opus 4.6 (needs to weigh nuanced arguments)
- **Simple positions:** Sonnet 4.5 (if cost matters and topic is straightforward)

## When To Use

✅ Architecture decisions with multiple valid approaches
✅ Debugging with unclear root cause
✅ Trading strategy evaluation
✅ Security review (red team pattern)
✅ Hackathon approach selection

❌ Simple implementation tasks
❌ Tasks with one obvious answer
❌ Sequential work with dependencies

## Example Prompts

### Architecture Debate
```
Question: "Should Nudge use Turso (SQLite) or Supabase (Postgres) for production?"
Agent 1: Argue for Turso — edge computing, simplicity, cost
Agent 2: Argue for Supabase — ecosystem, realtime, auth
Agent 3: Devil's advocate — what about a hybrid approach?
```

### Trading Strategy
```
Question: "Is ETH undervalued at current levels given macro conditions?"
Agent 1: Bull case — on-chain metrics, upcoming catalysts
Agent 2: Bear case — macro headwinds, technical levels
Agent 3: Neutral — range-bound thesis with key levels to watch
```

### Debug Investigation
```
Question: "App crashes on iOS 17 but not 18. What's the root cause?"
Agent 1: Investigate API deprecation changes
Agent 2: Investigate SwiftUI rendering pipeline differences
Agent 3: Investigate memory management changes
```

## Integration with Swarm

The debate pattern works across the swarm:
- Sprint can debate hackathon approaches
- Quant can run bull/bear/neutral analysis
- Architect can evaluate design patterns
- Any agent can spawn a debate when facing a non-obvious decision

## Future: Native Agent Teams

When OpenClaw supports Claude Code's agent teams natively:
- Agents will message each other directly (no file coordination)
- Shared task list replaces file-based progress tracking
- Lead can delegate without implementing
- This skill becomes a lightweight wrapper around native teams
