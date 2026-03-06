# Scale Diagnostic

Use this diagnostic to identify the true bottleneck before proposing a scaling plan.

## Intake Snapshot

Collect only the minimum needed to frame the problem:
- Scale target: what must increase and by how much
- Timeline: by when the target must be reached
- Constraint floor: budget, headcount, reliability, compliance
- Current baseline: throughput, failure rate, cycle time, or revenue

## Bottleneck Classification

Classify the dominant bottleneck now:
- Demand bottleneck: not enough qualified demand
- Capacity bottleneck: demand exists, production or delivery cannot keep up
- Coordination bottleneck: handoffs and dependencies create delay
- Quality bottleneck: rework and incidents consume growth capacity
- Decision bottleneck: unclear ownership slows execution

Pick one primary bottleneck. Secondary bottlenecks are tracked but not optimized first.

## Evidence Threshold

Require evidence before recommending high-cost changes:
- Trend data over at least two periods
- Queue depth or wait-time proof
- Failure or defect pattern showing repeated impact
- Opportunity cost estimate of current constraint

If evidence is weak, propose a low-cost measurement sprint first.

## Output Contract

Every diagnostic output must include:
- Bottleneck statement in one sentence
- Measurable objective and deadline
- Top three leverage candidates with tradeoffs
- First test with success and rollback criteria
