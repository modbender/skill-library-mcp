---
name: agentgate-security
displayName: AgentGate - Enterprise Security Firewall for OpenClaw
version: 1.0.0
author: AgentGate
website: https://agent-gate-rho.vercel.app
tags: [security, guardrails, authorization, enterprise, firewall, ai-agent]
---

# AgentGate - Enterprise Security Firewall for OpenClaw

AgentGate is a real-time policy enforcement layer that intercepts every tool call your OpenClaw agent makes before it executes. It evaluates the call against human-defined regex-based rules stored in Firestore and returns one of three decisions: ALLOW, DENY, or REQUIRE_APPROVAL.

## Why this exists

OpenClaw agents operate with full tool access by default. A single hallucination can cause the agent to run rm -rf, send unauthorized emails, issue Stripe API calls, push broken code to production, or exfiltrate data to external endpoints. AgentGate intercepts every tool call before execution.

## Architecture

AgentGate wraps the agent executeTool method using a middleware pattern. On every tool invocation it sends a POST request to the AgentGate Firebase Cloud Function with the agent API key, tool name, and serialized arguments. The function validates the key, evaluates regex policies, writes to the audit log, and returns the decision in under 80ms.

## Decision types

ALLOW: Tool executes normally.
DENY: Tool is blocked. Agent receives structured error: "AgentGate: Action blocked by policy [policy_id]. Do not retry."
REQUIRE_APPROVAL: Execution paused. Telegram webhook fires to operator with Approve/Deny buttons. Agent polls Firestore every 2 seconds for up to 5 minutes.

## Supported tool types
- bash: shell command execution
- browser: Playwright-based web automation
- fetch: outbound HTTP requests
- fs: filesystem read and write
- email: SMTP and SendGrid integrations
- stripe: payment API calls

## Policy format

agentId: string
toolName: string (e.g. "bash")
condition: string (regex evaluated against JSON.stringify(args))
ruleType: "ALLOW" | "DENY" | "REQUIRE_APPROVAL"
priority: integer (lower = evaluated first)

Example - block destructive bash commands:
toolName: "bash"
condition: "rm\\s+-rf|DROP\\s+TABLE"
ruleType: "DENY"

Example - require approval for Stripe charges over $100:
toolName: "stripe"
condition: "\"amount\":\\s*[1-9][0-9]{4,}"
ruleType: "REQUIRE_APPROVAL"

Example - whitelist-only outbound fetch:
toolName: "fetch"
condition: "^(?!.*(api\\.github\\.com|agent-gate-rho\\.vercel\\.app)).*$"
ruleType: "DENY"

## SDK usage

npm install @agentgate/openclaw-guard

import OpenClaw from 'openclaw';
import { withAgentGate } from '@agentgate/openclaw-guard';

const agent = new OpenClaw({ model: 'claude-3-5-sonnet', tools: ['bash', 'browser', 'fetch'] });

const securedAgent = withAgentGate(agent, {
  apiKey: process.env.AGENTGATE_API_KEY,
  endpoint: 'https://agent-gate-rho.vercel.app/api/evaluate-action',
  onDeny: (toolName, args, policyId) => console.log('Blocked:', toolName, policyId),
  onApprovalRequired: (toolName, args) => console.log('Awaiting approval:', toolName)
});

await securedAgent.run('Research competitors and update the CRM');

## Dashboard

https://agent-gate-rho.vercel.app provides:
- Agent management and API key rotation
- AI Policy Wizard: describe rules in plain English, Gemini generates the regex
- Real-time audit log via Firestore onSnapshot
- Approval queue with one-click approve or deny

## Getting started

1. Sign up free at https://agent-gate-rho.vercel.app
2. Create an agent and copy the API key
3. npm install @agentgate/openclaw-guard
4. Wrap your agent with withAgentGate
5. Define policies in the dashboard using the AI Wizard
6. Watch the real-time audit log as your agent runs

## Pricing

Free: 1 agent, 500 evaluations/month, 7-day audit log. No credit card required.
