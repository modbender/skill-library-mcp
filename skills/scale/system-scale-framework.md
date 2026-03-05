# System Scale Framework

Apply this when scaling infrastructure, platform services, data pipelines, or operational throughput.

## Sequence

### 1. Stabilize Before Expanding
- Define SLO and error budget baseline
- Remove known single points of failure
- Ensure observability exists for latency, errors, saturation, and traffic

### 2. Remove Queueing Hotspots
- Identify top queues and slowest dependency chain
- Add backpressure and admission control before adding raw capacity
- Reduce noisy neighbor effects using isolation or workload partitioning

### 3. Scale Capacity in Layers
- Optimize current tier first (caching, indexes, batching)
- Scale horizontally only when vertical tuning plateaus
- Add regional or cell-based partitioning only when blast radius justifies it

### 4. Control Cost and Reliability Together
- Track unit cost per request or workload
- Pair throughput improvements with reliability guardrails
- Reject scale plans that improve one while silently degrading the other

### 5. Roll Out in Bounded Stages
- Canary first, then segment expansion, then full rollout
- Define rollback trigger before deployment
- Log incident learnings into next iteration

## Red Flags

- Throughput increases while p95 and p99 collapse.
- Capacity added without load-shape analysis.
- Complex distributed patterns introduced without ownership model.
