---
name: Agent Ops Runbook
description: Generate a production-ready operations runbook for deploying AI
  agents. Covers pre-deployment checklists, shadow mode → supervised →
  autonomous rollout stages, monitoring dashboards, rollback proce...
---

# Agent Ops Runbook

Generate a production-ready operations runbook for deploying AI agents. Covers pre-deployment checklists, shadow mode → supervised → autonomous rollout stages, monitoring dashboards, rollback procedures, cost management, and incident response templates.

## When to Use
- Deploying an AI agent to production
- Building monitoring and alerting for agent systems
- Creating rollback procedures for autonomous workflows
- Estimating and controlling agent operational costs

## Instructions

When the user asks for an agent ops runbook or deployment plan:

1. Ask which agent function they're deploying (support, sales, document processing, etc.)
2. Ask about their risk tolerance (conservative, moderate, aggressive rollout)
3. Generate a complete runbook with:
   - Pre-deployment checklist specific to their function
   - 3-stage rollout plan with metrics and gates
   - Monitoring alerts (critical + warning thresholds)
   - Rollback procedures (3 levels: prompt, feature, full)
   - Cost estimates based on their expected volume
   - 90-day implementation timeline
   - Incident response template

4. Include specific metric targets:
   - Accuracy vs human baseline: >90%
   - Error rate: <2%
   - Cost per task benchmarks by function
   - Human escalation rate: 5-15%

5. Flag risks specific to their industry (compliance, PII, financial accuracy)

Output format: Markdown document ready to share with engineering and ops teams.
