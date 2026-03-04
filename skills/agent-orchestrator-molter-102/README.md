# Agent Orchestrator

Multi-agent orchestration with 5 proven patterns - Work Crew, Supervisor, Pipeline, Council, and Auto-Routing

Multi-agent orchestration for OpenClaw with 5 proven patterns:
- **Crew** (parallel workers)
- **Supervisor** (dynamic decomposition)
- **Pipeline** (staged workflows)
- **Council** (multi-expert deliberation)
- **Route** (auto-classification to specialists)

## Why this exists
Most agent work is either:
1) too simple for orchestration, or
2) complex enough that single-agent output is brittle.

This skill gives a practical middle path: use orchestration only when the quality/speed gain justifies the overhead.

## Quick start

```bash
# Route a task automatically
claw agent-orchestrator route --task "Write Python parser for CSV anomalies"

# Parallel research with convergence
claw agent-orchestrator crew \
  --task "Research Lightning adoption in 2026" \
  --agents 4 \
  --perspectives technical,business,security,competitors \
  --converge consensus

# Staged pipeline
claw agent-orchestrator pipeline \
  --config skills/agent-orchestrator/examples/content-pipeline.json \
  --input "Topic: value-for-value monetization"
```

## Usage examples
See:
- `SKILL.md` for decision matrix and full command reference
- `examples/README.md` for pipeline config structure
- `examples/content-pipeline.json` for a complete staged workflow

## Outcomes this is designed to improve
- Better confidence on high-stakes tasks (cross-checking perspectives)
- Faster wall-clock completion on parallelizable work
- Cleaner structure for multi-stage deliverables
- Less manual triage when task types vary (auto-routing)

## Cost warning
Multi-agent orchestration can use substantially more tokens than a single-agent run. Use it for high-value tasks where reliability or speed matters.

## Security / publish safety
- No secrets should ever be stored in skill files.
- Keep runtime state out of publication artifacts.
- Use `.clawhubignore` in this directory before publish.
- See `SECURITY.md` for threat model, mitigations, and residual risk.

## Changelog
See `CHANGELOG.md`.
