# OpenClaw + Axon Platform Convergence Plan

**Date:** 2026-02-12 (updated 2026-02-13)
**Status:** Architecture Finalized — Ready for Implementation
**Linear Epic:** TBD (create before starting work)
**Project:** Axon Platform Infrastructure

---

## Table of Contents

- [Vision: Three-Layer Convergence](#vision-three-layer-convergence)
- [Requirements](#requirements)
- [What is OpenClaw?](#what-is-openclaw)
- [Why OpenClaw for Ultrathink Solutions](#why-openclaw-for-ultrathink-solutions)
- [Infrastructure Fit: Dev Server Assessment](#infrastructure-fit-dev-server-assessment)
- [Convergence Architecture](#convergence-architecture)
- [Bidirectional Webhook Bridge](#bidirectional-webhook-bridge)
- [Shared Memory Bridge](#shared-memory-bridge)
- [Dual-Interface Design Pattern](#dual-interface-design-pattern)
- [Agent Design](#agent-design)
- [LiteLLM Integration & Cost Management](#litellm-integration-cost-management)
- [Claude Code Max Subscription Strategy](#claude-code-max-subscription-strategy)
- [MCP Tool Integration](#mcp-tool-integration)
- [External Service Integrations](#external-service-integrations)
- [Claude Code Rules & Skills Portability](#claude-code-rules-skills-portability)
- [Proactive Behavior: Cron & Heartbeat System](#proactive-behavior-cron-heartbeat-system)
- [Security Hardening](#security-hardening)
- [Implementation Phases](#implementation-phases)
- [Gaps & Open Questions](#gaps-open-questions)
- [References & Sources](#references-sources)

---

## Vision: Three-Layer Convergence

This plan deploys OpenClaw as the **channel layer** for Ultrathink's Axon platform, creating a unified system where AI agents are reachable from messaging surfaces (Slack, WhatsApp) AND the web UI — with the same orchestration backbone (Temporal), the same memory (Mem0), the same tools (MCP servers), and the same observability (Langfuse/LiteLLM).

The key architectural insight: **OpenClaw owns channels. Axon owns orchestration. Neither subsumes the other.** They communicate through a well-defined contract — REST for commands, webhooks for events, Mem0 REST API for shared memory.

```text
┌─────────────────────────────────────────────────────────────────┐
│  CHANNEL LAYER (OpenClaw Gateway)                                │
│  Slack, WhatsApp, iMessage, Voice — always-on, proactive         │
│                                                                   │
│  Owns: channel management, session routing, cron triggers,       │
│        conversational interface, delivery of workflow events      │
│  Does NOT own: orchestration, durable execution, memory          │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST + Webhooks (bidirectional)
┌──────────────────────────▼──────────────────────────────────────┐
│  ORCHESTRATION LAYER (Axon Platform)                             │
│  Temporal workflows, DAPERL, MCP tools, Langfuse                 │
│                                                                   │
│  Owns: durable workflow execution, approval gates, tool          │
│        execution via MCP, memory (Mem0), observability,          │
│        cost control, webhook callbacks to channel layer          │
│  Does NOT own: channels, messaging surfaces, voice               │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│  WEB UI LAYER (Next.js)                                          │
│  Rich plan review, campaign dashboards, document management      │
│                                                                   │
│  Owns: structured forms, AG-UI streaming chat, visual plan       │
│        review, campaign analytics dashboards                     │
│  Parallel channel to OpenClaw, not subordinate to it             │
└─────────────────────────────────────────────────────────────────┘
```

This is **composition, not extraction** — we run OpenClaw as a whole process to get free upgrades, community skills (5,700+ on ClawHub), and security patches, then integrate at the API layer.

---

## Requirements

### Business Goals

The founder of Ultrathink Solutions needs a proactive AI assistant ("Chief of Staff") that:

1. **Coordinates across domains** — marketing, engineering, sales, operations
2. **Learns priorities** over time and proactively suggests actions based on business goals
3. **Is always-on** — available via messaging (Slack, WhatsApp) 24/7, not just during active coding sessions
4. **Has access to all business tools** — Google Drive, Gmail, Calendar, HubSpot, Apollo, LinkedIn, Google Analytics, Search Console, Linear
5. **Can delegate coding tasks** to Claude Code (preserving existing plugins, skills, and rules)
6. **Manages marketing workflows** — blog posts, campaign landing pages, LinkedIn/Google Ads, email sequences, analytics queries
7. **Bridges to Axon orchestration** — can trigger DAPERL workflows, receive approval requests, and relay results back through messaging channels

### Technical Requirements

1. **Use Claude Code Max subscription** for coding work (not API keys — subscription covers heavy coding usage)
2. **Route non-coding LLM calls through LiteLLM** for centralized cost tracking, budgeting via virtual keys, and Langfuse observability
3. **Reuse existing MCP servers** deployed in k8s (Apollo, LinkedIn, Google Analytics) without duplicating infrastructure
4. **No per-agent OAuth** — MCP servers handle auth server-side via Kubernetes secrets
5. **Maintain all existing Claude Code configuration** — CLAUDE.md rules, AGENTS.md, feature-dev plugin, frontend-design plugin, pyright-lsp, Linear MCP, tessl library docs
6. **Deploy on existing dev-server** (Hetzner AX41-NVMe, NixOS, 64GB RAM) — no new infrastructure
7. **Bidirectional integration with Axon** — OpenClaw triggers Temporal workflows AND receives workflow events (approval requests, completion notifications) via webhooks
8. **Shared memory** — OpenClaw agents access the same Mem0 memory store used by Axon agents, enabling cross-system context continuity

### Desired Agent Capabilities

| Capability | Priority | Agent | Integration |
|-----------|----------|-------|-------------|
| Morning briefing (email, calendar, deals, issues) | P0 | Chief of Staff | Direct (OpenClaw tools) |
| Proactive lead monitoring (HubSpot + email) | P0 | Chief of Staff | Direct (OpenClaw tools) |
| Weekly strategy memo | P0 | Chief of Staff | Direct (OpenClaw tools) |
| Company research (Apollo enrichment, job postings) | P0 | Marketing | MCP + Axon REST API |
| Google Analytics reporting | P0 | Marketing | MCP (GA server) |
| **ABM campaign orchestration** | **P0** | **Marketing** | **Axon webhook bridge** |
| **Workflow approval via Slack/WhatsApp** | **P0** | **Chief of Staff** | **Axon webhook bridge** |
| Blog post generation | P1 | Content | Direct (OpenClaw tools) |
| LinkedIn ad campaign management | P1 | Marketing | MCP (LinkedIn server) |
| Landing page creation | P1 | Content | Direct (OpenClaw tools) |
| Email sequence generation | P1 | Content | Direct (OpenClaw tools) |
| Feature development (via Claude Code) | P0 | Coding | Claude Code subprocess |
| PR reviews (via Claude Code) | P1 | Coding | Claude Code subprocess |
| Google Ads campaign management | P2 | Marketing | MCP (future server) |
| Search Console analysis | P2 | Marketing | MCP (future server) |

---

## What is OpenClaw?

OpenClaw is an open-source AI agent framework (formerly "Clawdbot", then "Moltbot") that runs locally and connects to messaging platforms. Created by Peter Steinberger (PSPDFKit founder), it launched November 2025 and has 145,000+ GitHub stars as of February 2026 ([Creati.ai, Feb 2026](https://creati.ai/ai-news/2026-02-11/openclaw-open-source-ai-agent-viral-145k-github-stars/)).

**Key differentiators from chatbots:**
- **Always-on daemon** — runs as a gateway process, not per-session
- **Persistent memory** — remembers context across days/weeks/months via SOUL.md, USER.md, memory.md, and daily session logs
- **Multi-channel** — Slack, WhatsApp, Discord, Telegram, iMessage, email
- **Multi-agent** — isolated agents with separate workspaces, tools, and memory ([OpenClaw Multi-Agent Docs](https://docs.openclaw.ai/concepts/multi-agent))
- **Proactive** — cron jobs trigger scheduled tasks without user prompting ([OpenClaw Cron Docs](https://docs.openclaw.ai/automation/cron-jobs))
- **Bring your own model** — supports any OpenAI-compatible API, including LiteLLM proxies ([OpenClaw LiteLLM Provider](https://docs.openclaw.ai/providers/litellm))
- **Skill ecosystem** — 5,700+ skills on ClawHub registry ([ClawHub](https://github.com/openclaw/clawhub))
- **Webhook ingress** — external systems can trigger agent actions via authenticated HTTP endpoints ([OpenClaw Webhook Docs](https://docs.openclaw.ai/automation/webhook))

**Architecture:** OpenClaw runs a "Gateway" process that connects to messaging apps, routes inbound messages to agents via bindings (most-specific match wins), invokes tools, and sends responses. Each agent has its own workspace, state directory, auth profiles, and session store.

---

## Why OpenClaw for Ultrathink Solutions

### The Convergence Thesis

OpenClaw and Axon solve **different halves of the same problem**:

| Dimension | OpenClaw | Axon Platform |
|-----------|----------|---------------|
| **Strength** | Channel accessibility (Slack, WhatsApp, voice) | Workflow orchestration (Temporal, DAPERL) |
| **Interface** | Chat (messaging surfaces) | Web UI (Next.js + AG-UI) |
| **Execution model** | Conversational, ad-hoc, fire-and-forget | Durable, phased, human-in-the-loop |
| **Memory** | Per-agent session files (JSONL) | Mem0 hybrid (Qdrant + Neo4j + Redis) |
| **Tool access** | MCP adapter plugin | PydanticAI MCPServerStreamableHTTP |
| **Scheduling** | Cron jobs | Temporal schedules |
| **Approval flow** | Chat-based (no durability guarantee) | Temporal signals (survives crashes) |

**The convergence makes both systems stronger:**

- OpenClaw gains **durable orchestration** — when you say "research Nordstrom for ABM" in Slack, a Temporal workflow handles the multi-phase execution with retries and crash recovery
- Axon gains **channel reach** — approval requests and campaign results are delivered to wherever you are (Slack, WhatsApp, phone), not just the web UI
- Both systems share **unified memory** — what the ABM agent learns about a company is available to the chief-of-staff agent in Slack
- Both systems share **unified observability** — every LLM call from either system appears in the same Langfuse dashboard

### Why Composition, Not Extraction

OpenClaw's gateway cannot be cleanly extracted from its codebase — channels, sessions, and the agent runtime are deeply coupled across ~70 interdependent source directories. Running OpenClaw as a **whole process** (systemd service) and integrating via REST/webhooks provides:

1. **Free upgrades** — `npm update -g openclaw@latest` brings new features, security patches, and channel improvements
2. **Community ecosystem** — 5,700+ ClawHub skills (Google Workspace, HubSpot, coding-agent)
3. **Active security maintenance** — critical given CVE-2026-25253 and the 42,900 exposed instances found in February 2026
4. **Clean separation of concerns** — OpenClaw doesn't need to understand Temporal; Axon doesn't need to understand Baileys

### Cost Model

OpenClaw itself is free and open-source. Costs come from:
- LLM API usage (routed through LiteLLM with per-agent budget caps)
- Claude Code Max subscription (for coding tasks — already paid for)
- No additional infrastructure (runs on existing dev-server)

---

## Infrastructure Fit: Dev Server Assessment

### Server Specifications

| Component | Specification |
|-----------|---------------|
| Server | Hetzner AX41-NVMe (Finland) |
| CPU | AMD Ryzen 5 3600 (6c/12t) |
| RAM | 64GB DDR4 ECC |
| Storage | 2x 512GB NVMe (RAID1) |
| Network | 1 Gbit/s + Tailscale mesh |
| OS | NixOS (fully declarative) |
| Cost | ~EUR 50/month |

### Resource Budget

OpenClaw recommends ~8GB RAM per concurrent agent ([OpenClaw Multi-Agent Docs](https://docs.openclaw.ai/concepts/multi-agent)).

| Consumer | Estimated RAM |
|----------|--------------|
| Existing k8s workloads (all pods) | ~15-20GB |
| OpenClaw Gateway + 4 agents | ~32GB |
| **Available headroom** | ~12-17GB |
| **Total server RAM** | 64GB |

Comfortable fit. No new infrastructure needed.

### Security Posture

The dev-server is already hardened beyond what 93% of OpenClaw deployments have ([Security Boulevard, Feb 2026](https://securityboulevard.com/2026/02/42900-openclaw-exposed-control-panels-and-why-you-should-care/)):

- **SSH is Tailscale-only** — port 22 blocked on public IP
- **NixOS firewall** — only UDP 41641 (WireGuard) open publicly
- **k3s CNI trusted** — `cni0`, `flannel.1` in `trustedInterfaces`
- **SOPS secrets** — no plaintext credentials on disk
- **No public-facing services** — all access via Tailscale MagicDNS

OpenClaw bound to `loopback` on this server means it's only accessible via Tailscale SSH tunnel — completely invisible to the public internet.

### Deployment Approach: Standalone Systemd Service

**Decision:** Run OpenClaw directly on the dev-server as a systemd service, **outside k3s**.

**Reasoning:**
- OpenClaw is designed as a long-running local daemon, not a containerized microservice
- NixOS systemd integration is clean — declare it like k3s and Tailscale
- Simpler than containerizing (OpenClaw's Docker mode has quirks with volume mounts)
- Can still reach k8s services via ClusterIP (same machine)

```text
Dev Server (NixOS)
├── k3s (systemd) ← existing app workloads
│   ├── marketing-agent (backend/frontend/worker)
│   ├── Temporal, Langfuse, LiteLLM, etc.
│   ├── MCP servers (Apollo, LinkedIn, GA)
│   └── Mem0 REST API (new — exposes shared memory)
│
├── OpenClaw Gateway (systemd) ← NEW
│   ├── Agent: chief-of-staff
│   ├── Agent: marketing
│   ├── Agent: content
│   └── Agent: coding
│
└── Tailscale (systemd) ← secures everything
```

---

## Convergence Architecture

### System Interaction Diagram

```text
┌──────────────────────────────────────────────────────────────────────┐
│  YOUR DEVICES (Laptop/Phone)                                          │
│                                                                        │
│  Slack ─────┐                          ┌─── Web UI (localhost:3000)   │
│  WhatsApp ──┤  Proactive alerts,       │    Plan review, dashboards,  │
│  Email ─────┘  approvals, briefings    │    AG-UI chat, analytics     │
└──────────────────────┬─────────────────┼────────────────────────────┘
                       │                  │
     ┌─────────────────▼──────┐   ┌──────▼──────────────────┐
     │  OPENCLAW GATEWAY       │   │  NEXT.JS FRONTEND       │
     │  (systemd, port 18789)  │   │  (k8s, port 3000)       │
     │                         │   │                          │
     │  Chief of Staff agent   │   │  AG-UI streaming chat    │
     │  Marketing agent        │   │  Campaign management     │
     │  Content agent          │   │  Document ingestion      │
     │  Coding agent           │   │  Plan review UI          │
     └────────┬───────┬────────┘   └──────┬──────────────────┘
              │       │                    │
              │       │ POST /hooks/agent  │
              │       │ (webhook callback) │
              │       ▲                    │
     ┌────────▼───────┼────────────────────▼──────────────────────────┐
     │  AXON PLATFORM BACKEND (k8s)                                    │
     │                                                                  │
     │  ┌──────────────────────────────────────────────────────────┐   │
     │  │  FastAPI (port 8000)                                      │   │
     │  │  POST /v1/abm/campaigns         ← start workflow         │   │
     │  │  GET  /v1/abm/campaigns/:id     ← check progress         │   │
     │  │  GET  /v1/abm/campaigns/:id/plan ← get plan for review   │   │
     │  │  POST /v1/abm/campaigns/:id/approve ← send approval      │   │
     │  │  POST /v1/chat/completions      ← AG-UI chat endpoint    │   │
     │  │  GET  /v1/events/stream         ← SSE event bus          │   │
     │  └──────────────────────┬───────────────────────────────────┘   │
     │                         │                                        │
     │  ┌──────────────────────▼───────────────────────────────────┐   │
     │  │  Temporal Workers                                         │   │
     │  │  DAPERL Workflow: Detection → Analysis → Planning →       │   │
     │  │    Plan Review → [APPROVAL GATE] → Execution → Reporting │   │
     │  │                        │                                  │   │
     │  │                   On approval gate:                       │   │
     │  │                   1. Persist to Postgres                  │   │
     │  │                   2. Emit SSE event (web UI)              │   │
     │  │                   3. POST to OpenClaw webhook (Slack)     │   │
     │  │                   4. Wait for signal                      │   │
     │  └──────────────────────────────────────────────────────────┘   │
     │                                                                  │
     │  ┌──────────────────────────────────────────────────────────┐   │
     │  │  Shared Infrastructure                                    │   │
     │  │  LiteLLM (unified model gateway + cost tracking)         │   │
     │  │  Langfuse (observability for both Axon and OpenClaw)     │   │
     │  │  Mem0 REST API (shared memory for all agents)            │   │
     │  │  MCP Servers (Apollo, LinkedIn, GA, HubSpot, Linear)     │   │
     │  │  Postgres, Qdrant, Neo4j, Redis                          │   │
     │  └──────────────────────────────────────────────────────────┘   │
     └─────────────────────────────────────────────────────────────────┘
```

### Integration Contracts

The two systems communicate through three well-defined contracts:

| Contract | Direction | Protocol | Purpose |
|----------|-----------|----------|---------|
| **REST API** | OpenClaw → Axon | HTTP POST/GET | Trigger workflows, query status, send approvals |
| **Webhook Bridge** | Axon → OpenClaw | HTTP POST to `/hooks/agent` | Deliver approval requests, completion events, alerts |
| **Mem0 REST API** | OpenClaw → Mem0 | HTTP POST/GET | Search and add shared memories |

---

## Bidirectional Webhook Bridge

### The Problem

Without a bridge, these two systems are disconnected islands:

```text
User (Slack) → "Research Nordstrom for ABM"
    → OpenClaw → POST /v1/abm/campaigns → Temporal workflow starts
    → Workflow runs Detection → Analysis → Planning
    → Workflow reaches approval gate
    → ??? How does the user in Slack find out?
    → ??? How does their Slack reply become a Temporal signal?
```

### The Solution: Webhook Bridge via Temporal Activity + OpenClaw `/hooks/agent`

OpenClaw's webhook API ([OpenClaw Webhook Docs](https://docs.openclaw.ai/automation/webhook)) exposes `POST /hooks/agent` which runs an isolated agent turn and delivers the response to a specified messaging channel. This is the key integration point.

When a Temporal workflow reaches an approval gate, it:
1. Persists the plan to Postgres (for the web UI)
2. Emits an SSE event (for the web UI's real-time updates)
3. **Calls a Temporal activity that POSTs to OpenClaw's webhook** (for Slack/WhatsApp delivery)
4. Waits for a Temporal signal (from either the web UI or OpenClaw)

When the user responds in Slack, OpenClaw's chief-of-staff agent:
1. Recognizes the approval intent from the conversational context
2. Calls the `approve_campaign` tool (which POSTs to Axon's REST API)
3. Axon's REST API sends the Temporal signal, resuming the workflow
4. The workflow completion triggers another webhook back to OpenClaw for result delivery

### Architecture

```text
                    APPROVAL REQUEST FLOW
                    ─────────────────────

Temporal Workflow                    OpenClaw Gateway
┌─────────────────┐                 ┌─────────────────┐
│ Planning phase   │                │                  │
│ completes        │                │                  │
│                  │                │                  │
│ ┌──────────────┐ │  HTTP POST     │ ┌──────────────┐ │    Slack
│ │ notify_       │─┼──────────────►│ │ /hooks/agent │─┼───► DM
│ │ channel_      │ │ /hooks/agent  │ │              │ │
│ │ activity      │ │               │ │ agent:       │ │
│ └──────────────┘ │               │ │ chief-of-    │ │
│                  │               │ │ staff        │ │
│ ┌──────────────┐ │               │ └──────────────┘ │
│ │ wait_        │ │               │                  │
│ │ condition()  │ │               │                  │
│ │ (paused)     │ │               └─────────────────┘
│ └──────────────┘ │
└─────────────────┘

                    APPROVAL RESPONSE FLOW
                    ──────────────────────

User (Slack)                OpenClaw Agent              Axon REST API
┌──────────┐               ┌──────────────┐            ┌──────────────┐
│ "Approve  │               │ Chief of     │            │              │
│  the plan │──────────────►│ Staff agent  │            │              │
│  for      │               │              │  POST      │ approve_     │
│  Nordstrom│               │ Calls        │──────────►│ campaign()   │
│  "        │               │ approve_     │            │              │
│           │               │ campaign     │            │ Sends        │
│           │               │ tool         │            │ Temporal     │
│           │               │              │            │ signal       │
└──────────┘               └──────────────┘            └──────┬───────┘
                                                              │
                                                              ▼
                                                       Workflow resumes
                                                       Execution phase
                                                              │
                                                              ▼
                                                       notify_channel_
                                                       activity (again)
                                                              │
                                                              ▼
                                                       OpenClaw webhook
                                                              │
                                                              ▼
                                                       Slack: "Campaign
                                                       complete. 3 accounts
                                                       enrolled."
```

### Implementation: Temporal Notification Activity

This activity sends workflow events to OpenClaw's webhook endpoint for delivery to messaging channels. It follows Temporal best practices for external notifications: idempotent, retriable, with circuit breaker protection ([Temporal Workflow Orchestration](https://james-carr.org/posts/2026-01-29-temporal-workflow-orchestration/), [Webhook Best Practices](https://notigrid.com/blog/webhooks-for-custom-integrations)).

```python
# apps/marketing-agent/backend/app/activities/channel_notification.py

import httpx
from temporalio import activity
from pydantic import BaseModel

class ChannelNotificationInput(BaseModel):
    """Input for notifying an external messaging channel via OpenClaw webhook."""
    message: str
    agent_id: str = "chief-of-staff"
    channel: str = "slack"
    to: str  # Slack channel ID, phone number, etc.
    workflow_id: str  # For correlation
    event_type: str  # "approval_required", "execution_complete", "error"
    model: str = "sonnet"
    thinking: str = "low"

@activity.defn
async def notify_channel_activity(input: ChannelNotificationInput) -> dict:
    """
    Send a notification to a messaging channel via OpenClaw's webhook API.

    This activity is idempotent — OpenClaw's /hooks/agent returns 202 and
    processes asynchronously, so retries are safe.

    References:
    - OpenClaw Webhook Docs: https://docs.openclaw.ai/automation/webhook
    - Temporal Activity Best Practices: https://docs.temporal.io/activities
    """
    openclaw_url = activity.info().heartbeat_details or settings.openclaw_webhook_url
    hook_token = settings.openclaw_hook_token

    payload = {
        "message": input.message,
        "agentId": input.agent_id,
        "deliver": True,
        "channel": input.channel,
        "to": input.to,
        "model": input.model,
        "thinking": input.thinking,
        "wakeMode": "now",
        # Include workflow context so the agent can reference it
        "sessionKey": f"hook:workflow:{input.workflow_id}",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{openclaw_url}/hooks/agent",
            json=payload,
            headers={
                "Authorization": f"Bearer {hook_token}",
                "Content-Type": "application/json",
                "X-Idempotency-Key": f"{input.workflow_id}:{input.event_type}",
            },
        )
        response.raise_for_status()

    return {"status": "accepted", "workflow_id": input.workflow_id}
```

### Integration into DAPERL Workflow

Add the notification call at the approval gate in the existing `_handle_plan_review` method:

```python
# In daperl_workflow.py, after setting _awaiting_plan_approval = True

# Notify external channels (Slack/WhatsApp via OpenClaw)
if input_data.notify_channel:
    plan_summary = self._format_plan_for_chat(self._plan)
    await workflow.execute_activity(
        notify_channel_activity,
        args=[ChannelNotificationInput(
            message=(
                f"Campaign '{input_data.campaign_name}' needs your approval.\n\n"
                f"**{len(self._plan.actions)} actions** planned for "
                f"{len(input_data.targets)} target(s).\n\n"
                f"{plan_summary}\n\n"
                f"Reply 'approve', 'reject', or 'replan with [feedback]'.\n"
                f"Or review in detail at {settings.frontend_url}/campaigns/{workflow_id}"
            ),
            workflow_id=workflow.info().workflow_id,
            event_type="approval_required",
            channel=input_data.notify_channel,
            to=input_data.notify_to,
        )],
        start_to_close_timeout=datetime.timedelta(seconds=30),
        retry_policy=RetryPolicy(
            initial_interval=datetime.timedelta(seconds=2),
            maximum_interval=datetime.timedelta(seconds=30),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        ),
    )
```

### OpenClaw Skill: Axon API Bridge

The OpenClaw agent needs tools to interact with the Axon REST API. This is implemented as an OpenClaw workspace skill:

```markdown
# ~/.openclaw/workspace-chief-of-staff/skills/axon-api/SKILL.md
---
name: axon-api-bridge
description: Bridge to Axon Platform REST API for ABM campaigns and workflow management
metadata:
  openclaw:
    emoji: 🔗
---

# Axon Platform API Bridge

You have access to the Axon Platform backend for ABM campaign orchestration.

## Available Operations

### Start a Campaign
```bash
curl -X POST "${AXON_API_URL}/v1/abm/campaigns" \
  -H "Content-Type: application/json" \
  -d '{
    "targets": ["nordstrom.com", "macys.com"],
    "campaign_name": "Retail Q1 2026",
    "user_id": "nick",
    "require_approval": true,
    "notify_channel": "slack",
    "notify_to": "SLACK_USER_ID"
  }'
```

### Check Campaign Progress
```bash
curl "${AXON_API_URL}/v1/abm/campaigns/${WORKFLOW_ID}?user_id=nick"
```

### Get Plan for Review
```bash
curl "${AXON_API_URL}/v1/abm/campaigns/${WORKFLOW_ID}/plan?user_id=nick"
```

### Approve/Reject Plan
```bash
curl -X POST "${AXON_API_URL}/v1/abm/campaigns/${WORKFLOW_ID}/approve" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "approver_id": "nick",
    "feedback": "Looks good, proceed"
  }'
```

## Approval Handling

When you receive a message about a campaign needing approval:
1. Parse the workflow_id from the message context
2. Fetch the plan with the "Get Plan for Review" endpoint
3. Present a clear summary to the user
4. When the user responds with their decision, call the approve endpoint
5. Confirm the action was taken

Valid decisions: "approve", "reject", "replan"
If "replan", include the user's feedback in the feedback field.

### Webhook Configuration in OpenClaw

```json5
// ~/.openclaw/openclaw.json — hooks section
{
  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOK_TOKEN}",
    path: "/hooks",
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: true,
    allowedSessionKeyPrefixes: ["hook:workflow:"],
    allowedAgentIds: ["chief-of-staff"],
  },
}
```

### DAPERLInput Extension

Add notification fields to the workflow input so callers can specify where to deliver events:

```python
class DAPERLInput(BaseModel):
    domain: str
    targets: list[str]
    user_id: str
    require_approval: bool = True
    config: dict[str, Any] = {}

    # Channel notification (new fields for convergence)
    notify_channel: str | None = None  # "slack", "whatsapp", "telegram"
    notify_to: str | None = None  # Channel-specific recipient ID
    campaign_name: str | None = None  # Human-readable name for notifications
```

---

## Shared Memory Bridge

### The Problem

Without shared memory, the two systems develop **context amnesia**:

- OpenClaw's chief-of-staff learns you care about retail vertical → stores in `memory.md`
- Axon's ABM agent scores retail accounts → stores in Mem0 (Qdrant + Neo4j)
- Neither system knows what the other learned
- The chief-of-staff can't reference last week's ABM research in a morning briefing
- The ABM agent can't leverage strategic priorities discussed in Slack

### The Solution: Mem0 REST API as Shared Memory Layer

Mem0 provides a [REST API](https://docs.mem0.ai/open-source/features/rest-api) with CRUD endpoints for memories filtered by `user_id` and `agent_id`. By deploying the Mem0 REST server in k8s (pointing at the existing Qdrant + Neo4j infrastructure) and writing an OpenClaw skill that queries it, both systems share the same memory.

**Key design decision:** Mem0 becomes the **system of record** for cross-agent memory. OpenClaw's native `memory.md` still handles agent-local session notes, but anything that should persist across systems goes through Mem0.

### Architecture

```text
OpenClaw Agent                     Mem0 REST API                    Axon Agent
┌──────────────┐                  ┌──────────────┐                ┌──────────────┐
│ "What do we  │    GET /memories │              │                │ ABM workflow  │
│  know about  │    /search?      │   Qdrant     │  POST /memories│ researches    │
│  Nordstrom?" │────────────────►│   (vectors)  │◄───────────────│ Nordstrom     │
│              │                  │              │                │              │
│ Gets:        │◄────────────────│   Neo4j      │                │ Stores:       │
│ - ICP score  │  Memory results  │   (graph)    │                │ - Enrichment  │
│ - AI signals │                  │              │                │ - Score: 87   │
│ - Contacts   │                  │   Redis      │                │ - AI signals  │
│              │                  │   (cache)    │                │              │
│ POST /memories                  │              │                │              │
│ "Nick prefers │────────────────►│              │────────────────►│ Gets:         │
│  retail"      │  Add memory     │              │  Search query   │ "Focus on     │
│              │                  │              │                │  retail"       │
└──────────────┘                  └──────────────┘                └──────────────┘
```

### Mem0 REST API Deployment

Deploy the Mem0 REST server as a k8s service pointing at the existing infrastructure:

```yaml
# charts/custom/mem0-api/values.yaml
replicaCount: 1
image:
  repository: mem0ai/rest-server
  tag: "latest"
env:
  MEM0_VECTOR_STORE_PROVIDER: qdrant
  MEM0_VECTOR_STORE_URL: http://qdrant.qdrant.svc.cluster.local:6333
  MEM0_GRAPH_STORE_PROVIDER: neo4j
  MEM0_GRAPH_STORE_URL: bolt://neo4j.neo4j.svc.cluster.local:7687
  MEM0_LLM_PROVIDER: openai
  MEM0_LLM_BASE_URL: http://dev-stack-litellm.litellm.svc.cluster.local:4000
  MEM0_LLM_API_KEY: ${LITELLM_MEM0_KEY}
service:
  port: 8000
  clusterIP: mem0-api.mem0.svc.cluster.local
```

**Important:** The Mem0 REST API has no built-in auth ([Mem0 REST API Docs](https://docs.mem0.ai/open-source/features/rest-api)). Since it's only accessible within the k8s cluster and via the loopback network (OpenClaw runs on the same machine), this is acceptable for internal use. Add a network policy restricting access to the `marketing-agent` and `default` namespaces.

### OpenClaw Skill: Shared Memory

```markdown
# ~/.openclaw/workspace-chief-of-staff/skills/shared-memory/SKILL.md
---
name: shared-memory
description: Access the shared Axon memory system (Mem0) for cross-agent context
metadata:
  openclaw:
    emoji: 🧠
---

# Shared Memory (Mem0)

You have access to Ultrathink's shared memory system. Use it to recall
context from previous interactions, ABM research, campaign results,
and strategic decisions — regardless of which agent or system created
the memory.

## Search memories

```bash
curl -s "${MEM0_API_URL}/memories/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "your search query", "user_id": "nick", "limit": 10}'
```

## Add a memory

When you learn something important about the business, a client, a
strategy, or a preference, store it for future reference:

```bash
curl -s -X POST "${MEM0_API_URL}/memories" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "the context"},
      {"role": "assistant", "content": "the insight or fact to remember"}
    ],
    "user_id": "nick",
    "agent_id": "chief-of-staff"
  }'
```

## When to use shared memory

- **Always search** before answering questions about companies, campaigns,
  or strategic context
- **Always store** significant business decisions, user preferences,
  campaign outcomes, and ICP learnings
- Memories from ABM research (scored companies, contact mappings) are
  stored by the marketing-agent backend — search for them here
- Your local memory.md is for session-specific notes; Mem0 is for
  durable cross-system knowledge
```

### Memory Scoping Strategy

| Memory Type | Store | Scope | Example |
|-------------|-------|-------|---------|
| Business context, preferences | Mem0 | `user_id: "nick"` | "Prefers retail vertical for ABM" |
| ABM research results | Mem0 | `user_id: "nick", agent_id: "abm-agent"` | "Nordstrom scored 87/100" |
| Campaign outcomes | Mem0 | `user_id: "nick", agent_id: "abm-agent"` | "Q4 campaign: 12% reply rate" |
| Agent session notes | OpenClaw `memory.md` | Per-agent workspace | "Last conversation about hiring" |
| Tool usage patterns | OpenClaw `memory.md` | Per-agent workspace | "User prefers Sonnet for research" |

---

## Dual-Interface Design Pattern

### Principle: Two First-Class Frontends, One Backend

Both the web UI (Next.js) and messaging channels (OpenClaw) are **equal-status interfaces** to the same Axon backend. Neither is subordinate to the other.

This follows the emerging pattern described in the AG-UI specification: "any client that understands the protocol can talk to any agent that follows it — web app, CLI, Slack bot, mobile app" ([AG-UI Protocol Docs](https://docs.ag-ui.com/), [CopilotKit AG-UI Blog](https://webflow.copilotkit.ai/blog/introducing-ag-ui-the-protocol-where-agents-meet-users)).

| Scenario | Best Interface | Why |
|----------|---------------|-----|
| Review a 15-action ABM plan with per-account scoring | **Web UI** | Rich tables, expandable sections, inline editing |
| Quick approval of a low-risk campaign | **Slack** | "Approve" is one word; no context switch |
| Morning briefing while commuting | **WhatsApp** | Phone-native, voice possible |
| Deep campaign analytics review | **Web UI** | Charts, filters, date ranges |
| "What companies did we research last week?" | **Either** | Both can query the same Postgres + Mem0 data |
| Proactive lead alert at 2am | **Slack/WhatsApp** | You're not at your desk |
| Feature development delegation | **Slack** | "Build the landing page for Q1 campaign" → Claude Code |

### Event Routing Matrix

When a workflow state change occurs, the system decides where to deliver notifications:

| Event | Web UI (SSE) | OpenClaw Webhook | Reasoning |
|-------|-------------|-----------------|-----------|
| Workflow started | Yes | No | User just triggered it; they know |
| Phase transition (Detection → Analysis) | Yes | No | Progress visible in UI; low urgency |
| **Plan ready for approval** | **Yes** | **Yes** | Critical gate — reach user wherever they are |
| Plan approved/rejected | Yes | No | User initiated; they know |
| **Execution complete** | **Yes** | **Yes** | User wants to know results landed |
| Action failed (non-critical) | Yes | No | Visible in UI; skip-on-failure handles it |
| **Action failed (critical)** | **Yes** | **Yes** | Needs human intervention |
| Cron-triggered briefing | No | **Yes** | Only meaningful in messaging |

### Implementation: Event Router

Add a lightweight router that fans out workflow events to both surfaces:

```python
# apps/marketing-agent/backend/app/events/router.py

WEBHOOK_EVENTS = {
    AgentEventType.AWAITING_APPROVAL,
    AgentEventType.EXECUTION_COMPLETE,
    AgentEventType.CRITICAL_FAILURE,
}

async def route_workflow_event(
    user_id: str,
    agent_id: str,
    event_type: AgentEventType,
    payload: dict,
    notification_config: ChannelNotificationConfig | None = None,
) -> None:
    """
    Route a workflow event to all relevant surfaces.

    Always emits to SSE (web UI). Conditionally sends to OpenClaw
    webhook for events that warrant messaging channel delivery.
    """
    # 1. Always emit to SSE (existing pattern)
    await emit_event(user_id, agent_id, "daperl", event_type, payload)

    # 2. Conditionally notify messaging channels via OpenClaw
    if (
        notification_config
        and notification_config.enabled
        and event_type in WEBHOOK_EVENTS
    ):
        message = format_event_for_chat(event_type, payload)
        await notify_channel_activity(ChannelNotificationInput(
            message=message,
            workflow_id=payload.get("workflow_id", ""),
            event_type=event_type.value,
            channel=notification_config.channel,
            to=notification_config.to,
        ))
```

---

## Agent Design

### Agent Roster

| Agent ID | Role | Model | Sandbox | MCP Access | Key Tools |
|----------|------|-------|---------|------------|-----------|
| `chief-of-staff` | Coordinator, proactive assistant, approval relay | Sonnet 4.5 (LiteLLM) | `ro` workspace | All via delegation | read, sessions, fetch, axon-api, shared-memory |
| `marketing` | Research, analytics, ads | Sonnet 4.5 (LiteLLM) | `rw` workspace | Apollo, LinkedIn, GA, HubSpot | read, write, fetch, mcp-adapter, axon-api, shared-memory |
| `content` | Blog posts, landing pages, copy | Sonnet 4.5 (LiteLLM) | `rw` workspace | None (delegates data needs) | read, write, fetch, shared-memory |
| `coding` | Delegates to Claude Code | Sonnet 4.5 (LiteLLM) | `rw` workspace | None (Claude Code has its own) | exec, read, process |

### Agent Identity Files

Each agent gets its own workspace with identity and instruction files:

```text
~/.openclaw/
├── openclaw.json                          # Main config
├── cron/jobs.json                         # Scheduled tasks
├── workspace-chief-of-staff/
│   ├── SOUL.md                            # Identity: proactive business partner
│   ├── AGENTS.md                          # Operating instructions
│   ├── USER.md                            # Founder context, priorities
│   ├── HEARTBEAT.md                       # What to monitor proactively
│   ├── memory.md                          # Agent-local session notes
│   └── skills/
│       ├── axon-api/SKILL.md              # REST API bridge to Axon platform
│       └── shared-memory/SKILL.md         # Mem0 memory bridge
├── workspace-marketing/
│   ├── SOUL.md                            # Identity: marketing specialist
│   ├── AGENTS.md                          # Tool usage patterns, ICP criteria
│   └── skills/
│       ├── axon-api/SKILL.md              # REST API bridge (campaign operations)
│       └── shared-memory/SKILL.md         # Mem0 memory bridge
├── workspace-content/
│   ├── SOUL.md                            # Identity: content creator, brand voice
│   ├── AGENTS.md                          # Brand guidelines, content standards
│   └── skills/
│       └── shared-memory/SKILL.md         # Mem0 memory bridge
└── workspace-coding/
    ├── SOUL.md                            # Identity: delegation coordinator
    └── AGENTS.md                          # How to invoke Claude Code
```

### OpenClaw Configuration

```json5
// ~/.openclaw/openclaw.json
{
  gateway: {
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "${OPENCLAW_GATEWAY_TOKEN}" },
  },

  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOK_TOKEN}",
    path: "/hooks",
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: true,
    allowedSessionKeyPrefixes: ["hook:workflow:"],
    allowedAgentIds: ["chief-of-staff"],
  },

  models: {
    providers: {
      litellm: {
        baseUrl: "http://dev-stack-litellm.litellm.svc.cluster.local:4000",
        apiKey: "${LITELLM_OPENCLAW_KEY}",
        api: "openai-completions",
        models: [
          { id: "claude-opus-4-6", name: "Claude Opus 4.6", reasoning: true,
            contextWindow: 200000, maxTokens: 64000 },
          { id: "claude-sonnet-4-5-20250929", name: "Claude Sonnet 4.5",
            contextWindow: 200000, maxTokens: 8192 },
          { id: "gpt-4o", name: "GPT-4o",
            contextWindow: 128000, maxTokens: 8192 },
          { id: "gpt-4o-mini", name: "GPT-4o Mini",
            contextWindow: 128000, maxTokens: 4096 },
        ],
      },
    },
  },

  plugins: {
    entries: {
      "mcp-adapter": {
        enabled: true,
        config: {
          toolPrefix: true,
          servers: [
            // Existing k8s MCP servers
            { name: "apollo", transport: "http",
              url: "http://apollo-mcp-mcp-server.mcp-servers.svc.cluster.local:8080/mcp" },
            { name: "linkedin", transport: "http",
              url: "http://linkedin-mcp-mcp-server.mcp-servers.svc.cluster.local:8080/mcp" },
            { name: "google_analytics", transport: "http",
              url: "http://google-analytics-mcp-server.mcp-servers.svc.cluster.local:8080/mcp" },
            // External MCP servers
            { name: "linear", transport: "http",
              url: "https://mcp.linear.app/mcp",
              headers: { "Authorization": "Bearer ${LINEAR_API_KEY}" } },
            { name: "hubspot", transport: "http",
              url: "https://mcp.hubspot.com/sse",
              headers: { "Authorization": "Bearer ${HUBSPOT_ACCESS_TOKEN}" } },
          ],
        },
      },
    },
  },

  agents: {
    list: [
      {
        id: "chief-of-staff",
        default: true,
        workspace: "~/.openclaw/workspace-chief-of-staff",
        model: { primary: "litellm/claude-sonnet-4-5-20250929" },
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
        tools: {
          allow: ["read", "exec", "sessions_list", "sessions_history", "fetch", "mcp-adapter"],
          deny: ["write", "browser"],
        },
      },
      {
        id: "marketing",
        workspace: "~/.openclaw/workspace-marketing",
        model: { primary: "litellm/claude-sonnet-4-5-20250929" },
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "rw" },
        tools: {
          allow: ["read", "write", "exec", "mcp-adapter", "fetch"],
          deny: ["process"],
        },
      },
      {
        id: "content",
        workspace: "~/.openclaw/workspace-content",
        model: { primary: "litellm/claude-sonnet-4-5-20250929" },
        sandbox: { mode: "all", scope: "agent", workspaceAccess: "rw" },
        tools: {
          allow: ["read", "write", "exec", "fetch"],
          deny: ["process", "mcp-adapter"],
        },
      },
      {
        id: "coding",
        workspace: "~/.openclaw/workspace-coding",
        model: { primary: "litellm/claude-sonnet-4-5-20250929" },
        tools: {
          allow: ["exec", "read", "process"],
          deny: ["mcp-adapter"],
        },
      },
    ],
  },

  channels: {
    slack: {
      dmPolicy: "allowlist",
      groups: { "*": { requireMention: true } },
    },
  },

  discovery: { mdns: { mode: "off" } },
}
```

---

## LiteLLM Integration & Cost Management

### Why LiteLLM

The existing LiteLLM proxy at `http://dev-stack-litellm.litellm.svc.cluster.local:4000` is already the central gateway for all model calls in the marketing-agent backend. Routing OpenClaw through the same proxy provides:

1. **Unified cost tracking** — one dashboard for both marketing-agent app and OpenClaw agents
2. **Model fallback/routing** — if Claude is down, LiteLLM routes to GPT-4o
3. **Langfuse observability** — every LLM call appears in traces (already wired)
4. **Per-agent budget caps** — virtual keys with monthly spend limits

### Virtual Key Setup

Generate spend-limited keys per agent via LiteLLM API:

```bash
LITELLM_URL="http://dev-stack-litellm.litellm.svc.cluster.local:4000"
MASTER_KEY="sk-litellm-master-key"

# Chief of Staff — medium budget (coordination + briefing generation)
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -d '{"key_alias": "openclaw-chief-of-staff", "max_budget": 75.00, "budget_duration": "monthly"}'

# Marketing — medium budget (research, analytics queries)
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -d '{"key_alias": "openclaw-marketing", "max_budget": 100.00, "budget_duration": "monthly"}'

# Content — higher budget (heavy text generation: blogs, ads, emails)
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -d '{"key_alias": "openclaw-content", "max_budget": 200.00, "budget_duration": "monthly"}'

# Coding — low budget (just delegation prompts; Claude Code uses Max sub)
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -d '{"key_alias": "openclaw-coding", "max_budget": 25.00, "budget_duration": "monthly"}'

# Mem0 REST API — separate key for memory operations
curl -X POST "$LITELLM_URL/key/generate" \
  -H "Authorization: Bearer $MASTER_KEY" \
  -d '{"key_alias": "mem0-api", "max_budget": 50.00, "budget_duration": "monthly"}'
```

### Cost Attribution

To distinguish OpenClaw calls from Axon calls in Langfuse, configure LiteLLM metadata tagging:

| Virtual Key Alias | System | Langfuse Tag |
|-------------------|--------|-------------|
| `openclaw-chief-of-staff` | OpenClaw | `source:openclaw, agent:chief-of-staff` |
| `openclaw-marketing` | OpenClaw | `source:openclaw, agent:marketing` |
| `openclaw-content` | OpenClaw | `source:openclaw, agent:content` |
| `openclaw-coding` | OpenClaw | `source:openclaw, agent:coding` |
| `mem0-api` | Shared | `source:mem0, agent:memory` |
| `marketing-agent-*` | Axon | `source:axon, agent:*` |

**References:**
- [LiteLLM Virtual Keys](https://docs.litellm.ai/docs/proxy/virtual_keys)
- [LiteLLM Budgets & Rate Limits](https://docs.litellm.ai/docs/proxy/users)
- [OpenClaw LiteLLM Provider](https://docs.openclaw.ai/providers/litellm)

---

## Claude Code Max Subscription Strategy

### The Problem

Claude Code Max is a subscription (not API keys). Anthropic [tightened restrictions in January 2026](https://www.answeroverflow.com/m/1467147858607341712) on third-party tools using subscription auth tokens. The OpenClaw FAQ states: "you must verify with Anthropic that this usage is allowed" ([OpenClaw FAQ](https://docs.openclaw.ai/help/faq)).

### The Solution: Separation of Concerns

| LLM Consumer | Auth Method | Cost |
|-------------|-------------|------|
| **Claude Code** (subprocess via coding-agent skill) | Max subscription | Included in Max |
| **OpenClaw agents** (chief-of-staff, marketing, content) | LiteLLM with Anthropic API key | Pay per token |

**Reasoning:**
- Claude Code IS Anthropic's official tool — using Max subscription with it is explicitly supported
- Coding work is the most expensive (feature-dev parallel sub-agents, deep analysis) — Max covers this unlimited
- Marketing/content/strategy calls are shorter and cheaper — Sonnet 4.5 at ~$3/M input tokens via API is cost-effective
- The coding agent in OpenClaw itself is cheap (just delegation prompts); the heavy work happens in the Claude Code subprocess

### Claude Code as Subprocess

The official [`steipete/coding-agent`](https://github.com/openclaw/skills/blob/main/skills/steipete/coding-agent/SKILL.md) skill (by OpenClaw's creator) runs Claude Code as a background process:

```bash
# Non-interactive coding task
bash workdir:~/src/axon-internal-apps background:true command:"claude -p 'Fix the type error in chat_agent.py'"

# Interactive session via tmux
bash command:"tmux new-session -d -s coding 'cd ~/src/axon-internal-apps && claude'"

# Check progress
process action:log sessionId:SESSION_ID
```

**What Claude Code retains when spawned as subprocess:**
- CLAUDE.md + AGENTS.md rules (Graphite workflow, Python standards, etc.)
- feature-dev plugin (7-phase workflow with parallel sub-agents)
- frontend-design plugin (distinctive UI generation)
- pyright-lsp plugin (Python type checking)
- Linear MCP server
- tessl library docs (Pydantic, FastAPI, Temporal, etc.)
- Project auto-memory (MEMORY.md)
- GPG-signed commits via Graphite

**References:**
- [steipete/coding-agent Skill](https://github.com/openclaw/skills/blob/main/skills/steipete/coding-agent/SKILL.md)
- [openclaw-claude-code-skill MCP Bridge](https://github.com/Enderfga/openclaw-claude-code-skill)
- [OpenClaw vs Claude Code Comparison](https://www.getaiperks.com/en/blogs/10-openclaw-vs-claude-code)

---

## MCP Tool Integration

### Architecture

OpenClaw does **not** have native MCP support — [GitHub issue #4834 was closed as "not planned"](https://github.com/openclaw/openclaw/issues/4834) on Feb 1, 2026. Integration is via the community [`openclaw-mcp-adapter`](https://github.com/androidStern-personal/openclaw-mcp-adapter) plugin.

**How it works:**
1. Plugin connects to configured MCP servers at startup
2. Discovers tools via `listTools()` on each server
3. Registers discovered tools as native OpenClaw tools with prefix namespacing
4. Proxies agent tool calls to the appropriate MCP server
5. Auto-reconnects on connection failure

```text
OpenClaw Agent → MCP Adapter Plugin → HTTP → Apollo MCP Pod (has APOLLO_API_KEY)
                                            → LinkedIn MCP Pod (has LINKEDIN_TOKENS)
                                            → GA MCP Pod (has GOOGLE_OAUTH_CREDS)
                                            → Linear MCP (has LINEAR_API_KEY)
                                            → HubSpot MCP (has HUBSPOT_TOKEN)
```

### No Per-Agent OAuth Required

MCP servers handle authentication **server-side**. Each MCP server pod has API keys injected via Kubernetes secrets (from SOPS). The adapter just makes HTTP calls. Agents don't need individual OAuth tokens.

Agent access to MCP tools is controlled via OpenClaw's `tools.allow`/`tools.deny` sandbox lists — not at the MCP protocol level.

### Existing MCP Servers (Already Deployed)

| Server | k8s Endpoint | Tools | Auth | Status |
|--------|-------------|-------|------|--------|
| Apollo | `apollo-mcp-mcp-server.mcp-servers.svc.cluster.local:8080/mcp` | `organization_enrichment`, `organization_job_postings`, `employees_of_company` | API key (SOPS) | Active |
| LinkedIn | `linkedin-mcp-mcp-server.mcp-servers.svc.cluster.local:8080/mcp` | Ad campaigns, creatives, targeting, analytics, social posts | OAuth tokens (SOPS) | Deployed, disabled (empty URL) |
| Google Analytics | `google-analytics-mcp-server.mcp-servers.svc.cluster.local:8080/mcp` | Account summaries, property details, real-time reports, custom dimensions | OAuth2 (SOPS) | Deployed, disabled (empty URL) |

### External MCP Servers (New)

| Server | Endpoint | Tools | Auth |
|--------|----------|-------|------|
| Linear | `https://mcp.linear.app/mcp` | Issues, projects, documents, comments, cycles | OAuth (existing Claude Code config) |
| HubSpot | `https://mcp.hubspot.com/sse` | Contacts, companies, deals, CMS pages | API key / OAuth |

**References:**
- [OpenClaw MCP Adapter Plugin](https://github.com/androidStern-personal/openclaw-mcp-adapter)
- [OpenClaw Native MCP Issue #4834 (Closed)](https://github.com/openclaw/openclaw/issues/4834)
- [HubSpot MCP Server (Official)](https://developers.hubspot.com/mcp)

---

## External Service Integrations

### Integration Map

| Service | Integration Method | Skill/Plugin | Auth Type | Status |
|---------|-------------------|-------------|-----------|--------|
| **Gmail** | `gog` skill (Google Workspace CLI) | `clawhub install gog` | OAuth 2.0 (local tokens) | New |
| **Google Calendar** | `gog` skill | Same as above | OAuth 2.0 | New |
| **Google Drive** | `gog` skill | Same as above | OAuth 2.0 | New |
| **Google Docs/Sheets** | `gog` skill | Same as above | OAuth 2.0 | New |
| **HubSpot CRM** | `kwall1/hubspot` skill + HubSpot MCP | `clawhub install hubspot` + MCP adapter | API key | New |
| **Apollo** | MCP adapter (existing k8s server) | Already deployed | API key (server-side) | Existing |
| **LinkedIn Ads** | MCP adapter (existing k8s server) | Already deployed | OAuth (server-side) | Existing (enable URL) |
| **Google Analytics** | MCP adapter (existing k8s server) | Already deployed | OAuth (server-side) | Existing (enable URL) |
| **Linear** | MCP adapter (external) | `mcp.linear.app/mcp` | OAuth | Existing in Claude Code |
| **Slack** | Built-in OpenClaw channel | OpenClaw onboarding | Bot token | New |
| **Claude Code** | `steipete/coding-agent` skill | `clawhub install coding-agent` | Max subscription | New |
| **Axon Platform** | Custom REST API bridge skill | Workspace skill | Internal (loopback) | New |
| **Mem0 Memory** | Custom REST API skill | Workspace skill | Internal (loopback) | New |

### Google Workspace (`gog` Skill)

The `gog` skill is the Google Workspace CLI that connects to 13 Google services with OAuth 2.0. Data stays local — never passes through third-party cloud services ([Medium: Google Brain for OpenClaw](https://drlee.io/give-openclaw-moltbot-clawdbot-a-google-brain-how-to-connect-13-free-google-services-to-openclaw-52cdf13954e2)).

Capabilities: email summarization, draft replies, smart search, batch inbox operations, calendar management, event creation, daily briefings, Google Drive file access, Docs/Sheets manipulation.

### HubSpot CRM

Two integration paths available:
1. **HubSpot Skill** ([ClawHub](https://github.com/openclaw/skills/blob/main/skills/kwall1/hubspot/SKILL.md)) — REST API wrapper for contacts, companies, deals, CMS
2. **HubSpot MCP Server** ([Official](https://developers.hubspot.com/mcp)) — standardized MCP protocol access

Both can run simultaneously — the skill for CMS operations, the MCP server for CRM queries.

---

## Claude Code Rules & Skills Portability

### Current Claude Code Setup

| Component | Type | Status |
|-----------|------|--------|
| `~/.claude/CLAUDE.md` | Global rules (implementation principles, Graphite workflow) | Active |
| `AGENTS.md` | Project rules (dev tools, Python standards, testing, CI/CD) | Active |
| `frontend-design` plugin | Prompt-based UI design skill | Enabled |
| `feature-dev` plugin | 7-phase dev workflow (3 sub-agent types) | Enabled |
| `hookify` plugin | Runtime safety hooks (Python scripts) | Disabled |
| `pyright-lsp` plugin | Python type checking LSP | Enabled |
| Linear MCP | Streamable HTTP MCP server | Active |
| `.tessl/tiles/*` | Vendored library docs (Pydantic, FastAPI, Temporal, etc.) | Active |
| Project memory (`MEMORY.md`) | Working notes on dev patterns, gotchas | Active |

### Portability Assessment

**Nothing needs to move.** The Claude Code subprocess approach means all rules, plugins, and skills stay where they are:

| Component | Ports to OpenClaw? | Reasoning |
|-----------|-------------------|-----------|
| CLAUDE.md rules | **No — stays in Claude Code** | Claude Code subprocess reads them automatically |
| AGENTS.md | **No — stays in Claude Code** | Same — read by subprocess |
| feature-dev plugin | **No — stays in Claude Code** | Invoked via `claude /feature-dev` in subprocess |
| frontend-design plugin | **No — stays in Claude Code** | Invoked via `claude /frontend-design` in subprocess |
| pyright-lsp | **No — stays in Claude Code** | LSP runs within Claude Code process |
| Linear MCP | **Shared** — both Claude Code and OpenClaw access it | MCP adapter adds it for OpenClaw; Claude Code already has it |
| tessl tiles | **No — stays in Claude Code** | Only relevant for coding tasks |
| Project memory | **Separate** — each system has its own + shared Mem0 | OpenClaw uses memory.md (local); both share Mem0 (cross-system) |

### What OpenClaw Gets Instead

OpenClaw agents get their own identity/instruction files purpose-built for their roles:

- **Chief of Staff**: SOUL.md (proactive coordinator), USER.md (business context), HEARTBEAT.md (monitoring schedule), axon-api skill, shared-memory skill
- **Marketing**: SOUL.md (research specialist), AGENTS.md (ICP criteria, tool patterns), axon-api skill, shared-memory skill
- **Content**: SOUL.md (brand voice), AGENTS.md (content standards, guidelines access), shared-memory skill
- **Coding**: AGENTS.md (delegation instructions for Claude Code subprocess)

**References:**
- [OpenClaw Identity Architecture (MMNTM)](https://www.mmntm.net/articles/openclaw-identity-architecture)
- [SOUL.md Framework](https://github.com/aaronjmars/soul.md)
- [OpenClaw Skills Documentation](https://docs.openclaw.ai/tools/skills)

---

## Proactive Behavior: Cron & Heartbeat System

### How Proactive Behavior Works

OpenClaw becomes proactive through three mechanisms:

1. **Cron-triggered analysis** — scheduled jobs check sources and surface insights without prompting ([OpenClaw Cron Docs](https://docs.openclaw.ai/automation/cron-jobs))
2. **Main-session memory** — using `sessionTarget: "main"` accumulates context over days/weeks/months so the agent remembers business state
3. **HEARTBEAT.md + USER.md** — encode priorities and monitoring patterns; updates shift agent focus automatically

The real-world pattern from [24 Hours with OpenClaw (Substack)](https://sparkryai.substack.com/p/24-hours-with-openclaw-the-ai-setup): an agent independently detected a dental appointment email, created a calendar event with driving buffers, and sent confirmation — without being asked. This emerges from cron-scanned email + SOUL.md instructions to "default to action."

### Cron Job Configuration

```json
[
  {
    "name": "Morning briefing",
    "schedule": { "kind": "cron", "expr": "0 7 * * 1-5", "tz": "America/Los_Angeles" },
    "agentId": "chief-of-staff",
    "sessionTarget": "main",
    "wakeMode": "now",
    "payload": {
      "kind": "agentTurn",
      "message": "Good morning. Run the daily briefing: check email, calendar, HubSpot deals, Linear issues, and campaign metrics. Search shared memory for any overnight campaign completions or pending approvals. Summarize and recommend top 3 priorities for today.",
      "model": "sonnet",
      "thinking": "medium"
    },
    "delivery": {
      "mode": "announce",
      "channel": "slack",
      "to": "dm:SLACK_USER_ID"
    }
  },
  {
    "name": "Lead monitor",
    "schedule": { "kind": "every", "everyMs": 7200000 },
    "agentId": "chief-of-staff",
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "Check for new inbound leads in HubSpot and email. If any match our ICP, alert me with a brief summary and recommended next action. Store any significant findings in shared memory."
    },
    "delivery": {
      "mode": "announce",
      "channel": "slack",
      "to": "dm:SLACK_USER_ID",
      "bestEffort": true
    }
  },
  {
    "name": "Weekly strategy memo",
    "schedule": { "kind": "cron", "expr": "0 8 * * 1", "tz": "America/Los_Angeles" },
    "agentId": "chief-of-staff",
    "sessionTarget": "main",
    "payload": {
      "kind": "agentTurn",
      "message": "Prepare the weekly strategy memo: pipeline status from HubSpot, campaign performance from Google Analytics, engineering progress from Linear, ABM campaign results from Axon (check shared memory for recent campaign completions), and any competitive signals. Recommend priorities for the week and flag any risks.",
      "model": "opus",
      "thinking": "high"
    },
    "delivery": {
      "mode": "announce",
      "channel": "slack",
      "to": "channel:leadership"
    }
  },
  {
    "name": "Campaign performance check",
    "schedule": { "kind": "cron", "expr": "0 12 * * 1-5", "tz": "America/Los_Angeles" },
    "agentId": "chief-of-staff",
    "sessionTarget": "isolated",
    "payload": {
      "kind": "agentTurn",
      "message": "Pull today's campaign metrics from Google Analytics. Compare to yesterday and last week. Only alert if there are significant changes (>20% deviation) or if any campaign is underperforming targets."
    },
    "delivery": {
      "mode": "announce",
      "channel": "slack",
      "to": "dm:SLACK_USER_ID",
      "bestEffort": true
    }
  }
]
```

### Cron Limitations to Note

- **One concurrent run** — `maxConcurrentRuns: 1` prevents parallel cron jobs (increase if needed)
- **Isolated jobs have no conversation history** — use `main` session for tasks that need accumulated context
- **Exponential backoff on failure** — 30s, 1m, 5m, 15m, 60m
- **Gateway must be running** — cron runs inside the Gateway process

---

## Security Hardening

### Critical Context

- 42,900+ exposed OpenClaw control panels found across 82 countries ([Security Boulevard, Feb 2026](https://securityboulevard.com/2026/02/42900-openclaw-exposed-control-panels-and-why-you-should-care/))
- CVE-2026-25253 (CVSS 8.8) — remote code execution via stolen auth tokens ([Adversa AI, Feb 2026](https://adversa.ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/))
- 93.4% of exposed instances had authentication bypasses
- Our Tailscale-only access model sidesteps this entire attack surface

### Hardening Checklist

| Control | Configuration | Reference |
|---------|--------------|-----------|
| **Network binding** | `gateway.bind: "loopback"` (never `0.0.0.0`) | [OpenClaw Security Docs](https://docs.openclaw.ai/gateway/security) |
| **Gateway auth** | `auth.mode: "token"` with generated token | `openclaw doctor --generate-gateway-token` |
| **Webhook auth** | Separate `hooks.token` from gateway token | [OpenClaw Webhook Docs](https://docs.openclaw.ai/automation/webhook) |
| **Webhook scope** | `allowedAgentIds: ["chief-of-staff"]` | Restrict which agents webhooks can invoke |
| **Session key policy** | `allowedSessionKeyPrefixes: ["hook:workflow:"]` | Prevent session hijacking via webhooks |
| **File permissions** | `700` on dirs, `600` on files | `openclaw security audit --fix` |
| **mDNS discovery** | `discovery.mdns.mode: "off"` | Prevents network presence broadcast |
| **DM policy** | `dmPolicy: "allowlist"` or `"pairing"` | Requires explicit approval for contacts |
| **Group chat** | `requireMention: true` for all groups | Agent only responds when @mentioned |
| **Per-agent sandboxing** | `sandbox.mode: "all"` per agent | Container isolation per agent |
| **Tool restrictions** | `tools.deny` lists per agent | Principle of least privilege |
| **API key isolation** | Separate LiteLLM virtual key per agent | Budget caps prevent runaway costs |
| **Skill vetting** | Review all ClawHub skills before install | VirusTotal scanning enabled since Feb 2026 |
| **Agent-to-agent messaging** | Disabled by default | Only enable between specific pairs if needed |
| **Regular audits** | `openclaw security audit --deep` weekly | Automated posture check |
| **Mem0 API network policy** | Restrict to `marketing-agent` and `default` namespaces | No auth on Mem0 REST API |

### Tailscale Advantage

Since the dev-server is only accessible via Tailscale:
- OpenClaw's control panel is **never exposed** to the public internet
- CVE-2026-25253 requires network access to the gateway — impossible via our firewall
- SSH tunnel or Tailscale Serve provides authenticated HTTPS access from laptops
- OpenClaw webhook endpoint is only reachable from k8s services on the same machine (loopback)

**References:**
- [OpenClaw Security Docs](https://docs.openclaw.ai/gateway/security)
- [CSO Online: What CISOs Need to Know](https://www.csoonline.com/article/4129867/what-cisos-need-to-know-about-clawdbot-i-mean-moltbot-i-mean-openclaw.html)
- [Fortune: OpenClaw Security Risks](https://fortune.com/2026/02/12/openclaw-ai-agents-security-risks-beware/)
- [DigitalOcean Hardened 1-Click Deploy](https://www.digitalocean.com/blog/technical-dive-openclaw-hardened-1-click-app)
- [OpenClaw Security Hardening Guide (Medium)](https://alirezarezvani.medium.com/openclaw-security-my-complete-hardening-guide-for-vps-and-docker-deployments-14d754edfc1e)

---

## Implementation Phases

### Phase 1: Foundation — OpenClaw Install & Base Configuration (~2 hours)

**Goal:** OpenClaw running as a systemd service on dev-server, connected to LiteLLM.

**Tasks:**
- [ ] Install OpenClaw on dev-server (`npm install -g openclaw@latest`)
- [ ] Run `openclaw onboard --install-daemon` (installs systemd service)
- [ ] Generate gateway token (`openclaw doctor --generate-gateway-token`)
- [ ] Generate separate webhook token for `/hooks` endpoint
- [ ] Configure `openclaw.json` with LiteLLM provider and loopback binding
- [ ] Enable webhook endpoint with security constraints (`allowedAgentIds`, `allowedSessionKeyPrefixes`)
- [ ] Generate LiteLLM virtual keys for each agent + Mem0 API
- [ ] Run `openclaw security audit --fix`
- [ ] Verify: `openclaw doctor`, `openclaw status`

**Acceptance Criteria:**
- Gateway running as systemd service on dev-server
- LiteLLM connection verified (model list returned)
- Webhook endpoint responds to authenticated `POST /hooks/agent`
- Security audit passes with no critical findings
- Dashboard accessible via SSH tunnel

### Phase 2: Agent Identity & Skills (~3 hours)

**Goal:** Four agents with complete identity files, workspace skills, and MCP access.

**Tasks:**
- [ ] Write SOUL.md for each agent (chief-of-staff, marketing, content, coding)
- [ ] Write USER.md with founder context and business priorities
- [ ] Write HEARTBEAT.md with monitoring schedule
- [ ] Write AGENTS.md for coding agent (Claude Code delegation instructions)
- [ ] Write axon-api bridge skill for chief-of-staff and marketing workspaces
- [ ] Write shared-memory skill for chief-of-staff, marketing, and content workspaces
- [ ] Install community skills: `gog` (Google), `hubspot`, `coding-agent`
- [ ] Install `mcp-adapter` plugin with existing k8s MCP server endpoints
- [ ] Seed `memory.md` for each agent with initial context
- [ ] Test each skill manually (curl Axon API, curl Mem0 API)

**Acceptance Criteria:**
- Each agent has complete identity files
- Skills installed and verified (`openclaw plugins list`)
- MCP adapter discovers tools from Apollo, LinkedIn, GA servers
- Axon API bridge skill can hit `/v1/abm/campaigns` endpoints
- Shared memory skill can search and add memories via Mem0 REST API

### Phase 3: Shared Memory Bridge (~2 hours)

**Goal:** Mem0 REST API deployed in k8s, accessible from both Axon and OpenClaw.

**Tasks:**
- [ ] Deploy Mem0 REST server as k8s service (chart or manifest)
- [ ] Configure Mem0 to use existing Qdrant, Neo4j, and LiteLLM infrastructure
- [ ] Create k8s network policy restricting access to authorized namespaces
- [ ] Generate dedicated LiteLLM virtual key for Mem0 API (`mem0-api`)
- [ ] Verify Mem0 REST API responds: `GET /docs`, `POST /memories`, `GET /memories/search`
- [ ] Test from OpenClaw: shared-memory skill searches and adds memories
- [ ] Test from Axon: existing `MemoryManager` writes; OpenClaw skill reads
- [ ] Verify cross-system memory: Axon agent stores → OpenClaw agent retrieves

**Acceptance Criteria:**
- Mem0 REST API running at `mem0-api.mem0.svc.cluster.local:8000`
- OpenClaw agents can search memories by `user_id` and `query`
- OpenClaw agents can add memories that are retrievable by Axon agents
- ABM research results stored by Axon are searchable from OpenClaw
- Network policy prevents unauthorized access

### Phase 4: Bidirectional Webhook Bridge (~3 hours)

**Goal:** Temporal workflows can notify OpenClaw, and OpenClaw agents can trigger/approve workflows.

**Tasks:**
- [ ] Implement `notify_channel_activity` Temporal activity (POST to OpenClaw webhook)
- [ ] Add `notify_channel` and `notify_to` fields to `DAPERLInput`
- [ ] Integrate notification call at approval gate in `_handle_plan_review`
- [ ] Integrate notification call at workflow completion
- [ ] Implement `route_workflow_event` helper for dual-surface event routing
- [ ] Add `format_plan_for_chat` helper to format rich plans as readable chat messages
- [ ] Test end-to-end: start campaign via OpenClaw → workflow runs → approval request appears in Slack → approve via Slack → completion notification in Slack
- [ ] Add circuit breaker for OpenClaw webhook calls (fail gracefully if gateway is down)
- [ ] Add idempotency key header to prevent duplicate notifications on retry

**Acceptance Criteria:**
- Approval requests are delivered to Slack via OpenClaw webhook
- User can approve/reject campaigns from Slack conversation
- Workflow completion results are delivered to Slack
- Webhook failures don't break the Temporal workflow (graceful degradation)
- All webhook calls have idempotency keys and retry with exponential backoff

### Phase 5: Channel & Messaging Setup (~1 hour)

**Goal:** Slack connected, routing configured, DM and group policies set.

**Tasks:**
- [ ] Connect Slack workspace (create bot, configure channel)
- [ ] Configure routing bindings (DMs → chief-of-staff by default)
- [ ] Set DM policy to allowlist
- [ ] Set group `requireMention` to true
- [ ] Test sending a message and receiving a response
- [ ] Test approval flow via Slack (trigger campaign → approve → result)

**Acceptance Criteria:**
- Slack DM to bot gets routed to chief-of-staff agent
- Agent responds with context from SOUL.md identity
- @mention in channel triggers response
- Full approval flow works end-to-end via Slack

### Phase 6: Claude Code Integration (~30 min)

**Goal:** Coding agent delegates to Claude Code preserving all existing configuration.

**Tasks:**
- [ ] Install `coding-agent` skill
- [ ] Configure coding agent AGENTS.md with delegation instructions
- [ ] Test: ask coding agent to make a simple code change
- [ ] Verify Claude Code subprocess uses Max subscription (not API key)
- [ ] Verify Claude Code reads project CLAUDE.md and AGENTS.md rules

**Acceptance Criteria:**
- OpenClaw coding agent spawns Claude Code successfully
- Claude Code follows Graphite workflow, GPG signs commits
- Feature-dev and frontend-design skills accessible via delegation
- Max subscription billed (not API key)

### Phase 7: Google Workspace & HubSpot (~1 hour)

**Goal:** Chief-of-staff has access to email, calendar, and CRM.

**Tasks:**
- [ ] Set up Google OAuth for `gog` skill (Gmail, Calendar, Drive)
- [ ] Configure HubSpot API key/OAuth for HubSpot skill + MCP
- [ ] Test Gmail reading and search
- [ ] Test Calendar event creation
- [ ] Test HubSpot deal/contact queries
- [ ] Enable LinkedIn MCP URL in k8s config (currently disabled)
- [ ] Enable Google Analytics MCP URL in k8s config (currently disabled)

**Acceptance Criteria:**
- Chief-of-staff can read email, check calendar, query HubSpot deals
- Marketing agent can query GA reports, LinkedIn ad stats, Apollo enrichment
- All data flows through existing k8s infrastructure

### Phase 8: Proactive Behavior & Cron (~1 hour)

**Goal:** Scheduled agent runs with cross-system context.

**Tasks:**
- [ ] Configure morning briefing cron job (7am weekdays) — includes Mem0 search for overnight events
- [ ] Configure lead monitor cron job (every 2 hours)
- [ ] Configure weekly strategy memo (Monday 8am) — includes Axon campaign results
- [ ] Configure campaign performance check (noon weekdays)
- [ ] Test each cron job manually (`openclaw cron run <jobId>`)
- [ ] Verify Slack delivery for all cron outputs
- [ ] Verify shared memory integration (cron jobs reference cross-system context)

**Acceptance Criteria:**
- Morning briefings are actionable and include Axon campaign status
- Lead monitor correctly identifies ICP-matching leads
- Weekly memo includes pipeline, campaign, engineering, and ABM data
- All outputs delivered to correct Slack channels
- Shared memory provides cross-system context enrichment

### Phase 9: Validation, Tuning & Hardening (~ongoing, 2 weeks)

**Goal:** Production-quality integration with verified end-to-end flows.

**Tasks:**
- [ ] Run for 2 weeks with all cron jobs active
- [ ] Tune SOUL.md/USER.md based on quality of suggestions
- [ ] Tune axon-api bridge skill based on actual approval flow usage
- [ ] Adjust cron schedules based on actual usage patterns
- [ ] Review LiteLLM cost dashboard — adjust virtual key budgets
- [ ] Verify shared memory quality (are memories useful? too noisy?)
- [ ] Review Langfuse traces — verify cost attribution tags work correctly
- [ ] Run `openclaw security audit --deep`
- [ ] Verify webhook circuit breaker behavior under failure conditions
- [ ] Document any issues and resolutions

**Acceptance Criteria:**
- Morning briefings are actionable and accurate
- Agent proactively surfaces relevant insights from shared memory
- Approval flow via Slack works reliably (>95% success rate)
- No security audit findings
- Monthly cost within acceptable range
- Cross-system memory is coherent and useful

---

## Gaps & Open Questions

### Must Resolve Before Implementation

| Gap | Impact | Effort | Notes |
|-----|--------|--------|-------|
| **Enable LinkedIn MCP URL** | Marketing agent can't manage LinkedIn ads | 5 min | Set `LINKEDIN_MCP_URL` env var in `values-local.yaml` |
| **Enable Google Analytics MCP URL** | Marketing agent can't query GA | 5 min | Set `GOOGLE_ANALYTICS_MCP_URL` env var in `values-local.yaml` |
| **HubSpot API credentials** | Chief-of-staff can't query CRM | 30 min | Need HubSpot private app or OAuth setup |
| **Google OAuth for gog** | No email/calendar/drive access | 30 min | Need Google Cloud Console OAuth client |
| **Mem0 REST API deployment** | No shared memory bridge | 1-2 hours | Deploy container in k8s, configure network policy |
| **`notify_channel_activity` implementation** | No webhook bridge | 2-3 hours | Temporal activity + DAPERL integration |

### Architecture Decisions to Validate

| Decision | Options | Recommendation | Reasoning |
|----------|---------|---------------|-----------|
| **Webhook vs polling for approval delivery** | Webhook (push) vs cron poll (pull) | Webhook (push) | Lower latency, no wasted cycles; OpenClaw's `/hooks/agent` is purpose-built for this ([OpenClaw Webhook Docs](https://docs.openclaw.ai/automation/webhook)) |
| **Mem0 access pattern** | REST API vs direct Qdrant/Neo4j queries | REST API | Mem0 handles embedding, deduplication, and graph extraction automatically; direct queries bypass these ([Mem0 REST API Docs](https://docs.mem0.ai/open-source/features/rest-api)) |
| **Session key for webhook-triggered conversations** | Shared session vs isolated | Isolated (`hook:workflow:{id}`) | Prevents webhook payloads from polluting the main conversation session; each workflow gets its own context window ([OpenClaw Webhook Docs](https://docs.openclaw.ai/automation/webhook)) |
| **Event routing strategy** | All events to all surfaces vs selective | Selective (matrix-based) | Only high-priority events (approval, completion, critical failure) warrant messaging delivery; avoids notification fatigue |

### Future Enhancements (Post-Convergence)

| Enhancement | Impact | Effort | Notes |
|-------------|--------|--------|-------|
| **Google Search Console MCP server** | Search performance analysis | 1-2 days | Same OAuth pattern as GA MCP |
| **Google Ads MCP server** | Google Ads campaign management | 2-3 days | Needs Google Ads developer token |
| **WhatsApp channel** | Mobile approval flow | 1-2 hours | OpenClaw built-in; needs phone number |
| **Landing page deployment skill** | Content agent can generate but not deploy | 1-2 days | Push HTML to git/Vercel/static host |
| **Email sequence integration** | Automated outreach sequences | 1-2 days | Depends on ESP (Apollo sequences, SendGrid) |
| **NixOS module for OpenClaw** | Declarative config like k3s/Tailscale | 1 day | Would make config reproducible via nix |
| **A2A protocol support** | External agent interop | Deferred | See [10-multi-agent-coordination.md](./daperl-agent-pattern/10-multi-agent-coordination.md) |

### Open Questions

1. **Anthropic ToS for Max subscription + Claude Code subprocess**: The coding-agent skill spawning Claude Code should be fine (it IS Anthropic's tool), but should verify explicitly with Anthropic support.

2. **OpenClaw update cadence**: Given CVE-2026-25253, how quickly do we want to track OpenClaw releases? Weekly? Pin to specific versions?

3. **Mem0 memory quality**: How do we prevent memory noise? Strategy: aggressive `agent_id` scoping + periodic memory review via cron job that summarizes and prunes low-value memories.

4. **Cost monitoring threshold**: What monthly LLM spend is acceptable across all OpenClaw agents? Need to set LiteLLM virtual key budgets accordingly.

5. **Webhook reliability SLA**: What's acceptable for the Axon→OpenClaw webhook? If OpenClaw is down, Temporal retries 3 times then fails gracefully. User can still approve via web UI. Is this sufficient?

---

## References & Sources

### OpenClaw Documentation
- [OpenClaw Official Install Docs](https://docs.openclaw.ai/install)
- [OpenClaw Multi-Agent Routing](https://docs.openclaw.ai/concepts/multi-agent)
- [OpenClaw Cron Jobs](https://docs.openclaw.ai/automation/cron-jobs)
- [OpenClaw Webhook API](https://docs.openclaw.ai/automation/webhook)
- [OpenClaw Security Docs](https://docs.openclaw.ai/gateway/security)
- [OpenClaw LiteLLM Provider](https://docs.openclaw.ai/providers/litellm)
- [OpenClaw Skills Documentation](https://docs.openclaw.ai/tools/skills)
- [OpenClaw FAQ](https://docs.openclaw.ai/help/faq)
- [OpenClaw Default AGENTS.md Reference](https://docs.openclaw.ai/reference/AGENTS.default)
- [OpenClaw Configuration Guide (Molt Founders)](https://moltfounders.com/openclaw-configuration)
- [OpenClaw Architecture Overview (Substack)](https://ppaolo.substack.com/p/openclaw-system-architecture-overview)
- [OpenClaw Custom API Integration Guide (LumaDock)](https://lumadock.com/tutorials/openclaw-custom-api-integration-guide)

### Skills & Integrations
- [steipete/coding-agent Skill (Official)](https://github.com/openclaw/skills/blob/main/skills/steipete/coding-agent/SKILL.md)
- [openclaw-claude-code-skill MCP Bridge](https://github.com/Enderfga/openclaw-claude-code-skill)
- [OpenClaw MCP Adapter Plugin](https://github.com/androidStern-personal/openclaw-mcp-adapter)
- [HubSpot Skill (ClawHub)](https://github.com/openclaw/skills/blob/main/skills/kwall1/hubspot/SKILL.md)
- [HubSpot MCP Server (Official)](https://developers.hubspot.com/mcp)
- [Google Workspace gog Skill](https://drlee.io/give-openclaw-moltbot-clawdbot-a-google-brain-how-to-connect-13-free-google-services-to-openclaw-52cdf13954e2)
- [ClawHub Skills Marketplace](https://github.com/openclaw/clawhub)
- [SOUL.md Framework](https://github.com/aaronjmars/soul.md)

### Protocol Standards
- [AG-UI Protocol Overview](https://docs.ag-ui.com/)
- [AG-UI: Agent-User Interaction Protocol (CopilotKit)](https://webflow.copilotkit.ai/blog/introducing-ag-ui-the-protocol-where-agents-meet-users)
- [AG-UI Protocol Multi-Channel Architecture (DataCamp)](https://www.datacamp.com/tutorial/ag-ui)
- [A2A, MCP, AG-UI Protocol Stack (Medium)](https://medium.com/@visrow/a2a-mcp-ag-ui-a2ui-the-essential-2026-ai-agent-protocol-stack-ee0e65a672ef)
- [Top 5 Open Protocols for Multi-Agent Systems (OneReach)](https://onereach.ai/blog/power-of-multi-agent-ai-open-protocols/)

### Temporal & Workflow Patterns
- [Temporal Workflow Orchestration (James Carr)](https://james-carr.org/posts/2026-01-29-temporal-workflow-orchestration/)
- [Temporal Slack Alert Workflow (GitHub)](https://github.com/rachfop/slack-alert-workflow)
- [Temporal Python SDK](https://github.com/temporalio/sdk-python)
- [Slack Approval Workflows Tutorial](https://api.slack.com/tutorials/tracks/building-approval-workflows)

### Memory & RAG
- [Mem0 REST API Docs](https://docs.mem0.ai/open-source/features/rest-api)
- [Mem0 REST API Reference (DeepWiki)](https://deepwiki.com/mem0ai/mem0/7.2-rest-api-reference)
- [Mem0 Graph Memory for AI Agents (2026)](https://mem0.ai/blog/graph-memory-solutions-ai-agents)
- [AWS: Persistent Memory with Mem0](https://aws.amazon.com/blogs/database/build-persistent-memory-for-agentic-ai-applications-with-mem0-open-source-amazon-elasticache-for-valkey-and-amazon-neptune-analytics/)
- [OpenMemory MCP Server Setup](https://apidog.com/blog/openmemory-mcp-server/)

### Webhook Best Practices
- [Webhooks for Custom Integrations (NotiGrid)](https://notigrid.com/blog/webhooks-for-custom-integrations)
- [Webhook Triggers for Event-Driven APIs (DreamFactory)](https://blog.dreamfactory.com/webhook-triggers-for-event-driven-apis)
- [Understanding Webhooks (Theneo)](https://www.theneo.io/blog/understanding-webhooks-what-they-are-and-how-to-use-them)

### Security
- [42,900 Exposed Control Panels (Security Boulevard)](https://securityboulevard.com/2026/02/42900-openclaw-exposed-control-panels-and-why-you-should-care/)
- [CVE-2026-25253 & Hardening (Adversa AI)](https://adversa.ai/blog/openclaw-security-101-vulnerabilities-hardening-2026/)
- [CSO Online: What CISOs Need to Know](https://www.csoonline.com/article/4129867/what-cisos-need-to-know-about-clawdbot-i-mean-moltbot-i-mean-openclaw.html)
- [Fortune: OpenClaw Security Risks](https://fortune.com/2026/02/12/openclaw-ai-agents-security-risks-beware/)
- [DigitalOcean Hardened 1-Click Deploy](https://www.digitalocean.com/blog/technical-dive-openclaw-hardened-1-click-app)
- [OpenClaw Security Hardening Guide (Medium)](https://alirezarezvani.medium.com/openclaw-security-my-complete-hardening-guide-for-vps-and-docker-deployments-14d754edfc1e)

### LiteLLM & Cost Management
- [LiteLLM Virtual Keys](https://docs.litellm.ai/docs/proxy/virtual_keys)
- [LiteLLM Budgets & Rate Limits](https://docs.litellm.ai/docs/proxy/users)
- [OpenClaw + LiteLLM Setup (Medium)](https://gdsks.medium.com/how-to-use-openclaw-with-azure-openai-using-litellm-proxy-7b7d05cddf13)

### Background & Context
- [OpenClaw Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)
- [CNBC: From Clawdbot to OpenClaw](https://www.cnbc.com/2026/02/02/openclaw-open-source-ai-agent-rise-controversy-clawdbot-moltbot-moltbook.html)
- [Creati.ai: OpenClaw 145k+ Stars](https://creati.ai/ai-news/2026-02-11/openclaw-open-source-ai-agent-viral-145k-github-stars/)
- [OpenClaw vs Claude Code Comparison](https://www.getaiperks.com/en/blogs/10-openclaw-vs-claude-code)
- [OpenClaw Identity Architecture (MMNTM)](https://www.mmntm.net/articles/openclaw-identity-architecture)
- [24 Hours as Chief of Staff (Substack)](https://sparkryai.substack.com/p/24-hours-with-openclaw-the-ai-setup)
- [OpenClaw Marketing Playbook 2026](https://marketingagent.blog/2026/01/31/how-to-use-openclaw-ai-for-marketing-in-2026-a-complete-playbook/)
- [OpenClaw for Marketing Agencies (Serif)](https://www.serif.ai/openclaw/marketing-agencies)
- [OpenClaw Proactive Cron Guide](https://zenvanriel.nl/ai-engineer-blog/openclaw-cron-jobs-proactive-ai-guide/)
- [Anthropic Subscription Policy Discussion](https://www.answeroverflow.com/m/1467147858607341712)

---

*Last updated: 2026-02-13*
