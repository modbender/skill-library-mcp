# Credit Score System

## Overview

AgentGuard now includes a **Credit Score System** that calculates reputation scores for AI agents based on their behavior history.

## Quick Start

```bash
# Get credit score for an agent
agentguard credit score my-agent

# Get full credit report
agentguard credit report my-agent

# Rank all agents
agentguard credit rank

# Compare multiple agents
agentguard credit compare agent1 agent2 agent3
```

## Credit Score Tiers

| Tier | Score | Name | Emoji | Meaning |
|------|-------|------|-------|---------|
| **S** | 90-100 | 卓越 | 🏆 | Excellent, trusted for critical tasks |
| **A** | 80-89 | 优秀 | ⭐ | Very good, can automate |
| **B** | 70-79 | 良好 | ✓ | Good, standard permissions |
| **C** | 60-69 | 一般 | ○ | Average, limited permissions |
| **D** | 50-59 | 及格 | △ | Passing, needs oversight |
| **F** | 0-49 | 危险 | ⚠️ | Dangerous, strict limits |

## Scoring Factors

| Factor | Impact | Description |
|--------|--------|-------------|
| Task Success | +10 | Successfully completed operations |
| Task Failure | -20 | Failed operations |
| Approval Granted | +5 | Human approved requests |
| Approval Denied | -10 | Human denied requests |
| Credential Access | +1 | Accessed credentials (logged) |
| Dangerous Operation | -5 | Required human approval |
| Days Active | +2/day | Agent account age |
| Human Interaction | +3 | Interactions with humans |

## Initial Score

All agents start with **50 points** (D tier) and earn/lose points based on behavior.

## API Usage

```javascript
const AgentGuard = require('agentguard');

const guard = new AgentGuard({ masterPassword: 'xxx' });
await guard.init();

// Get credit score
const score = await guard.getCreditScore('my-agent', 30); // last 30 days

console.log(`Score: ${score.score}/100`);
console.log(`Tier: ${score.tier.name} (${score.tier.level})`);

// Get full report
const report = await guard.getCreditReport('my-agent', 30);

console.log('Recommendation:', report.recommendation.message);
console.log('Can Automate:', report.recommendation.canAutomate);

// Compare agents
const ranking = await guard.compareCreditScores(['agent1', 'agent2', 'agent3'], 30);

// Get all agent rankings
const allRankings = await guard.getAgentRankings(30);
```

## Credit Report Structure

```javascript
{
  report: {
    title: 'Agent Credit Report',
    generatedAt: '2026-03-01T11:41:00.000Z',
    period: '30 days'
  },
  agent: {
    id: 'my-agent',
    owner: 'user@example.com',
    createdAt: '2026-03-01T10:00:00.000Z',
    status: 'active',
    permissionLevel: 'write'
  },
  credit: {
    score: 85,
    tier: {
      level: 'A',
      name: '优秀',
      color: 'green',
      emoji: '⭐'
    },
    rating: '⭐ 优秀 (A)'
  },
  statistics: {
    daysActive: 30,
    taskSuccess: 15,
    taskFailure: 2,
    approvalsGranted: 5,
    approvalsDenied: 1,
    dangerousOps: 8,
    credentialAccess: 20
  },
  factors: [
    { factor: 'taskSuccess', impact: 150, count: 15 },
    { factor: 'taskFailure', impact: -40, count: 2 },
    ...
  ],
  recommendation: {
    level: 'low_risk',
    message: '该智能体信誉良好，可放心委托重要任务',
    canAutomate: true,
    suggestedPermissions: ['admin']
  }
}
```

## Use Cases

### 1. Trust Decisions
```javascript
const score = await guard.getCreditScore('unknown-agent');

if (score.score >= 80) {
  // High trust: allow automation
  await executeWithoutApproval();
} else if (score.score >= 60) {
  // Medium trust: require approval
  await requestApproval();
} else {
  // Low trust: deny
  throw new Error('Agent reputation too low');
}
```

### 2. Dynamic Permissions
```javascript
const score = await guard.getCreditScore('my-agent');

// Adjust permissions based on score
if (score.score >= 90) {
  await guard.setPermissionLevel('my-agent', 'admin');
} else if (score.score >= 70) {
  await guard.setPermissionLevel('my-agent', 'write');
} else {
  await guard.setPermissionLevel('my-agent', 'read');
}
```

### 3. Marketplace Integration
```javascript
// In an agent marketplace
const rankings = await guard.getAgentRankings(30);

// Display top agents
for (const agent of rankings.ranking.slice(0, 10)) {
  console.log(`${agent.tier.emoji} ${agent.agentId}: ${agent.score}/100`);
}
```

## Best Practices

1. **Monitor Regularly**: Check credit scores weekly
2. **Investigate Drops**: Sudden score drops indicate problems
3. **Reward Good Behavior**: High scores should unlock privileges
4. **Automate Based on Trust**: Use scores for automation decisions

---

*Credit Score: The FICO score for AI agents*
