---
name: agent-orchestrator
version: 1.0.2
author: molter-white
description: Multi-agent orchestration with 5 proven patterns - Work Crew, Supervisor, Pipeline, Council, and Auto-Routing
license: MIT
tags: multi-agent,orchestration,automation,productivity,ai-workflow
compatibility: OpenClaw 0.8+
---

# agent-orchestrator

Multi-agent orchestration for OpenClaw. Implements 5 proven patterns for coordinating multiple AI agents: Work Crew, Supervisor, Pipeline, Expert Council, and Auto-Routing.

**USE WHEN:**
- A task can be parallelized for speed or redundancy (Work Crew)
- Complex tasks need dynamic planning and delegation (Supervisor)
- Work follows a predictable sequence of stages (Pipeline)
- Cross-domain input is needed from multiple specialists (Expert Council)
- Mixed task types need automatic routing to appropriate specialists (Auto-Routing)
- Research tasks require breadth-first exploration of multiple angles
- High-stakes decisions need confidence through multiple perspectives

**DON'T USE WHEN:**
- Simple tasks that fit in one agent's context window (use main session instead)
- Sequential tasks with no parallelization opportunity (use regular tool calls)
- One-shot deterministic tasks (use single agent)
- Tasks requiring real-time inter-agent conversation (this uses async spawning)
- Tasks where 15x token cost cannot be justified
- Quick/simple tasks where coordination overhead exceeds benefit

**Outputs:**
- Aggregated results from multiple parallel agents
- Synthesized consensus recommendations
- Routing decisions to appropriate specialists
- Structured output from staged processing

## Decision Matrix

| Pattern | Use When | Avoid When |
|---------|----------|------------|
| **crew** | Same task from multiple angles, verification, research breadth | Results cannot be easily compared/merged |
| **supervise** | Dynamic decomposition needed, complex planning | Fixed workflow, simple delegation |
| **pipeline** | Well-defined sequential stages, content creation | Path needs runtime adaptation |
| **council** | Cross-domain expertise, risk assessment, policy review | Single-domain task, need fast consensus |
| **route** | Mixed workload types, automatic classification | Task type is already known |

## Auto-Routing Pattern

The route command analyzes tasks and automatically classifies them by type, then routes to the appropriate specialist:

```bash
# Basic routing
claw agent-orchestrator route --task "Write Python parser"

# With custom specialist pool
claw agent-orchestrator route \
  --task "Analyze data and create report" \
  --specialists "analyst,data,writer"

# Force specific specialist
claw agent-orchestrator route \
  --task "Something complex" \
  --force coder
```

### Confidence Thresholds

- **High confidence (>0.85)**: Auto-route immediately
- **Good confidence (0.7-0.85)**: Propose with confirmation option
- **Moderate confidence (0.5-0.7)**: Show top alternatives
- **Low confidence (<0.5)**: Request clarification

Available specialists: coder, researcher, writer, analyst, planner, reviewer, creative, data, devops, support

## Common Workflows

```bash
# Parallel research with consensus
claw agent-orchestrator crew \
  --task "Research Bitcoin Lightning 2026 adoption" \
  --agents 4 \
  --perspectives technical,business,security,competitors \
  --converge consensus

# Best-of redundancy for critical analysis
claw agent-orchestrator crew \
  --task "Audit this smart contract for vulnerabilities" \
  --agents 3 \
  --converge best-of

# Supervisor-managed code review
claw agent-orchestrator supervise \
  --task "Refactor authentication module" \
  --workers coder,reviewer,tester \
  --strategy adaptive

# Staged content pipeline
claw agent-orchestrator pipeline \
  --stages research,draft,review,finalize \
  --input "topic: AI agent adoption trends"

# Expert council for decision
claw agent-orchestrator council \
  --question "Should we publish this blog post about unreleased features?" \
  --experts skeptic,ethicist,strategist \
  --converge consensus \
  --rounds 2

# Auto-route mixed tasks
claw agent-orchestrator route \
  --task "Write Python function to analyze CSV data" \
  --specialists coder,researcher,writer,analyst

# Force route to specific specialist
claw agent-orchestrator route \
  --task "Debug authentication error" \
  --force coder \
  --confidence-threshold 0.9

# Route and output as JSON for scripting
claw agent-orchestrator route \
  --task $TASK \
  --format json \
  --specialists "coder,data,analyst"
```

## Negative Examples

**DON'T: Use crew for simple single-answer questions**
```bash
# WRONG: Wasteful for simple facts
claw agent-orchestrator crew --task "What is 2+2?" --agents 3

# RIGHT: Use main session directly
What is 2+2?
```

**DON'T: Use supervise when pipeline suffices**
```bash
# WRONG: Over-engineering fixed workflows
claw agent-orchestrator supervise --task "Draft, edit, publish"

# RIGHT: Use pipeline for fixed sequences
claw agent-orchestrator pipeline --stages draft,edit,publish
```

**DON'T: Route when task type is obvious**
```bash
# WRONG: Unnecessary classification overhead
claw agent-orchestrator route --task "Write Python code"

# RIGHT: Direct to appropriate specialist
claw agent-orchestrator crew --pattern code --task "Write Python code"
```

**DON'T: Use multi-agent for very small context tasks**
```bash
# WRONG: Coordination overhead exceeds value
claw agent-orchestrator crew --task "Fix typo" --agents 2

# RIGHT: Single agent or direct edit
edit file.py "typo" "correct"
```

## Token Cost Warning

Multi-agent patterns use approximately 15x more tokens than single-agent interactions. Use only for high-value tasks where quality improvement justifies the cost. See Anthropic research: token usage explains 80% of performance variance in complex tasks.

## Dependencies

- Python 3.8+
- OpenClaw sessions_spawn capability
- OpenClaw sessions_list capability
- OpenClaw sessions_history capability

## Files

- `__main__.py` - CLI entry point
- `crew.py` - Work Crew pattern implementation
- `supervise.py` - Supervisor pattern (Phase 2)
- `council.py` - Expert Council pattern (Phase 2)
- `pipeline.py` - Pipeline pattern (Phase 2)
- `route.py` - Auto-Routing pattern (Phase 2)
- `utils.py` - Shared utilities for session management

## Status

- MVP: Work Crew pattern implemented
- **Phase 2: 100% Complete**
  - [x] Supervisor pattern implemented - dynamic task decomposition and worker delegation
  - [x] Pipeline pattern implemented - sequential staged processing with validation gates
  - [x] Council pattern implemented - multi-expert deliberation with convergence methods
  - [x] Route pattern implemented - intelligent task classification and specialist routing

## References

- Anthropic Multi-Agent Research System
- LangGraph Supervisor Pattern
- CrewAI Framework
- AutoGen Conversational Agents
