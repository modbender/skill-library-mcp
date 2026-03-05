# Cost Guardrails — Open Router

## Budget-First Operations

Set budget limits before scaling usage.

| Control | Why it matters | Suggested baseline |
|---------|----------------|--------------------|
| Monthly ceiling | Prevents surprise invoices | Hard cap with early warning at 70% |
| Per-task cap | Avoids expensive outliers | Maximum token budget by workload class |
| Premium-model gate | Protects high-cost models | Use only for high-impact tasks |

## Cost Review Cadence

Run a short review weekly:

1. Check top spend by workload class.
2. Identify low-value traffic using premium models.
3. Reassign low-stakes traffic to cheaper models.
4. Re-verify quality after each routing adjustment.

## Optimization Heuristics

- Use cheaper models for extraction, tagging, and repetitive transformations.
- Reserve premium models for ambiguous reasoning and high-risk decisions.
- Prefer deterministic prompts to reduce retries and token waste.
- Keep fallback chains short to avoid compounding token burn.

## Cost Trap

Cost spikes usually come from routing mistakes, not model list prices alone.
Always review task-model alignment before changing providers.
