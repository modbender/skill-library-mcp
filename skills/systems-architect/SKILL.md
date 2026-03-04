---
name: Systems Architect
description: Design infrastructure, networks, and cloud systems with integration, reliability, and security patterns.
metadata: {"clawdbot":{"emoji":"🌐","os":["linux","darwin","win32"]}}
---

# Systems Architecture Rules

## Infrastructure Design
- Design for failure at every layer — hardware fails, networks partition, regions go down
- Redundancy costs money, downtime costs more — calculate acceptable risk
- Prefer managed services for undifferentiated work — run less, build more
- Infrastructure as code from day one — manual changes drift and break
- Immutable infrastructure beats patching — replace, don't repair

## Cloud Architecture
- Multi-AZ minimum, multi-region for critical systems — availability zones fail together sometimes
- Right-size first, auto-scale second — baseline must be correct
- Reserved capacity for steady load, spot/preemptible for bursts — cost optimization requires planning
- Egress costs add up — keep traffic within regions when possible
- Cloud vendor lock-in is real — abstract where escape matters, accept where it doesn't

## Networking
- Private subnets for workloads, public only for load balancers — minimize attack surface
- VPC peering and transit gateways for multi-account — plan topology before scaling
- DNS for service discovery — hardcoded IPs break migrations
- Zero trust: authenticate and encrypt internal traffic — perimeter security isn't enough
- Network segmentation limits blast radius — flat networks let attackers roam

## Integration Patterns
- APIs for synchronous, queues for asynchronous — match pattern to requirements
- Event-driven for loose coupling — producers don't know consumers
- Service mesh for complex microservices — observability and security at network layer
- Rate limiting and backpressure protect systems — don't let slow consumers crash fast producers
- Dead letter queues for failed messages — don't lose data, process later

## Reliability
- Define SLOs before building — what does "up" mean for this system?
- Error budgets allow controlled risk — 99.9% means 8 hours downtime per year is acceptable
- Blast radius reduction: cell-based architecture — limit how many users one failure affects
- Chaos engineering in staging first — break things intentionally before production breaks accidentally
- Runbooks for every alert — 3 AM isn't debugging time

## Disaster Recovery
- RTO (recovery time) and RPO (data loss) are business decisions — architect for the requirement
- Backups aren't recovery until tested — restore regularly
- Hot/warm/cold standby each have trade-offs — cost vs speed of recovery
- Cross-region replication for critical data — single region is single point of failure
- DR drills reveal real problems — plan meets reality

## Security
- Defense in depth: multiple barriers — one layer will fail
- Least privilege for services too — not just users
- Secrets management centralized — no secrets in code, config files, or environment variables in images
- Audit logging for compliance and forensics — you'll need it after a breach
- Patch aggressively — known vulnerabilities are actively exploited

## Monitoring and Observability
- Metrics, logs, and traces together — each tells part of the story
- Alerting on symptoms, not causes — users down matters, CPU high might not
- Dashboards for each service with golden signals — latency, traffic, errors, saturation
- Distributed tracing across services — follow requests end to end
- Log aggregation with retention policy — balance cost and forensic needs

## Capacity Planning
- Measure current baseline before projecting — can't scale what you don't measure
- Load test to find breaking points — theory differs from reality
- Capacity leads demand — scaling takes time, be ahead
- Cost modeling for growth scenarios — 10x users is rarely 10x cost
- Review quarterly at minimum — patterns change

## Migration and Evolution
- Strangler fig pattern for legacy replacement — route traffic gradually
- Blue-green or canary for infrastructure changes — test in production safely
- Database migrations are hardest — plan data migration separately
- Rollback plans before rollout — assume failure, prepare for it
- Communicate maintenance windows — surprises damage trust
