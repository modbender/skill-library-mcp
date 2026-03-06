# Beszel Deployment Patterns

## Goal

Choose a topology that gives reliable monitoring signals while keeping management overhead predictable.

## Pattern A: Single Host Baseline

Use when:
- One primary server hosts most critical workloads.
- User wants fastest path to first useful alerts.

Guidelines:
- Start with one hub and one agent in the same environment.
- Validate CPU, memory, disk, and uptime reporting before adding more nodes.
- Define ownership for each alert stream immediately.

## Pattern B: Hub Plus Remote Agents

Use when:
- Multiple servers or sites must be monitored.
- Operations are distributed across teams or networks.

Guidelines:
- Add agents incrementally and verify each one before onboarding the next.
- Keep network exposure narrow and review node-level permissions.
- Tag nodes by environment to separate production and non-production noise.

## Pattern C: Staged Expansion

Use when:
- Current setup is unstable or alert fatigue already exists.
- Team needs confidence before broad rollout.

Guidelines:
- Start with the highest-risk systems first.
- Capture one week of baseline behavior before tightening thresholds.
- Require rollback notes for every topology change.

## Decision Checklist

- Which incidents are most expensive if detected late?
- Which nodes need immediate coverage vs later onboarding?
- Who owns first response and escalation?
- What rollback path exists for each deployment change?
